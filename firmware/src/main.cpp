#include <Arduino.h>
#include <WiFi.h>
#include "consts.h"
#include "plotter.h"
#include "server.h"
#include "comms.h"
#include "gcode.h"
#include "esp_heap_caps_init.h"

TaskHandle_t Task1;

bool running = false;

char **gcode = nullptr;
unsigned int length;
unsigned int line;

const char *ssid = "WEEEPlotter";
const char *password = "asdasdasd";
const int channel = 10;
const bool hide_SSID = false; 
const int max_connection = 8; 
IPAddress local_ip(192, 168, 0, 1);
IPAddress gateway(192, 168, 0, 1);
IPAddress subnet(255, 255, 255, 0);

// SET_LOOP_TASK_STACK_SIZE( 1 << 16 );


void setup()
{
  Serial.begin(BAUD_RATE);
  Serial.setTimeout(-1);

  pinMode(PEN_PIN, OUTPUT);

  plotter_setup();
  
  xTaskCreatePinnedToCore(
      handleBackendComms, /* Function to implement the task */
      "Task1",            /* Name of the task */
      (1<<13),              /* Stack size in words */
      NULL,               /* Task input parameter */
      0,                  /* Priority of the task */
      &Task1,             /* Task handle. */
      0                   /* Core where the task should run */
  );
  // Serial.println(heap_caps_get_free_size(MALLOC_CAP_8BIT));
  // move(1, 0);
  // move(1, 1);
  // move(0, 1);
  // move(0, 0);
  // WiFi.mode(WIFI_AP_STA);
  // WiFi.softAPConfig(local_ip, gateway, subnet);
  // WiFi.softAP(ssid, password, channel, hide_SSID, max_connection);
  // Serial.printf("Network: %s\n", WiFi.softAPIP().toString());
  // connect(ssid, password);
  // Serial.printf("IP: %s\n", WiFi.localIP().toString());
  heap_caps_enable_nonos_stack_heaps();
  Serial.println("Setup Done");
}

void loop()
{
  if (running && line < length)
  {
    // Serial.printf("parsing line %i\n", line);
    // Serial.printf("Line: %s\n", line);
    parse_gcode_line(gcode[line]);
    line++;
  }
  
}