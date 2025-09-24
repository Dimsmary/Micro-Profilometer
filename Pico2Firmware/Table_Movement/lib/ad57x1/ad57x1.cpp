#include "ad57x1.hpp"

// === AD57x1 Command Definitions ===
#define CMD_WR_UPDATE_DAC_REG  0x03
#define CMD_WR_CTRL_REG        0x04
#define CMD_SW_FULL_RESET      0x0F

#define CONTROL_REG_BASE 0b0000000001101000

// Voltage factor table
const float VOLTAGE_FACTORS[8][2] = {
    {8.0f, 4.0f},     // -10 ~ +10V
    {4.0f, 0.0f},     // 0 ~ +10V
    {4.0f, 2.0f},     // -5 ~ +5V
    {2.0f, 0.0f},     // 0 ~ +5V
    {4.0f, 1.0f},     // -2.5 ~ +7.5V
    {2.4f, 1.2f},     // -3 ~ +3V
    {6.4f, 0.0f},     // 0 ~ 16V
    {8.0f, 0.0f}      // 0 ~ 20V
};

AD57x1::AD57x1(spi_inst_t *spi, uint cs_pin, bool is_16bit, float vref)
    : spi(spi), cs_pin(cs_pin), is_16bit(is_16bit), vref(vref), voltage_range(0b000) {
    gpio_init(cs_pin);
    gpio_set_dir(cs_pin, GPIO_OUT);
    gpio_put(cs_pin, 1); // Deselect
}

void AD57x1::cs_select() {
    gpio_put(cs_pin, 0);
}

void AD57x1::cs_deselect() {
    gpio_put(cs_pin, 1);
}

void AD57x1::write_register(uint8_t command, uint16_t data) {
    uint8_t buf[3] = {
        command,
        (uint8_t)((data >> 8) & 0xFF),
        (uint8_t)(data & 0xFF)
    };
    cs_select();
    spi_write_blocking(spi, buf, 3);
    cs_deselect();
}

void AD57x1::write_dac(uint16_t value) {
    write_register(CMD_WR_UPDATE_DAC_REG, value);
}

void AD57x1::write_voltage(float voltage) {
    uint16_t value = voltage_to_dac(voltage);
    write_dac(value);
}

uint16_t AD57x1::voltage_to_dac(float voltage) {
    int N = is_16bit ? 65535 : 4095;
    float m = VOLTAGE_FACTORS[voltage_range][0];
    float c = VOLTAGE_FACTORS[voltage_range][1];

    float reg_val = ((voltage / vref) + c) * N / m;
    if (reg_val < 0) reg_val = 0;
    if (reg_val > N) reg_val = N;

    return (uint16_t)reg_val;
}

void AD57x1::set_range(uint8_t range_code) {
    voltage_range = range_code & 0b111;
    uint16_t control = CONTROL_REG_BASE | voltage_range;
    write_register(CMD_WR_CTRL_REG, control);
}

void AD57x1::software_reset() {
    write_register(CMD_SW_FULL_RESET, 0);
    write_register(CMD_WR_CTRL_REG, CONTROL_REG_BASE);
}

