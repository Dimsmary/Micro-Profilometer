from serial_manager import SerialManager
from tkinter import ttk, messagebox
import tkinter as tk

# ------------------------- DAC Manual Control -------------------------
class DACControl(tk.Frame):
    def __init__(self, parent, dac_id, serial_manager: SerialManager):
        super().__init__(parent)
        self.dac_id = dac_id
        self.serial_manager = serial_manager

        self.ranges = {
            "-10V~10V": 0b00,
            "0~10V": 0b01,
            "-5~5V": 0b10,
            "0~5V": 0b11,
        }

        self.selected_range = tk.StringVar(value="-10V~10V")
        self.voltage_var = tk.DoubleVar(value=0.0)
        self.input_voltage_str = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text=f"DAC {self.dac_id} Control").grid(row=0, column=0, columnspan=3, pady=5)
        ttk.Label(self, text="Voltage Range:").grid(row=1, column=0, sticky="w")
        range_menu = ttk.OptionMenu(self, self.selected_range, self.selected_range.get(), *self.ranges.keys(), command=self.on_range_change)
        range_menu.grid(row=1, column=1, columnspan=2, sticky="ew")

        ttk.Label(self, text="Voltage:").grid(row=2, column=0, sticky="w")
        self.scale = ttk.Scale(self, from_=-10, to=10, orient="horizontal", variable=self.voltage_var, command=self.on_scale_change)
        self.scale.grid(row=2, column=1, columnspan=2, sticky="ew")

        ttk.Label(self, text="Set Voltage:").grid(row=3, column=0, sticky="w")
        self.input_entry = ttk.Entry(self, textvariable=self.input_voltage_str)
        self.input_entry.grid(row=3, column=1, sticky="ew")
        btn_set = ttk.Button(self, text="Set", command=self.on_set_button)
        btn_set.grid(row=3, column=2, sticky="ew")

        self.columnconfigure(1, weight=1)

    def on_range_change(self, selected):
        param = self.ranges[selected]
        # 只通过 moving table 端口发送设置范围命令
        if self.serial_manager.is_open("moving table"):
            # Select chip
            cmd = f"DACNU{self.dac_id:06d}"
            self.serial_manager.send_command("moving table", cmd)
            # Set range parameters
            cmd = f"DACRA{param:06d}"
            self.serial_manager.send_command("moving table", cmd)


        # 更新滑条范围
        if selected == "-10V~10V":
            self.scale.configure(from_=-10, to=10)
        elif selected == "0~10V":
            self.scale.configure(from_=0, to=10)
        elif selected == "-5~5V":
            self.scale.configure(from_=-5, to=5)
        elif selected == "0~5V":
            self.scale.configure(from_=0, to=5)

    def on_scale_change(self, value):
        val = float(value)
        self.input_voltage_str.set(f"{val:.4f}")
        self.send_voltage(val)

    def on_set_button(self):
        try:
            val = float(self.input_voltage_str.get())
        except ValueError:
            messagebox.showerror("Invalid input", "Please enter a valid voltage number.")
            return

        limits = {
            "-10V~10V": (-10, 10),
            "0~10V": (0, 10),
            "-5~5V": (-5, 5),
            "0~5V": (0, 5)
        }
        low, high = limits[self.selected_range.get()]
        if val < low or val > high:
            messagebox.showerror("Out of range", f"Voltage must be between {low} and {high} V.")
            return

        self.voltage_var.set(val)
        self.send_voltage(val)

    def send_voltage(self, voltage):
        if not self.serial_manager.is_open("moving table"):
            print("Serial port 'moving table' not open, cannot send voltage")
            return

        # 选择 DAC
        dac_num_cmd = f"DACNU{self.dac_id:06d}"
        self.serial_manager.send_command("moving table", dac_num_cmd)

        integer_part = int(abs(voltage))
        decimal_part = int(round((abs(voltage) - integer_part) * 10000))
        param = f"{integer_part:02d}{decimal_part:04d}"

        if voltage >= 0:
            dac_val_cmd = f"DACVA{param}"
        else:
            dac_val_cmd = f"DACVB{param}"
        self.serial_manager.send_command("moving table", dac_val_cmd)
