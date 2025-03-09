# P.E.P.E.R.O.N.C.I.N.O
Plotter Estremamente Preciso E Reattivo Ottimizzato Nel Controllo Istantaneo Non Ostruibile 


## Project Structure
This repository includes three sub-projects:
- **Firmware** - PlatformIO project to be uploaded on the ESP32 board. 
- **Backend** - Software capable of communicating with the board through serial
- **Frontend** - Optional Web Interface for the backend

## Setup
In the `backend/` directory, run:
`pip install .[all]`
or if you want to install exclusively the cli/server dependencies
`poetry install .[cli]`
`poetry install .[server]`

## Usage
### CLI
`peperoncino_backend cli [COMMAND]`
The available commands are:
- `start` - start or resume the drawing job
- `pause` - pause the drawing job
- `reset` - reset the drawing job (restart from line 0)
- `send $path` - send a file. The path to a valid gcode file must be specified.

### Server
`peperoncino_backend server`