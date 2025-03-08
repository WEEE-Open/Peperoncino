import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI, APIRouter, File, UploadFile
from fastapi.responses import JSONResponse

from . import lib

app = FastAPI()

plotter = lib.Plotter()

files_path = "files/"
Path(files_path).mkdir(parents=True, exist_ok=True)
# initialize 'jobs' list with the files in the 'files' directory
jobs = [f"{f}" for f in Path(files_path).iterdir() if f.is_file()]


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
    # If the file is a raster image, convert it to a gcode file
    gcode_file = []
    if file.content_type in ["image/png", "image/jpeg", "image/bmp"]:
        pass

    if file.content_type == "image/svg+xml":
        # use vpype to convert the svg to gcode
        pass

    if file.content_type == "text/plain":
        gcode_file = file.file.readlines()

    # Save the file in the "files" directory
    with open(Path(files_path, file.filename.split(".")[:-1] + ".gcode"), "wb") as f:
        f.writelines(gcode_file)

    # Append the path to the list jobs
    jobs.append(f"files/{file.filename}")

    return JSONResponse(
        content={"filename": file.filename, "message": "File received"}, status_code=200
    )

@app.get("/ports")
async def get_available_ports():
    return JSONResponse(content=lib.get_available_ports(), status_code=200)

@app.get("/ports/selected")
async def get_port():
    return JSONResponse(content={"port": plotter.port}, status_code=200)


@app.post("/ports/selected")
async def set_port(port: str):
    plotter.port = port
    return JSONResponse(content={"message": f"Port set to {port}"}, status_code=200)

def main():
    uvicorn.run(
        "peperoncino_backend.server:app",
        host="0.0.0.0",
        port=int(os.getenv("PEPERONCINO_BACKEND_PORT", 3000)),
        log_level="info",
        workers=2,
    )
