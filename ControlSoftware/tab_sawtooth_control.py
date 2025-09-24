from serial_manager import SerialManager
from tkinter import ttk
import tkinter as tk
import threading

# ------------------------- Sawtooth Control Tab -------------------------

class SawtoothControlTab(ttk.Frame):
    def __init__(self, parent, serial_manager: SerialManager):
        super().__init__(parent)
        self.serial_manager = serial_manager

        self.steps_var = tk.StringVar(value="10")
        self.increment_var = tk.StringVar(value="0.0500")
        self.amplitude_var = tk.StringVar(value="10.0000")
        self.bias_var = tk.StringVar(value="0")  # 新增 bias 变量

        # 互斥选择 X 或 Y
        self.channel_var = tk.StringVar(value="X")  # "X" or "Y"

        self.is_sending = False

        self.create_widgets()

    def create_widgets(self):
        row = 0
        ttk.Label(self, text="Sawtooth Steps:").grid(row=row, column=0, sticky="e")
        ttk.Entry(self, textvariable=self.steps_var, width=10).grid(row=row, column=1, sticky="w")
        row += 1

        ttk.Label(self, text="Increment:").grid(row=row, column=0, sticky="e")
        ttk.Entry(self, textvariable=self.increment_var, width=10).grid(row=row, column=1, sticky="w")
        row += 1

        ttk.Label(self, text="Maximum Voltage:").grid(row=row, column=0, sticky="e")
        ttk.Entry(self, textvariable=self.amplitude_var, width=10).grid(row=row, column=1, sticky="w")
        row += 1

        # Bias 输入框
        ttk.Label(self, text="Bias Voltage:").grid(row=row, column=0, sticky="e")
        ttk.Entry(self, textvariable=self.bias_var, width=10).grid(row=row, column=1, sticky="w")
        row += 1

        # 互斥按钮 + 自动同步
        ttk.Label(self, text="Channel Select:").grid(row=row, column=0, sticky="e")
        frame_channel = ttk.Frame(self)
        frame_channel.grid(row=row, column=1, sticky="w")
        ttk.Radiobutton(
            frame_channel, text="X Channel", variable=self.channel_var,
            value="X", command=self.sync_settings
        ).pack(side="left", padx=2)
        ttk.Radiobutton(
            frame_channel, text="Y Channel", variable=self.channel_var,
            value="Y", command=self.sync_settings
        ).pack(side="left", padx=2)
        row += 1

        btn_sync = ttk.Button(self, text="Sync Settings", command=self.sync_settings)
        btn_sync.grid(row=row, column=0, columnspan=2, pady=5)
        row += 1

        btn_pos = ttk.Button(self, text="Send Positive Sawtooth", command=lambda: self.send_sawtooth(True))
        btn_pos.grid(row=row, column=0, pady=5, sticky="ew")

        btn_neg = ttk.Button(self, text="Send Negative Sawtooth", command=lambda: self.send_sawtooth(False))
        btn_neg.grid(row=row, column=1, pady=5, sticky="ew")

    def sync_settings(self):
        if not self.serial_manager.is_open("moving table"):
            print("Error: Serial port 'moving table' not connected.")
            return
        try:
            steps = int(self.steps_var.get())
            if steps < 1:
                raise ValueError
            increment = float(self.increment_var.get())
            amplitude = float(self.amplitude_var.get())
            bias = float(self.bias_var.get())  # 读取 bias
        except Exception:
            print("Invalid input: Please input valid numbers for all fields.")
            return

        cmds = [
            f"TRSTP{steps:06d}",
            self._format_float_command("TRINC", increment),
            self._format_float_command("TRAMP", amplitude),
            self._format_float_command("TRBIA", bias),  # 同步 bias
        ]

        if self.channel_var.get() == "X":
            cmds.append("TRSLX000000")
        else:
            cmds.append("TRSLY000000")

        for c in cmds:
            self.serial_manager.send_command("moving table", c)

        print("Settings sent.")

    def _format_float_command(self, cmd_prefix, value):
        integer_part = int(abs(value))
        decimal_part = int(round((abs(value) - integer_part) * 10000))
        param = f"{integer_part:02d}{decimal_part:04d}"
        return f"{cmd_prefix}{param}"

    def send_sawtooth(self, positive: bool):
        if self.is_sending:
            print("Info: Already sending command, please wait.")
            return
        if not self.serial_manager.is_open("moving table"):
            print("Error: Serial port 'moving table' not connected.")
            return

        self.is_sending = True

        def task():
            cmd = "TRFWD000000" if positive else "TRBKD000000"
            success = False
            try:
                success = self.serial_manager.send_command_wait_ok("moving table", cmd)
            except Exception as e:
                print(f"send_command_wait_ok exception: {e}")
            if success:
                print(f"{'Positive' if positive else 'Negative'} sawtooth command acknowledged.")
            else:
                print("Error: No acknowledgement received.")
            self.is_sending = False

        threading.Thread(target=task, daemon=True).start()
