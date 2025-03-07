#include "gcode.h"

bool mm = true;

void parse_gcode_line(const char *line)
{
    const char *cmd;
    const char *x;
    const char *y;
    char gcode[64] = {0};
    double x_v, y_v;

    // Serial.printf("Line (%i): %s\n", strlen(line), line);
    // for (int i = 0; i < strlen(line); i++) {
    //     Serial.printf("%x\n", line[i]);
    // }


    strcpy(gcode, line);
    Serial.printf("line: %s\n", gcode);
    cmd = strtok(gcode, " ");

    if (strcmp(cmd, "G00") == 0)
    {
        // Serial.println("move");
        setPenUp();

        // x and y are in the form 'X3507 Y2305', to skip the first char increase the pointer
        x = strtok(NULL, " ");
        x++;
        y = strtok(NULL, " ");
        y++;

        // Serial.printf("x: %s, y: %s\n", x, y);
        x_v = std::stod(x);
        y_v = std::stod(y);

        if (!mm)
        {
            x_v = 25.4 * x_v;
            y_v = 25.4 * y_v;
        }
        move(x_v, y_v, true);
        // Serial.printf("x: %f mm, y: %f mm\n", x_v, y_v);
    }
    else if (strcmp(cmd, "G01") == 0)
    {
        // Serial.println("write");
        setPenDown();
        x = strtok(NULL, " ");
        x++;
        y = strtok(NULL, " ");
        y++;
        // Serial.printf("x: %s, y: %s\n", x, y);
        x_v = std::stod(x);
        y_v = std::stod(y);

        if (!mm)
        {
            x_v = 25.4 * x_v;
            y_v = 25.4 * y_v;
        }
        move(x_v, y_v, false);
        // Serial.printf("x: %f mm, y: %f mm\n", x_v, y_v);
    }
    else if (strcmp(cmd, "G17") == 0)
    { // select plane XY
        // Serial.println("XY");
    }
    else if (strcmp(cmd, "G20") == 0)
    { // interpret as inches
        Serial.println("Inches");
        mm = false;
    }
    else if (strcmp(cmd, "G21") == 0)
    { // interpret as mm
        Serial.println("mm");
        mm = true;
    }
    else if (strcmp(cmd, "G90") == 0)
    { // absolute positioning
        // Serial.println("absolute");
    }
    else if (strcmp(cmd, "M2") == 0)
    { // end of program
        Serial.println("Stop");
        setPenUp();
        move(0, 0, true);
    }
    else
    {
        Serial.printf("Received Unknown Command: %s\n", line);
        // Handle other commands or do nothing
    }
}