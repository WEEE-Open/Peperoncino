# P.E.P.E.R.O.N.C.I.N.O

Plotter Estremamente Preciso E Reattivo Ottimizzato Nel Controllo Istantaneo Non Ostruibile

## Project Structure

This repository includes three sub-projects:

- **Firmware** - PlatformIO project to be uploaded on the ESP32 board.
- **Backend** - Software capable of communicating with the board through serial
- **Frontend** - Optional Web Interface for the backend

## Setup

In the `backend/` directory, create a virtual environment and run:
`pip install .[all]`
or if you want to install exclusively the cli/server dependencies
`poetry install .[cli]`
`poetry install .[server]`

If using the web frontend, in the `frontend/` directory, run 
`npm install`
`npm run build`

## Usage

### CLI

`peperoncino_backend cli [COMMAND]`
The available commands are:

- `start` - start or resume the drawing job
- `pause` - pause the drawing job
- `reset` - reset the drawing job (restart from line 0)
- `send $path` - send a file. The path to a valid gcode file must be specified.

Since they're still in early development, the frontend, backend and firmware might get out of sync. If you see strange things (like the plotter not responding to the commands you send) I suggest restarting the backend, then resetting the esp32 and refreshing the frontend.

### Server

in `backend/`
```sh
peperoncino_backend server
```

in `frontend/`
```sh
npm run preview
```
