#include <Arduino.h>
#include "comms.h"
#include "consts.h"
#include "server.h"
#include <unordered_map>
#include <WiFi.h>
#include "gcode.h"

extern bool running;

extern char **gcode;
extern unsigned int length;
extern unsigned int line;

extern const std::unordered_map<unsigned char, callback_function> comms_table;

void start()
{
    Serial.println("Start");
    running = true;
    //     triggerInterrupt();
}

void stop()
{
    Serial.println("Stop");
    running = false;
    //     triggerInterrupt();
}

void reset()
{
    Serial.println("Reset");
    running = false;
    delay(100);
    line = 0;
    setPenUp();
    move(0, 0, true);
    // triggerInterrupt();
}

void readGCodeFile()
{
    size_t received_size;
    char buffer[64];

    Serial.println("Read");

    bool tmp = running; // pause the execution
    running = false;

    if (gcode != nullptr) {
        for (int i = 0; i < length; i++) {
            if (gcode[i] != nullptr) {
                delete[] gcode[i];
            }
        }
        delete[] gcode;
    }

    length = 0;
    for (int i = 0; i < 4; i++)
    {
        while (Serial.available() <= 0) {}
        length |= (Serial.read() << (8 * i));
    }

    
    gcode = new char *[length];
    line = 0;

    
    for (unsigned int i = 0; i < length; i++)
    {
        received_size = Serial.readBytesUntil('\n', buffer, 63);
        buffer[received_size] = '\0';
        // Serial.println(Serial.read());
        gcode[i] = new char [received_size+1];
        gcode[i] = strcpy(gcode[i], buffer);
        // Serial.printf("Parsing Line: %s\n", gcode[i]);
    }

    Serial.printf("Received length %u\n", length);
    running = tmp;
}

void readOnlineGCode() {

    size_t received_size;
    char buffer[64];

    Serial.println("Read Online");

    running = false;

    length = 0;
    for (int i = 0; i < 4; i++)
    {
        while (Serial.available() <= 0) {}
        length |= (Serial.read() << (8 * i));
    }

    
    Serial.printf("Received length %u\n", length);

    
    for (unsigned int i = 0; i < length; i++)
    {
        // Serial.println(i);
        received_size = Serial.readBytesUntil('\n', buffer, 63);
        buffer[received_size] = '\0';
        // Serial.print('A');
        // Serial.println(buffer);
        parse_gcode_line(buffer);
    }

    Serial.println("Done");
}

void send_confirmation_signal() {
    Serial.printf("Done %d\n", length);
}

void handleBackendComms(void *parameter)
{
    unsigned char received_cmd;

    while (true)
    {
        // server_listen();
        
        // Serial.print("Z");
        if (Serial.available() > 0)
        {
            received_cmd = Serial.read();
            // Serial.printf("Received: %s\n", received_cmd);
            if (comms_table.find(received_cmd) != comms_table.end())
            {
                comms_table.at(received_cmd)();
            }
            else
            {
                Serial.println("Unknown command received");
            }
        }
    }
}