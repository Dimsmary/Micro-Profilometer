#include "pico/stdlib.h"
#include "hardware/spi.h"
#include <lib/ad57x1/ad57x1.hpp>
#include <lib/command_handle/command_handle.hpp>

#include <bsp/board_api.h>

uint16_t tri_steps = 1;
float tri_bias_voltage = 0.0f;
float tri_increasement = 0.05f;
float tri_amplitude = 10.0f;
bool tri_x = true;
bool tri_forward = true;

float dac_val = 0.0f;
uint8_t dac_range = 0;
uint8_t dac_num = 0;


bool command_dac = false;
bool command_dac_range = false;
bool command_tri = false;

AD57x1 dac1(spi0, 17); // GPIO17 -> CS1
AD57x1 dac2(spi0, 20); // GPIO20 -> CS2
AD57x1 dac3(spi0, 21); // GPIO21 -> CS3

void generate_sawtooth_wave();

int main() {
    // init CDC UART
    board_init();
    tusb_init();

    stdio_init_all();
    
    // init SPI
    spi_init(spi0, 10 * 1000 * 1000);

    // Set SPI mode2
    spi_set_format(spi0,
                   8, 
                   SPI_CPOL_1, 
                   SPI_CPHA_0, 
                   SPI_MSB_FIRST); 
    gpio_set_function(18, GPIO_FUNC_SPI); // SCK
    gpio_set_function(19, GPIO_FUNC_SPI); // MOSI
    gpio_set_function(16, GPIO_FUNC_SPI); // MISO

    dac1.software_reset();
    dac2.software_reset();
    dac3.software_reset();

    dac1.set_range(0b000);
    dac2.set_range(0b000);
    dac3.set_range(0b000);

    while (true) {
        // TinyUSB device task | must be called regurlarly
        tud_task();
        
        // If there are command wating
        if(command_dac){
            // select dac
            switch (dac_num){
                case 0:
                dac1.write_voltage(dac_val);
                break;

                case 1:
                dac2.write_voltage(dac_val);
                break;

                case 2:
                dac3.write_voltage(dac_val);
                break;
            }
            command_dac = false;
        }

        else if(command_dac_range){
            switch (dac_num){
                case 0:
                dac1.set_range(dac_val);
                break;

                case 1:
                dac2.set_range(dac_val);
                break;

                case 2:
                dac3.set_range(dac_val);
                break;
            }
            command_dac_range = false;
        }

        else if(command_tri){
            generate_sawtooth_wave();
            command_tri = false;
        }
    // }
    }
}


void generate_sawtooth_wave()
{
    for (int wave = 0; wave < tri_steps; wave++)
    {
        float voltage;

        if (tri_forward)
        {
            // Positive wave
            for (voltage = 0.0f + tri_bias_voltage; voltage <= tri_amplitude + tri_bias_voltage; voltage += tri_increasement)
            {
                if (tri_x)
                    dac1.write_voltage(voltage);
                else
                    dac2.write_voltage(voltage);

            }

            // Zero
            if (tri_x)
                dac1.write_voltage(0.0f + tri_bias_voltage);
            else
                dac2.write_voltage(0.0f + tri_bias_voltage);
        }
        else
        {
            // Negative wave
            for (voltage = tri_bias_voltage; voltage >= (tri_bias_voltage - tri_amplitude); voltage -= tri_increasement)
            {
                if (tri_x)
                    dac1.write_voltage(voltage);
                else
                    dac2.write_voltage(voltage);
            }

            // back to mid point
            if (tri_x)
                dac1.write_voltage(tri_bias_voltage);
            else
                dac2.write_voltage(tri_bias_voltage);
        }
    }
    tud_cdc_n_write(0, "TRIOK\r\n", 7);
    tud_cdc_n_write_flush(0);
}


