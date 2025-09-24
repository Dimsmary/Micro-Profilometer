# gui.py
import tkinter as tk
from tkinter import ttk
from serial_manager import SerialManager
from tab_serial import SerialTab
from tab_dac_control import DACControl
from tab_sawtooth_control import SawtoothControlTab
from tab_scan import ScanTab

# ------------------------- Main App -------------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Confocal Profilometry")

        self.serial_manager = SerialManager()

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        # 串口
        serial_tab = SerialTab(notebook, self.serial_manager)
        notebook.add(serial_tab, text="Serial Ports")

        # DAC 控制
        dac_tab = ttk.Frame(notebook)
        notebook.add(dac_tab, text="DAC Manual Control")
        for i in range(3):
            dac_control = DACControl(dac_tab, dac_id=i, serial_manager=self.serial_manager)
            dac_control.pack(fill="x", padx=10, pady=5)

        # 锯齿波
        sawtooth_tab = SawtoothControlTab(notebook, self.serial_manager)
        notebook.add(sawtooth_tab, text="Sawtooth Control")

        # 扫描
        scan_tab = ScanTab(notebook, self.serial_manager)
        notebook.add(scan_tab, text="Scan")

if __name__ == "__main__":
    app = App()
    app.mainloop()
