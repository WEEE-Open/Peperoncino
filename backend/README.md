# Peperoncino Backend API Documentation

This document provides an overview of the API endpoints available in the Peperoncino backend server.

## Endpoints

### 1. Start

- **URL:** `/start`
- **Method:** `POST`
- **Description:** Starts the process.
- **Response:**
  - `200 OK`: `{ "message": "Started" }`

### 2. Pause

- **URL:** `/pause`
- **Method:** `POST`
- **Description:** Pauses the process.
- **Response:**
  - `200 OK`: `{ "message": "Paused" }`

### 3. Reset

- **URL:** `/reset`
- **Method:** `POST`
- **Description:** Resets the process.
- **Response:**
  - `200 OK`: `{ "message": "Reset" }`

### 4. Append File to Queue

- **URL:** `/queue`
- **Method:** `POST`
- **Description:** Uploads a file and appends it to the processing queue.
- **Request:**
  - `file`: The file to be uploaded (supports `image/png`, `image/jpeg`, `image/bmp`, `image/svg+xml`, `text/plain`).
- **Response:**
  - `200 OK`: `{ "filename": "<uploaded-filename>", "message": "File received" }`

### 5. Get Available Ports

- **URL:** `/ports`
- **Method:** `GET`
- **Description:** Retrieves the list of available ports.
- **Response:**
  - `200 OK`: `{ "ports": ["port1", "port2"] }`

### 6. Get Selected Port

- **URL:** `/ports/selected`
- **Method:** `GET`
- **Description:** Retrieves the current port used by the plotter.
- **Response:**
  - `200 OK`: `{ "port": "<current-port>" }`

### 7. Set Port

- **URL:** `/ports/selected`
- **Method:** `POST`
- **Description:** Sets the port for the plotter.
- **Request:**
  - `port`: The port to be set.
- **Response:**
  - `200 OK`: `{ "message": "Port set to <port>" }`

### 8. Get Queue

- **URL:** `/queue`
- **Method:** `GET`
- **Description:** Retrieves the list of jobs in the queue.
- **Response:**
  - `200 OK`: `{ "jobs": ["file1", "file2"] }`

## Running the Server

In a virtual environment install the package:

```sh
pip install .[server]
```

and run it with

```sh
python server
```

> The port is controlled by the `PEPERONCINO_BACKEND_PORT` environment variable

### Development

For development, install the project with poetry and run the command:

```bash
DEBUG=1 poetry run uvicorn peperoncino_backend.server:app --port 5000 --reload --workers=2
```

FastAPI automatically builds all relevant OpenAPI stuff and provides a way to test the endpoints at `/docs`
