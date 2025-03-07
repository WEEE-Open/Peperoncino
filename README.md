# P.E.P.E.R.O.N.C.I.N.O
Plotter Estremamente Preciso E Reattivo Ottimizzato Nel Controllo Istantaneo Non Ostruibile 


## Project Structure
This repository includes three sub-projects:
- **Firmware** - PlatformIO project to be uploaded on the ESP32 board. 
- **Backend** - Software capable of communicating with the board through serial
- **Frontend** - Optional Web Interface for the backend

## Setup
The backend can be installed with poetry install (soon to be a PyPi package)
poetry env use python
poetry install

## Usage
poetry run cli
