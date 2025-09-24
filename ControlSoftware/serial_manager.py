import serial
import serial.tools.list_ports
import time


class SerialManager:
    def __init__(self):
        self.ports = {
            "moving table": None,
            "confocal": None,
        }

    def list_ports(self):
        """列出所有可用串口设备"""
        return [p.device for p in serial.tools.list_ports.comports()]

    def open_port(self, port_key, port_name, baudrate=115200):
        """打开指定串口"""
        try:
            if self.ports[port_key] is not None and self.ports[port_key].is_open:
                self.ports[port_key].close()
            self.ports[port_key] = serial.Serial(port=port_name, baudrate=baudrate, timeout=1)
            print(f"{port_key} opened on {port_name} at {baudrate} baud")
            return True
        except Exception as e:
            print(f"Failed to open {port_key} on {port_name}: {e}")
            return False

    def close_port(self, port_key):
        """关闭指定串口"""
        if self.ports[port_key] is not None and self.ports[port_key].is_open:
            self.ports[port_key].close()
            print(f"{port_key} closed")
        self.ports[port_key] = None

    def is_open(self, port_key):
        """检查指定串口是否打开"""
        return self.ports[port_key] is not None and self.ports[port_key].is_open

    def send_command(self, port_key, command: str):
        """向指定串口发送命令，不等待确认"""
        if not self.is_open(port_key):
            print(f"[{port_key}] not open, cannot send command")
            return False
        try:
            self.ports[port_key].write((command + '\r\n').encode())
            self.ports[port_key].flush()
            print(f"Sent to [{port_key}]: {command}")

            # 读取 MCU 返回并打印
            resp = self.read_line(port_key, timeout=1)
            if resp:
                print(f"[{port_key}] -> {resp}")

            return True
        except Exception as e:
            print(f"Failed to send on [{port_key}]: {e}")
            return False

    def read_byte(self, port_key):
        return self.ports[port_key].read(1)

    def read_line(self, port_key, timeout=2):
        """从串口读取一行"""
        if not self.is_open(port_key):
            return None
        self.ports[port_key].timeout = timeout
        try:
            line = self.ports[port_key].readline()
            return line.decode(errors='ignore').strip()
        except Exception:
            return None

    def send_command_wait_ok(self, port_key, command: str, wait_ok="TRIOK", timeout=3):
        """发送命令并等待确认字符串"""
        if not self.send_command(port_key, command):
            return False
        start_time = time.time()
        while time.time() - start_time < timeout:
            resp = self.read_line(port_key, timeout=timeout)

            if resp == wait_ok:
                print(f"{port_key} received OK: {resp}")
                return True
        print(f"{port_key} did not receive OK within {timeout}s")
        return False
