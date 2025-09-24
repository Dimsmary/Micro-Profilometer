#include <stdlib.h>
#include <bsp/board_api.h>
#include <string.h>
#include <stdbool.h>
#include <tusb.h>
#include <pico/stdio.h>
#include <lib/ad57x1/ad57x1.hpp>

#define CMD_BUF_SIZE 64

void tud_cdc_rx_cb(uint8_t itf);
void process_command(const char *cmd_line);

extern uint16_t tri_steps;
extern float tri_bias_voltage;
extern float tri_increasement;
extern float tri_amplitude;
extern bool tri_forward;
extern bool tri_x;

extern float dac_val;
extern uint8_t dac_range;
extern uint8_t dac_num;

extern bool command_dac;
extern bool command_dac_range;
extern bool command_tri;

// 全局命令缓冲区
static char cmd_buf[CMD_BUF_SIZE];
static uint8_t cmd_buf_pos = 0;