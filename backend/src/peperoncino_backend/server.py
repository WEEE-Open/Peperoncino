from json import JSONDecodeError
import logging
import os
from pathlib import Path
import re

import cv2
import vtracer
import hatched
import uvicorn
from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .gcode import convert_svg_to_gcode, convert_gcode_to_image

from . import lib
import base64

log = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

plotter = lib.Plotter()

files_path = "files/"
default_files_path = "default_files/"
previews_path = "previews/"
Path(files_path).mkdir(parents=True, exist_ok=True)
Path(default_files_path).mkdir(parents=True, exist_ok=True)
Path(previews_path).mkdir(parents=True, exist_ok=True)

# initialize 'jobs' list with the files in the 'files' directory
default_jobs = [
    f"{f.stem}" for f in Path(default_files_path).glob("*.gcode") if f.is_file()
]
jobs = [f"{f.stem}" for f in Path(files_path).glob("*.gcode") if f.is_file()]

log.info(f"Default jobs: {default_jobs}")
log.info(f"Jobs: {jobs}")


@app.get("/")
async def root():
    return JSONResponse(content={"message": "ok"}, status_code=200)


@app.post("/start")
async def start():
    plotter.start()
    return JSONResponse(content={"message": "Started"}, status_code=200)


@app.post("/pause")
async def pause():
    plotter.pause()
    return JSONResponse(content={"message": "Paused"}, status_code=200)


@app.post("/reset")
async def reset():
    plotter.reset()
    return JSONResponse(content={"message": "Reset"}, status_code=200)


@app.get("/queue")
async def get_jobs():
    return JSONResponse(
        content={"jobs": jobs, "default_jobs": default_jobs}, status_code=200
    )


@app.post("/queue")
async def append_file(request: Request, file: UploadFile = File(...)):
    form = await request.form()
    name_match = re.match(r"(.*?)(?:\..*)?$", file.filename)
    name = name_match.group(1) if name_match else file.filename
    res = None

    tmp = form.get("tmp")
    vectorialization_method = form.get("vectorialization_method", "trace")
    # Trace
    filter_speckle = int(form.get("filter_speckle", 4))
    curve_fitting = form.get("curve_fitting", "polygon")
    corner_threshold = int(form.get("corner_threshold", 60))
    segment_length = int(form.get("segment_length", 4.0))
    splice_threshold = int(form.get("splice_threshold", 45))
    # Hatch
    interpolation = form.get("interpolation", "linear")
    match interpolation:
        case "linear":
            interpolation = cv2.INTER_LINEAR
        case "nearest":
            interpolation = cv2.INTER_NEAREST
        case "cubic":
            interpolation = cv2.INTER_CUBIC
        case _:
            interpolation = cv2.INTER_LINEAR

    blur_radius = int(form.get("blur_radius", 0))
    hatch_pitch = float(form.get("hatch_pitch", 1))
    hatch_angle = float(form.get("hatch_angle", 0))
    levels = int(form.get("levels", 1))
    invert = form.get("invert", "false").lower() == "true"
    circular = form.get("circular", "false").lower() == "true"
    center_x = float(form.get("center_x", 0)) if circular else None
    center_y = float(form.get("center_y", 0)) if circular else None

    while name in jobs:
        if file.content_type in [
            "image/png",
            "image/jpeg",
            "image/jpg",
            "image/bmp",
            "image/gif",
            "image/webp",
            "application/pdf",
        ]:
            return JSONResponse(
                content={
                    "filename": file.filename,
                    "message": "File already exists",
                },
                status_code=405,
            )

        suffix_match = re.match(r"(.*?)__(\d+)$", name)
        if suffix_match:
            base_name, num = suffix_match.groups()
            name = f"{base_name}__{int(num) + 1}"
        else:
            name = f"{name}__1"

    # Append the path to the list jobs
    if not tmp:
        jobs.append(name)

    # Create a temporary file to store the uploaded file
    with open(Path(files_path, file.filename), "wb") as f:
        f.write(file.file.read())

    output_path = Path(files_path, name + ".gcode")
    # If the file is a raster image, convert it to a gcode file
    match file.content_type:
        case "text/plain" | "text/x.gcode":
            Path(files_path, file.filename).replace(output_path)
        case "image/svg+xml":
            convert_svg_to_gcode(Path(files_path, file.filename), output_path)
        case (
            "image/png"
            | "image/jpeg"
            | "image/jpg"
            | "image/bmp"
            | "image/gif"
            | "image/webp"
            | "application/pdf"
        ):
            if vectorialization_method == "trace":
                vtracer.convert_image_to_svg_py(
                    Path(files_path, file.filename).resolve().as_posix(),
                    Path(files_path, name + ".svg").resolve().as_posix(),
                    colormode="binary",  # ["color"] or "binary"
                    mode=curve_fitting,  # ["spline"] "polygon", or "none"
                    filter_speckle=filter_speckle,
                    corner_threshold=corner_threshold,
                    length_threshold=segment_length,
                    splice_threshold=splice_threshold,
                )
            elif vectorialization_method == "hatch":
                # print(blur_radius)
                hatched.hatch(
                    Path(files_path, file.filename).resolve().as_posix(),
                    hatch_pitch=hatch_pitch,
                    # levels=levels,
                    blur_radius=blur_radius,
                    interpolation=interpolation,
                    h_mirror=False,
                    invert=invert,
                    circular=circular,
                    center=(center_x, center_y),
                    hatch_angle=hatch_angle,
                    show_plot=False,
                    save_svg=True,
                )

            try:
                convert_svg_to_gcode(Path(files_path, name + ".svg"), output_path)
            except TypeError:
                pass
            finally:
                Path(files_path, name + ".svg").unlink(missing_ok=True)
        case _:
            if not tmp:
                jobs.remove(name)
            res = JSONResponse(
                content={
                    "filename": file.filename,
                    "message": "Unsupported file format",
                },
                status_code=405,
            )

    # Delete the temporary file
    Path(files_path, file.filename).unlink(missing_ok=True)

    return res or JSONResponse(
        content={"filename": file.filename, "message": "File received"}, status_code=200
    )


@app.delete("/queue/{job}")
async def delete_job(job: str):
    if job in jobs:
        jobs.remove(job)
        Path(files_path, job + ".gcode").unlink(missing_ok=True)
        Path(previews_path, job + ".webp").unlink(missing_ok=True)
        return JSONResponse(content={"message": "Job deleted"}, status_code=200)
    elif job in default_jobs:
        return JSONResponse(
            content={"message": "Default job can't be deleted"}, status_code=404
        )
    return JSONResponse(content={"message": "Job not found"}, status_code=404)


@app.post("/queue/{job}")
async def send_job(job: str):
    file_path = None

    if job in jobs:
        file_path = Path(files_path, job + ".gcode")
    elif job in default_jobs:
        file_path = Path(default_files_path, job + ".gcode")
    else:
        return JSONResponse(content={"message": "Job not found"}, status_code=404)

    if not file_path.exists():
        if job in jobs:
            jobs.remove(job)
        elif job in default_jobs:
            default_jobs.remove(job)
        Path(previews_path, job + ".webp").unlink(missing_ok=True)
        return JSONResponse(
            content={"message": "Gcode file not found"}, status_code=404
        )

    plotter.send(file_path)
    message = "Default job sent" if job in default_jobs else "Job sent"
    return JSONResponse(content={"message": message}, status_code=200)


@app.get("/queue/{job}/preview")
async def preview_job(job: str):
    # if job not in jobs + default_jobs:
    #     return JSONResponse(content={"message": "Job not found"}, status_code=404)
    preview_path = Path(previews_path, job + ".webp")
    if not preview_path.exists() or (job not in jobs and job not in default_jobs):
        try:
            convert_gcode_to_image(
                Path(files_path, job + ".gcode"), preview_path, format="webp"
            )
        except FileNotFoundError:
            return JSONResponse(
                content={"message": "Gcode file not found"}, status_code=404
            )

    return JSONResponse(
        content={
            "preview": base64.b64encode(preview_path.read_bytes()).decode("utf-8")
        },
        status_code=200,
    )


@app.get("/ports")
async def get_available_ports():
    return JSONResponse(content=lib.get_available_ports(), status_code=200)


@app.get("/ports/selected")
async def get_port():
    return JSONResponse(content={"port": plotter.port}, status_code=200)


@app.post("/ports/selected")
async def set_port(request: Request):
    data = await request.json()
    port = data.get("port")
    if port:
        plotter.port = port
        return JSONResponse(content={"message": f"Port set to {port}"}, status_code=200)
    return JSONResponse(content={"message": "Port not provided"}, status_code=400)


@app.get("/speed")
async def get_speed():
    return JSONResponse(content={"speed": plotter.speed}, status_code=200)


@app.post("/speed")
async def set_speed(request: Request):
    try:
        data = await request.json()
    except JSONDecodeError:
        return JSONResponse(content={"message": "Speed not provided"}, status_code=400)
    speed = data.get("speed")
    if speed:
        plotter.speed = speed
        return JSONResponse(
            content={"message": f"Speed set to {speed}"}, status_code=200
        )
    return JSONResponse(content={"message": "Speed not provided"}, status_code=400)


@app.get("/state")
async def get_state():
    plotter.check_running()
    uploaded, running = plotter.state
    data = {
        "uploaded": uploaded.stem if uploaded else None,
        "running": running,
    }
    return JSONResponse(content=data, status_code=200)


def main():
    uvicorn.run(
        "peperoncino_backend.server:app",
        host="0.0.0.0",
        port=int(os.getenv("PEPERONCINO_BACKEND_PORT", 3000)),
        log_level="info",
        workers=2,
    )
