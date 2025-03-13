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
void send_confirmation_signal();

const std::unordered_map<unsigned char, callback_function> comms_table = {
    { 0x00, start },
    { 0x01, stop },
    { 0x02, readGCodeFile },
    { 0x03, reset },
    { 0x04, readOnlineGCode }
};

#endif