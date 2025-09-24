import serial
import time

def extract_6bit_value(byte):
    """Discard 2MSB"""
    return byte & 0b00111111

def decode_24bit_from_3bytes(b0, b1, b2):
    """Concat the 6bit data into  24bit"""
    val = (extract_6bit_value(b2) << 12) | (extract_6bit_value(b1) << 6) | extract_6bit_value(b0)
    return val

# Initiate Serial Port, None Block
ser = serial.Serial(
    port='COM5',
    baudrate=115200,
    timeout=0
)

print("Reading...")

try:
    while True:
        # ser.reset_input_buffer()
        byte1 = ser.read(1)
        if byte1:
            b1 = byte1[0]
            prefix = (b1 & 0b11000000) >> 6
            if prefix == 0b00:
                byte2 = ser.read(1)
                byte3 = ser.read(1)
                if len(byte2) == 1 and len(byte3) == 1:
                    b2 = byte2[0]
                    b3 = byte3[0]
                    value = decode_24bit_from_3bytes(b1, b2, b3)
                    distance = (value - 98232) * 1.25/65536
                    print(distance)
                else:
                    # Wait for subsequent byte
                    continue
        else:
            # Sleep
            time.sleep(0.001)

except KeyboardInterrupt:
    ser.close()
    print("\nEnd")