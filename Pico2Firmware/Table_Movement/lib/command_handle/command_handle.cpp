#include "command_handle.hpp"


// callback when data is received on a CDC interface
void tud_cdc_rx_cb(uint8_t itf)
{
    uint8_t buf[CFG_TUD_CDC_RX_BUFSIZE];
    uint32_t count = tud_cdc_n_read(itf, buf, sizeof(buf));
    if (count == 0) return;

    for (uint32_t i = 0; i < count; i++) {
        char c = (char)buf[i];

        // 过滤回车符
        if (c == '\r') continue;

        if (c == '\n') {
            // 遇到换行，命令结束
            cmd_buf[cmd_buf_pos] = 0; // 结束符
            if (cmd_buf_pos > 0) {
                process_command(cmd_buf);
            }
            cmd_buf_pos = 0; // 清空缓冲区
        } else {
            if (cmd_buf_pos < CMD_BUF_SIZE - 1) {
                cmd_buf[cmd_buf_pos++] = c;
            } else {
                // 缓冲区溢出，重置
                cmd_buf_pos = 0;
            }
        }
    }
}

void process_command(const char *cmd_line)
{
    size_t len = strlen(cmd_line);
    if (len < 5) return;

    char cmd[7] = {0};  // Extra byte preventing overflow
    memcpy(cmd, cmd_line, 6); // split the command

    char resp[64];
    resp[0] = 0;

    // Command Resolving

    // Triangle wave step setting
    if (strncmp(cmd, "TRSTP", 5) == 0)
    {
        if (len < 11) return;
        char param_str[7] = {0};
        memcpy(param_str, cmd_line + 5, 6);
        int val = atoi(param_str);
        tri_steps = val;
        snprintf(resp, sizeof(resp), "TRSTP OK: %d\r\n", tri_steps);
    }

    // Triangle wave bias setting
    else if (strncmp(cmd, "TRBIA", 5) == 0)
    {
        if (len < 11) return;
        char param_str[7] = {0};
        memcpy(param_str, cmd_line + 5, 6);

        char int_part_str[3] = {0};
        char dec_part_str[5] = {0};
        memcpy(int_part_str, param_str, 2);
        memcpy(dec_part_str, param_str + 2, 4);

        int int_part = atoi(int_part_str);
        int dec_part = atoi(dec_part_str);

        tri_bias_voltage = int_part + dec_part / 10000.0f;
        snprintf(resp, sizeof(resp), "TRBIA OK: %.4f\r\n", tri_amplitude);
    }

    // Triangle wave increment setting (Unit:V)
    else if (strncmp(cmd, "TRINC", 5) == 0)
    {
        if (len < 11) return;
        char param_str[7] = {0};
        memcpy(param_str, cmd_line + 5, 6);

        char int_part_str[3] = {0};
        char dec_part_str[5] = {0};
        memcpy(int_part_str, param_str, 2);
        memcpy(dec_part_str, param_str + 2, 4);

        int int_part = atoi(int_part_str);
        int dec_part = atoi(dec_part_str);

        tri_increasement = int_part + dec_part / 10000.0f;
        snprintf(resp, sizeof(resp), "TRINC OK: %.4f\r\n", tri_increasement);
    }

    // Triangle wave amplitude setting (Unit:V)
    else if (strncmp(cmd, "TRAMP", 5) == 0)
    {
        if (len < 11) return;
        char param_str[7] = {0};
        memcpy(param_str, cmd_line + 5, 6);

        char int_part_str[3] = {0};
        char dec_part_str[5] = {0};
        memcpy(int_part_str, param_str, 2);
        memcpy(dec_part_str, param_str + 2, 4);

        int int_part = atoi(int_part_str);
        int dec_part = atoi(dec_part_str);

        tri_amplitude = int_part + dec_part / 10000.0f;
        snprintf(resp, sizeof(resp), "TRAMP OK: %.4f\r\n", tri_amplitude);
    }

    // Triangle wave direction setting
    else if (strncmp(cmd, "TRFWD", 5) == 0)
    {
        tri_forward = true;
        command_tri = true;
        snprintf(resp, sizeof(resp), "TRFWD OK\r\n");
    }
    else if (strncmp(cmd, "TRBKD", 5) == 0)
    {
        tri_forward = false;
        command_tri = true;
        snprintf(resp, sizeof(resp), "TRBKD OK\r\n");
    }

    // Triangle wave channel select
    else if (strncmp(cmd, "TRSLX", 5) == 0)
    {
        tri_x = true;
        snprintf(resp, sizeof(resp), "TRSLX OK\r\n");
    }

    else if (strncmp(cmd, "TRSLY", 5) == 0)
    {
        tri_x = false;
        snprintf(resp, sizeof(resp), "TRSLY OK\r\n");
    }

    // Positive DAC Voltage setting
    else if (strncmp(cmd, "DACVA", 5) == 0)
    {
        if (len < 11) return;
        char param_str[7] = {0};
        memcpy(param_str, cmd_line + 5, 6);

        char int_part_str[3] = {0};
        char dec_part_str[5] = {0};
        memcpy(int_part_str, param_str, 2);
        memcpy(dec_part_str, param_str + 2, 4);

        int int_part = atoi(int_part_str);
        int dec_part = atoi(dec_part_str);

        dac_val = int_part + dec_part / 10000.0f;
        snprintf(resp, sizeof(resp), "DACVA OK: %.4f\r\n", dac_val);
        command_dac = true;
    }

    // Negative DAC Voltage setting
    else if (strncmp(cmd, "DACVB", 5) == 0)
    {
        if (len < 11) return;
        char param_str[7] = {0};
        memcpy(param_str, cmd_line + 5, 6);

        char int_part_str[3] = {0};
        char dec_part_str[5] = {0};
        memcpy(int_part_str, param_str, 2);
        memcpy(dec_part_str, param_str + 2, 4);

        int int_part = atoi(int_part_str);
        int dec_part = atoi(dec_part_str);

        dac_val = int_part + dec_part / 10000.0f;
        dac_val = -dac_val;
        snprintf(resp, sizeof(resp), "DACVB OK: %.4f\r\n", dac_val);
        command_dac = true;
    }

    // DAC Range setting
    else if (strncmp(cmd, "DACRA", 5) == 0)
    {
        if (len < 11) return;
        char param_str[7] = {0};
        memcpy(param_str, cmd_line + 5, 6);
        dac_range = atoi(param_str);
        snprintf(resp, sizeof(resp), "DACRA OK: %d\r\n", dac_range);
        command_dac_range = true;
    }

    // DAC number selecting
    else if (strncmp(cmd, "DACNU", 5) == 0)
    {
        if (len < 11) return;
        char param_str[7] = {0};
        memcpy(param_str, cmd_line + 5, 6);
        dac_num = atoi(param_str);
        snprintf(resp, sizeof(resp), "DACNU OK: %d\r\n", dac_num);
    }
    else
    {
        // Command not recognized
        return;
    }

    // feedback to uart
    tud_cdc_n_write(0, (const uint8_t *)resp, strlen(resp));
    tud_cdc_n_write_flush(0);
}
