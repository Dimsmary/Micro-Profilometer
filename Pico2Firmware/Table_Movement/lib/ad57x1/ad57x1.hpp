#ifndef AD57X1_HPP
#define AD57X1_HPP

#include "hardware/spi.h"
#include "pico/stdlib.h"

class AD57x1 {
public:
    AD57x1(spi_inst_t *spi, uint cs_pin, bool is_16bit = true, float vref = 2.5f);

    void write_register(uint8_t command, uint16_t data);
    void write_dac(uint16_t value);
    void write_voltage(float voltage);
    void set_range(uint8_t range_code);
    void software_reset();

private:
    spi_inst_t *spi;
    uint cs_pin;
    bool is_16bit;
    float vref;
    uint8_t voltage_range;

    void cs_select();
    void cs_deselect();
    uint16_t voltage_to_dac(float voltage);
};

#endif // AD57X1_HPP
