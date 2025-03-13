#include "plotter.h"
#include "consts.h"

Adafruit_MCP4725 dacX;
Adafruit_MCP4725 dacY;

double currentX = 0;
double currentY = 0;

volatile bool penDown = false;

unsigned int mm_to_DAC(double v)
{
  return round((v)*MM_DAC_RATIO);
}

void move(double x, double y, bool fast = false)
{
  double t;
  bool x_longer;
  int x_diff, y_diff;
  int long_side, short_side;
  int step_x, step_y;
  unsigned int target_x, target_y;

  target_x = mm_to_DAC(x);
  target_y = mm_to_DAC(y);
  t = get_wait(x, y);

  // fast = true;
  if (fast)
  {
    sendX(target_x);
    sendY(target_y);
    currentX = x;
    currentY = y;
    // Serial.printf("(a) Wating %f ms\n", t);
    delay(t/2);
  }
  else
  {
    unsigned int dist = abs(x - currentX) + abs(y - currentY);
    unsigned int interpolation_steps = STEPS_PER_MM * INTERPOLATION_APPROX_COEFF * dist;
    // Serial.println(interpolation_steps);
    for (float i = 1; i <= interpolation_steps; i++)
    {
      currentX += (i / interpolation_steps) * (x - currentX);
      currentY += (i / interpolation_steps) * (y - currentY);
      sendX(mm_to_DAC(currentX));
      sendY(mm_to_DAC(currentY));
      delay(t / interpolation_steps);
    }
  }
}
