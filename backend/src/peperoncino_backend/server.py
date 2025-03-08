from pathlib import Path

import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse

from .lib import Plotter

app = FastAPI()

plotter = Plotter()

files_path = "files/"
Path(files_path).mkdir(parents=True, exist_ok=True)
# initialize 'jobs' list with the files in the 'files' directory
jobs = [f"{f}" for f in Path(files_path).iterdir() if f.is_file()]


@app.post("/start")
async def start():
    # Implement your start logic here
    return JSONResponse(content={"message": "Started"}, status_code=200)


@app.post("/pause")
async def pause():
    # Implement your pause logic here
    return JSONResponse(content={"message": "Paused"}, status_code=200)


@app.post("/reset")
async def reset():
    # Implement your reset logic here
    return JSONResponse(content={"message": "Reset"}, status_code=200)


@app.post("/queue")
async def append_file(file: UploadFile = File(...)):
    # If the file is a raster image, convert it to a gcode file
    gcode_file = []
    if file.content_type in ["image/png", "image/jpeg", "image/bmp"]:
        pass

    if file.content_type == "image/svg+xml":
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


@app.get("/port")
async def get_port():
    return JSONResponse(content={"port": plotter.port}, status_code=200)


@app.post("/port")
async def set_port(port: str):
    plotter.port = port
    return JSONResponse(content={"message": f"Port set to {port}"}, status_code=200)


@app.get("/queue")
async def get_jobs():
    # Implement your get jobs logic here
    return JSONResponse(content={"jobs": []}, status_code=200)


def main():
    uvicorn.run(
        "peperoncino_backend.server:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True,
        workers=2,
    )
