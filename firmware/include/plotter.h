#ifndef PLOTTER_H
#define PLOTTER_H

#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_MCP4725.h>
#include "consts.h"

extern Adafruit_MCP4725 dacX;
extern Adafruit_MCP4725 dacY;

extern volatile bool penDown;

extern double delay_multiplier;

#define setPenDown()              \
  {                               \
    if (!penDown)                 \
    {                             \
      digitalWrite(PEN_PIN, LOW); \
      penDown = true;             \
      delay(300);                 \
    }                             \
  }

#define setPenUp()                 \
  {                                \
    if (penDown)                   \
    {                              \
      digitalWrite(PEN_PIN, HIGH); \
      penDown = false;             \
      delay(300);                  \
    }                              \
  }

#define sendX(x)                                                  \
  {                                                               \
    dacX.setVoltage(std::min((unsigned int)(x), MAX_DAC), false); \
  }

#define sendY(y)                                                  \
  {                                                               \
    dacY.setVoltage(std::min((unsigned int)(y), MAX_DAC), false); \
  }

#define get_wait(x, y) ({                   \
  double _dx = abs((double)(x) - currentX); \
  double _dy = abs((double)(y) - currentY); \
  double _d = sqrt(_dx * _dx + _dy * _dy);  \
  _d * delay_multiplier;                     \
})

#define plotter_setup()          \
  {                              \
    dacX.begin(X_addr);          \
    dacY.begin(Y_addr);          \
    dacX.setVoltage(0, true);    \
    dacY.setVoltage(0, true);    \
    digitalWrite(PEN_PIN, HIGH); \
  }

unsigned int mm_to_DAC(double v);
void move(double x, double y, bool fast);

#endif