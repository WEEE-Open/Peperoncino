#ifndef COMMS_H
#define COMMS_H

#include <unordered_map>
#include "consts.h"

void handleBackendComms(void* parameter);

void start();
void stop();
void reset();
void readGCodeFile();
void readOnlineGCode();
void readDelayMultiplier();
void writeState();

const std::unordered_map<unsigned char, callback_function> comms_table = {
    { 0x00, start },
    { 0x01, stop },
    { 0x02, readGCodeFile },
    { 0x03, reset },
    { 0x04, readOnlineGCode },
    { 0x05, readDelayMultiplier },
    { 0x06, writeState }
};

#endif