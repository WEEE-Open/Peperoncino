#ifndef CONSTS_H
#define CONSTS_H

#define BAUD_RATE 115200

#define X_addr 0x62
#define Y_addr 0x63

#define PEN_PIN 32

#define MAX_DAC ((1 << 12) - 1u)
#define SHORTEST_SIZE_MM 200.0
#define MM_DAC_RATIO (MAX_DAC / SHORTEST_SIZE_MM)

#define DELAY_MULTIPLIER 4

typedef void (*callback_function)(void);

#endif