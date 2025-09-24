from serial_manager import SerialManager
from tkinter import ttk, messagebox
import tkinter as tk

# ------------------------- Serial Ports Tab -------------------------
class SerialTab(ttk.Frame):
    def __init__(self, parent, serial_manager: SerialManager):
        super().__init__(parent)
        self.serial_manager = serial_manager

        self.port_names = {
            "moving table": tk.StringVar(),
            "confocal": tk.StringVar(),
        }
        self.baudrates = {
            "moving table": tk.StringVar(value="115200"),
            "confocal": tk.StringVar(value="115200"),
        }
        self.status_labels = {}

        self.create_widgets()
        self.refresh_ports()

    def create_widgets(self):
        row = 0
        for key in ["moving table", "confocal"]:
            ttk.Label(self, text=f"{key} Port:").grid(row=row, column=0, sticky="e", padx=4, pady=4)
            port_combo = ttk.Combobox(self, textvariable=self.port_names[key], values=[], width=16, state="readonly")
            port_combo.grid(row=row, column=1, sticky="w", padx=4, pady=4)

            ttk.Label(self, text="Baudrate:").grid(row=row, column=2, sticky="e", padx=4, pady=4)
            baud_entry = ttk.Entry(self, textvariable=self.baudrates[key], width=10)
            baud_entry.grid(row=row, column=3, sticky="w", padx=4, pady=4)

            btn_connect = ttk.Button(self, text="Connect", command=lambda k=key: self.connect_port(k))
            btn_connect.grid(row=row, column=4, padx=4, pady=4)

            btn_disconnect = ttk.Button(self, text="Disconnect", command=lambda k=key: self.disconnect_port(k))
            btn_disconnect.grid(row=row, column=5, padx=4, pady=4)

            status_label = ttk.Label(self, text="Disconnected", foreground="red")
            status_label.grid(row=row, column=6, sticky="w", padx=4, pady=4)
            self.status_labels[key] = status_label

            row += 1

        ttk.Button(self, text="Refresh Ports", command=self.refresh_ports).grid(row=row, column=0, columnspan=2, pady=8)

    def refresh_ports(self):
        try:
            import serial.tools.list_ports
            ports = [p.device for p in serial.tools.list_ports.comports()]
        except Exception:
            # 退化到 SerialManager.list_ports（如果逻辑层提供）
            ports = []
            try:
                ports = self.serial_manager.list_ports()
            except Exception:
                pass

        for idx, key in enumerate(self.port_names.keys()):
            current = self.port_names[key].get()
            self.port_names[key].set("")
            # 找到第 idx 行第 1 列的组合框（就是上面创建的）
            combos = self.grid_slaves(row=idx, column=1)
            if combos:
                combo = combos[0]
                combo['values'] = ports
            if current in ports:
                self.port_names[key].set(current)

    def connect_port(self, key):
        port_name = self.port_names[key].get()
        try:
            baud = int(self.baudrates[key].get())
        except Exception:
            messagebox.showerror("Error", f"Invalid baudrate for {key}")
            return

        if not port_name:
            messagebox.showerror("Error", f"No port selected for {key}")
            return

        success = False
        try:
            success = self.serial_manager.open_port(key, port_name, baud)
        except Exception as e:
            print(f"[{key}] open_port exception: {e}")

        if success:
            self.status_labels[key].config(text="Connected", foreground="green")
            print(f"[{key}] Connected to {port_name} @ {baud}")
        else:
            messagebox.showerror("Error", f"Failed to connect {key}")

    def disconnect_port(self, key):
        try:
            self.serial_manager.close_port(key)
        finally:
            self.status_labels[key].config(text="Disconnected", foreground="red")
            print(f"[{key}] Disconnected")