import logging
import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI, File, Request, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .gcode import convert_svg_to_gcode

from . import lib

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
Path(files_path).mkdir(parents=True, exist_ok=True)
# initialize 'jobs' list with the files in the 'files' directory
default_jobs = [f"{f.stem}" for f in Path(files_path).iterdir() if f.is_file()]
jobs = default_jobs.copy()


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
    return JSONResponse(content={"jobs": jobs}, status_code=200)


@app.post("/queue")
async def append_file(file: UploadFile = File(...)):
    name = "".join(file.filename.split(".")[:-1])
    # Append the path to the list jobs
    jobs.append(name)

    # Create a temporary file to store the uploaded file
    with open(Path(files_path, file.filename), "wb") as f:
        f.write(file.file.read())

    # If the file is a raster image, convert it to a gcode file
    match file.content_type:
        case "text/plain":
            gcode_file = file.file.readlines()
            with open(Path(files_path, name + ".gcode"), "w") as f:
                f.writelines(gcode_file)
        case "image/svg+xml":
            convert_svg_to_gcode(Path(files_path, file.filename), name + ".gcode")
        case (
            "image/png"
            | "image/jpeg"
            | "image/jpg"
            | "image/bmp"
            | "image/gif"
            | "image/webp"
            | "application/pdf"
        ):
            log.warning("Raster image to gcode conversion is yet to be implemented.")
            return JSONResponse(
                content={
                    "filename": file.filename,
                    "message": "Raster image to gcode conversion is yet to be implemented.",
                },
                status_code=405,
            )
        case _:
            return JSONResponse(
                content={
                    "filename": file.filename,
                    "message": "Unsupported file format",
                },
                status_code=405,
            )

    # Delete the temporary file
    if Path(files_path, file.filename).exists():
        Path(files_path, file.filename).unlink()

    return JSONResponse(
        content={"filename": file.filename, "message": "File received"}, status_code=200
    )


@app.delete("/queue/{job}")
async def delete_job(job: str):
    if job in jobs:
        jobs.remove(job)
        if job not in default_jobs:
            Path(files_path, job + ".gcode").unlink()
        return JSONResponse(content={"message": "Job deleted"}, status_code=200)
    return JSONResponse(content={"message": "Job not found"}, status_code=404)


@app.post("/queue/{job}")
async def send_job(job: str):
    if job in jobs:
        plotter.send(Path(files_path, job + ".gcode"))
        return JSONResponse(content={"message": "Job sent"}, status_code=200)
    return JSONResponse(content={"message": "Job not found"}, status_code=404)


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
