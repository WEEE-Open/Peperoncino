import logging
import os
from pathlib import Path
import re

import vtracer
import uvicorn
from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .gcode import convert_svg_to_gcode, convert_gcode_to_jpg

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
default_files = "default_files/"
Path(files_path).mkdir(parents=True, exist_ok=True)
# initialize 'jobs' list with the files in the 'files' directory
default_jobs = [f"{f.stem}" for f in Path(default_files).iterdir() if f.is_file()]
jobs = [f"{f.stem}" for f in Path(files_path).iterdir() if f.is_file()]
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
async def append_file(
    request: Request,
    file: UploadFile = File(...)
):
    form = await request.form()
    name_match = re.match(r"(.*?)(?:\..*)?$", file.filename)
    name = name_match.group(1) if name_match else file.filename
    res = None

    # Get parameters from form data with defaults
    filter_speckle = int(form.get("filter_speckle", 4))
    curve_fitting = form.get("curve_fitting", "polygon")
    corner_threshold = int(form.get("corner_threshold", 60))
    segment_length = int(form.get("segment_length", 4.0))
    splice_threshold = int(form.get("splice_threshold", 45))
    print(filter_speckle, curve_fitting, corner_threshold, segment_length, splice_threshold)
    if name in jobs:
        suffix_match = re.match(r"(.*?)__(\d+)$", name)
        if suffix_match:
            base_name, num = suffix_match.groups()
            name = f"{base_name}__{int(num) + 1}"
        else:
            name = f"{name}__1"
    # Append the path to the list jobs
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
            vtracer.convert_image_to_svg_py(
                Path(files_path, file.filename).resolve().as_posix(),
                Path(files_path, name + ".svg").resolve().as_posix(),
                colormode='binary',        # ["color"] or "binary"
                hierarchical='stacked',    # ["stacked"] or "cutout"
                mode=curve_fitting,        # ["spline"] "polygon", or "none"
                filter_speckle=filter_speckle,
                corner_threshold=corner_threshold,
                length_threshold=segment_length,
                splice_threshold=splice_threshold
            )
        case _:
            jobs.remove(name)
            res = JSONResponse(
                content={
                    "filename": file.filename,
                    "message": "Unsupported file format",
                },
                status_code=405,
            )

    # Delete the temporary file
    if Path(files_path, file.filename).exists():
        Path(files_path, file.filename).unlink()

    return res or JSONResponse(
        content={"filename": file.filename, "message": "File received"}, status_code=200
    )


@app.delete("/queue/{job}")
async def delete_job(job: str):
    if job in jobs:
        jobs.remove(job)
        Path(files_path, job + ".gcode").unlink()
        return JSONResponse(content={"message": "Job deleted"}, status_code=200)
    elif job in default_jobs:
        return JSONResponse(
            content={"message": "Default job can't be deleted"}, status_code=404
        )
    return JSONResponse(content={"message": "Job not found"}, status_code=404)


@app.post("/queue/{job}")
async def send_job(job: str):
    if job in jobs:
        plotter.send(Path(files_path, job + ".gcode"))
        return JSONResponse(content={"message": "Job sent"}, status_code=200)
    elif job in default_jobs:
        plotter.send(Path(default_files, job + ".gcode"))
        return JSONResponse(content={"message": "Default job sent"}, status_code=200)
    return JSONResponse(content={"message": "Job not found"}, status_code=404)

@app.get("/queue/{job}/preview")
async def preview_job(job: str):
    if job in jobs:
        preview_path = Path(files_path, job + ".jpg")
    elif job in default_jobs:
        preview_path = Path(default_files, job + ".jpg")
    else:
        return JSONResponse(content={"message": "Job not found"}, status_code=404)

    if not preview_path.exists():
        convert_gcode_to_jpg(Path(files_path, job + ".gcode"), preview_path)

    return JSONResponse(
        content={"preview": base64.b64encode(preview_path.read_bytes()).decode("utf-8")},
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
    data = await request.json()
    speed = data.get("speed")
    if speed:
        plotter.speed = speed
        return JSONResponse(
            content={"message": f"Speed set to {speed}"}, status_code=200
        )
    return JSONResponse(content={"message": "Speed not provided"}, status_code=400)


@app.get("/state")
async def get_state():
    plotter.check_confirmation()
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
