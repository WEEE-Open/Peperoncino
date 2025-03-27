# Usability Testing

## Scope

This document serves as a base to conduct usability tests of the frontend.
The test's objective is understanding how the users interpret the interface and try to engage with it.
In turn, this allows improving the software in a way that matches the user's expectations on what it can do and how.

The target demographic is members of the team WEEE Open, which means:

- aged 19-30
- university studends
- mostly engineers
- good understanding of technology in general and computers specifically

As a prerequisite, they need to understand what the plotter does but shouldn't need to know the details of the implementation.

## Background

The following piece should be read to all participants before the test begins:

> The plotter is a device that can be controlled on two axes, to draw images with a pen/pencil or similar.
> To control it, we have developed this software, named Peperoncino, that allows you to select an image for the plotter to draw and to send commands like start, pause and reset.
> In the future we plan to allow sending raster images (like jpg, png and similar formats), but for now only SVG and GCODE is allowed.
> (If you don't know what GCODE is don't worry - it's a format common to 3D printers, plotters, CNC machines and similar devices. You won't need it)
> Before we start, keep in mind that we're not testing you but the software - any error or difficulty that arises is not your fault but instead it highlights a shortcoming in our design.

In Italian:

> Il plotter è un dispositivo che può essere controllato su due assi per disegnare immagini con una penna/matita o simili.
> Per controllarlo abbiamo sviluppato questo software, chiamato Peperoncino, che ti permette di selezionare un'immagine da far disegnare al plotter e di mandargli comandi come avvio, pausa e reset.
> In futuro pianifichiamo di permettere di mandare immagini raster (come jpg, png e formati simili), ma per ora supportiamo solo SVG e GCODE.
> (Se non sai cos'è GCODE non preoccuparti - è un formato comune a stampanti 3D, plotter, macchine CNC e dispositivi di questo genere. Non avrai bisogno di usarlo)
> Prima di iniziare, ricorda che non stiamo testando te ma il software - qualsiasi errore o difficoltà non è colpa tua ma mostra una falla del nostro design.

## Setup

Before performing the test, make sure the equipment is working and properly setup.

- [ ] The plotter is powered and set on 'Servo On'
- [ ] The pen is positioned at the bottom-right corner
- [ ] Range is 10 and Gain is barely more than 1 for both X and Y
- [ ] Sweep is external for X and Y
- [ ] Polarity is Normal for Y, Inverted for X
- [ ] The red and green cable go into Input X and Input Y and the blue cable into Remote 1 on the back of the plotter
- [ ] The arduino is connected via USB to a computer that will host the backend
- [ ] The backend is running
- [ ] The frontend is running
- [ ] The computer hosting the frontend can reach the computer hosting the backend (they can be the same computer)
- [ ] Double-check using the frontend yourself before showing it to the participant

## Test

> I will ask you to perform a series of tasks.
> You have all the time you deem necessary.
> When you think you're done or you can't complete the task let me know so we can jump to the next one.
> In any moment feel free to stop the test or ask me questions.

In Italian:

> Ti chiederò di svolgere una serie di task.
> Hai a disposizione tutto il tempo che ritieni necessario.
> Quando pensi di aver completato il task o ritieni di non riuscire a completarlo fammelo sapere per andare al successivo.
> In qualsiasi momento puoi interrompere oppure farmi domande.

After each task, submit a SEQ and keep note of the answer

> [!NOTE]
> a SEQ is a single question asking how easy the task was on a scale from 1 to 7, where 1 is very hard and 7 is very easy.

While the participant performs the tasks you (or preferably one colleague whose role is solely observing and taking notes) should take note of what they try to do.

After the test is done, you can ask specific questions about their actions to understand how the user reasoned about the interface.
Don't interrupt them while they perform the task.
Ask the user if they have any suggestions or inputs.

Some tasks may be tagged with **TA**, which means Think-Aloud: ask the participant to describe their thought and actions while they perform the task.

The specific tasks should be related to the specific version of the software being tested. If you have released a new version of Peperoncino and are updating the tasks,

- if it's a major version, create a new section in this document noting the new version.
- if it's a minor/patch version, edit the section of the corresponding major (remember to also update the version in the section)

## Tasks [v1.0]

> [!TIP]
> The server defaults to port 3000

| Task | Description                                                                                |
|------|--------------------------------------------------------------------------------------------|
| T1   | Make sure the program is connected to the server                                           |
| T2   | Start the default drawing and wait for it to finish                                        |
| T3   | Upload a file                                                                              |
| T4   | Start the drawing again, interrupt it after it starts and then resume it and let it finish |
| T5   | Change the drawing speed and make sure it changed                                          |
