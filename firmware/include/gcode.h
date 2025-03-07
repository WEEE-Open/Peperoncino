#ifndef GCODE_H
#define GCODE_H

#include <unordered_map>
#include <Arduino.h>
#include "consts.h"
#include "plotter.h"

void parse_gcode_line(const char* line);

#endif