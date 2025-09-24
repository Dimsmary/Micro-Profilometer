from serial_manager import SerialManager
from tkinter import ttk, filedialog
import tkinter as tk
import threading
import time
import numpy as np
from PIL import Image, ImageTk


# ------------------------- Scan Tab -------------------------
class ScanTab(ttk.Frame):
    def __init__(self, parent, serial_manager: SerialManager):
        super().__init__(parent)
        self.serial_manager = serial_manager

        # 电压与参数
        self.x_fwd_var = tk.StringVar(value="10")
        self.x_bwd_var = tk.StringVar(value="10")
        self.y_fwd_var = tk.StringVar(value="10")
        self.y_bwd_var = tk.StringVar(value="10")  # 目前流程未用到，但保留
        self.size_x_var = tk.StringVar(value="10")     # Image size X（每行步数）
        self.size_y_var = tk.StringVar(value="10")     # Image size Y（行数）
        self.increment_var = tk.StringVar(value="0.05")

        # 监听线程控制
        self.monitoring = False
        self._monitor_thread = None
        self._monitor_stop = threading.Event()

        # 扫描线程控制
        self._scan_thread = None
        self._scan_stop = threading.Event()

        # Current Displacement
        self.current_displacement = 0

        # Scan Data storage
        self.scan_data_raw = np.zeros((200,200))
        self.scan_image = np.zeros((200,200))
        self.save_img = Image.fromarray(np.zeros((200,200)))

        # ---------- 实时显示文字 ----------
        self.monitor_var = tk.StringVar()
        self.monitor_var.set("0.00000mm")

        self.create_widgets()

    def create_widgets(self):
        # ----------------- 左侧控制面板 -----------------
        self.control_frame = ttk.Frame(self)
        self.control_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nw")

        row = 0
        ttk.Label(self.control_frame, text="X Forward Steps:").grid(row=row, column=0, sticky="e", padx=4, pady=4)
        ttk.Entry(self.control_frame, textvariable=self.x_fwd_var, width=10).grid(row=row, column=1, sticky="w", padx=4,
                                                                                  pady=4)
        row += 1

        ttk.Label(self.control_frame, text="X Backward Steps:").grid(row=row, column=0, sticky="e", padx=4, pady=4)
        ttk.Entry(self.control_frame, textvariable=self.x_bwd_var, width=10).grid(row=row, column=1, sticky="w", padx=4,
                                                                                  pady=4)
        row += 1

        ttk.Label(self.control_frame, text="Y Forward Steps:").grid(row=row, column=0, sticky="e", padx=4, pady=4)
        ttk.Entry(self.control_frame, textvariable=self.y_fwd_var, width=10).grid(row=row, column=1, sticky="w", padx=4,
                                                                                  pady=4)
        row += 1

        ttk.Label(self.control_frame, text="Y Backward Steps:").grid(row=row, column=0, sticky="e", padx=4, pady=4)
        ttk.Entry(self.control_frame, textvariable=self.y_bwd_var, width=10).grid(row=row, column=1, sticky="w", padx=4,
                                                                                  pady=4)
        row += 1

        ttk.Label(self.control_frame, text="Image size X:").grid(row=row, column=0, sticky="e", padx=4, pady=4)
        ttk.Entry(self.control_frame, textvariable=self.size_x_var, width=10).grid(row=row, column=1, sticky="w",
                                                                                   padx=4, pady=4)
        row += 1

        ttk.Label(self.control_frame, text="Image size Y:").grid(row=row, column=0, sticky="e", padx=4, pady=4)
        ttk.Entry(self.control_frame, textvariable=self.size_y_var, width=10).grid(row=row, column=1, sticky="w",
                                                                                   padx=4, pady=4)
        row += 1

        ttk.Label(self.control_frame, text="Increment:").grid(row=row, column=0, sticky="e", padx=4, pady=4)
        ttk.Entry(self.control_frame, textvariable=self.increment_var, width=10).grid(row=row, column=1, sticky="w",
                                                                                      padx=4, pady=4)
        row += 1

        # 控制按钮
        self.btn_monitor = ttk.Button(self.control_frame, text="Start Monitor", command=self.toggle_monitor)
        self.btn_monitor.grid(row=row, column=0, padx=4, pady=8, sticky="ew")

        self.btn_scan = ttk.Button(self.control_frame, text="Scan", command=self.start_scan)
        self.btn_scan.grid(row=row, column=1, padx=4, pady=8, sticky="ew")

        # ----------------- 右侧显示面板 -----------------
        self.display_frame = ttk.Frame(self)
        self.display_frame.grid(row=0, column=1, padx=5, pady=5, sticky="nw")

        # monitor 文本
        self.monitor_label = ttk.Label(self.display_frame, textvariable=self.monitor_var, width=50, anchor="w")
        self.monitor_label.grid(row=0, column=0, sticky="nw", pady=4)

        # 初始化黑色图像
        img = Image.fromarray(self.scan_data_raw, mode="L")
        self.tk_img = ImageTk.PhotoImage(img)

        self.image_label = ttk.Label(self.display_frame, image=self.tk_img)
        self.image_label.grid(row=1, column=0, sticky="nw", pady=4)

        # 保存按钮
        self.save_button = ttk.Button(self.display_frame, text="Save Image", command=self.save_image)
        self.save_button.grid(row=2, column=0, sticky="w", pady=4)

    def save_image(self):
        if self.scan_data_raw is None:
            print("No scan data to save.")
            return

        # 弹出保存对话框，默认保存为 TIFF
        file_path = filedialog.asksaveasfilename(
            defaultextension=".tiff",
            filetypes=[("TIFF files", "*.tiff"), ("All files", "*.*")],
            title="Save Scan Image"
        )
        if not file_path:  # 用户取消
            return

        scan_corrected = self.scan_data_raw.copy()
        for i in range(scan_corrected.shape[0]):
            if i % 2 == 1:  # 奇数行（Python 从 0 开始，索引1,3,...）
                scan_corrected[i] = scan_corrected[i][::-1]  # 反转这一行

        # 将 self.scan_data 映射到 0~255
        min_val = np.nanmin(scan_corrected)
        max_val = np.nanmax(scan_corrected)
        norm_data = (scan_corrected - min_val) * 100000
        # norm_data = ((scan_corrected - min_val) / (max_val - min_val + 1e-9) * 255).astype(np.uint8)

        print(min_val)
        print(max_val)

        # 转成图像
        img = Image.fromarray(norm_data)
        # 转成图像并保存
        img.save(file_path, format="TIFF")
        self.save_img.save(file_path[:-5] + '_scaled.tiff', format="TIFF")
        print(f"Image saved to {file_path}")

    # ---------- Monitor ----------
    def toggle_monitor(self):
        if not self.serial_manager.is_open("confocal"):
            print("Error: Serial port 'confocal' not connected.")
            return

        if not self.monitoring:
            # 启动监听
            self.monitoring = True
            self._monitor_stop.clear()
            self.btn_monitor.config(text="Stop Monitor")
            self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._monitor_thread.start()
            print("[Monitor] Started.")
        else:
            # 停止监听
            self._monitor_stop.set()
            self.monitoring = False
            self.btn_monitor.config(text="Start Monitor")
            print("[Monitor] Stopped.")

    def extract_6bit_value(self, byte):
        """Discard 2MSB"""
        return byte & 0b00111111

    def decode_24bit_from_3bytes(self, b0, b1, b2):
        """Concat the 6bit data into  24bit"""
        val = (self.extract_6bit_value(b2) << 12) | (self.extract_6bit_value(b1) << 6) | self.extract_6bit_value(b0)
        return val

    def read_confocal(self, timeout=0.1):
        distance = -1
        byte1 = self.serial_manager.read_byte("confocal")
        if byte1:
            b1 = byte1[0]
            prefix = (b1 & 0b11000000) >> 6
            if prefix == 0b00:
                byte2 = self.serial_manager.read_byte("confocal")
                byte3 = self.serial_manager.read_byte("confocal")
                if len(byte2) == 1 and len(byte3) == 1:
                    b2 = byte2[0]
                    b3 = byte3[0]
                    value = self.decode_24bit_from_3bytes(b1, b2, b3)
                    distance = round((value - 98232) * 1.25/65536, 5)
                    self.current_displacement = distance
        return distance

    def _monitor_loop(self):
        while not self._monitor_stop.is_set() and self.serial_manager.is_open("confocal"):
            line = self.read_confocal()
            if line:
                self.monitor_var.set(str(line) + "mm")
        # 退出时复位
        self.monitoring = False
        self.btn_monitor.config(text="Start Monitor")

    # ---------- Scan ----------
    def start_scan(self):
        if self._scan_thread and self._scan_thread.is_alive():
            print("Scan already running.")
            return

        if not (self.serial_manager.is_open("moving table") and self.serial_manager.is_open("confocal")):
            print("Error: Please connect both 'moving table' and 'confocal' ports.")
            return

        # 解析参数
        try:
            size_x = int(self.size_x_var.get())
            size_y = int(self.size_y_var.get())
            inc = float(self.increment_var.get())

            x_fwd = float(self.x_fwd_var.get())
            x_bwd = float(self.x_bwd_var.get())
            y_fwd = float(self.y_fwd_var.get())

            if size_x < 1 or size_y < 1 or inc <= 0:
                raise ValueError

        except Exception:
            print("Invalid input: please check Image size X/Y and Increment and voltages.")
            return

        self._scan_stop.clear()
        self._scan_thread = threading.Thread(
            target=self._scan_worker,
            args=(size_x, size_y, inc, x_fwd, x_bwd, y_fwd),
            daemon=True
        )
        self._scan_thread.start()

    def update_image(self):
        scan_corrected = self.scan_data_raw.copy()
        for i in range(scan_corrected.shape[0]):
            if i % 2 == 1:  # 奇数行（Python 从 0 开始，索引1,3,...）
                scan_corrected[i] = scan_corrected[i][::-1]  # 反转这一行

        # 将 self.scan_data 映射到 0~255
        min_val = np.nanmin(scan_corrected)
        max_val = np.nanmax(scan_corrected)
        norm_data = ((scan_corrected - min_val) / (max_val - min_val + 1e-9) * 255).astype(np.uint8)

        # 转成图像
        img = Image.fromarray(norm_data)
        self.save_img = img.copy()
        img = img.resize((200, 200))  # 可以调整显示大小
        img = ImageTk.PhotoImage(img)

        # 更新 label
        self.tk_img = img
        self.image_label.config(image=self.tk_img)

    def _scan_worker(self, size_x, size_y, inc, x_fwd, x_bwd, y_fwd):
        print(f"[Scan] Start: sizeX={size_x}, sizeY={size_y}, inc={inc:.4f}")
        self.scan_data_raw = np.zeros((size_y, size_x))
        for line_idx in range(size_y):
            if self._scan_stop.is_set():
                print("[Scan] Stopped by user.")
                return

            # 1) 配置 X 行扫描（正/反向交替）
            forward = (line_idx % 2 == 0)
            stp_x = x_fwd if forward else x_bwd
            move_cmd = "TRFWD000000" if forward else "TRBKD000000"

            # Setting up for X scan
            self.serial_manager.send_command("moving table", f"TRSTP{int(stp_x):06d}")
            self.serial_manager.send_command("moving table", "TRAMP100000")
            self.serial_manager.send_command("moving table", self._format_float_command("TRINC", inc))
            self.serial_manager.send_command("moving table", "TRSLX000000")

            for line_idy in range(size_x):
                self.serial_manager.send_command_wait_ok("moving table", move_cmd)
                time.sleep(0.001)
                self.scan_data_raw[line_idx, line_idy] = self.current_displacement
                self.update_image()

            # Setting up for Y scan
            self.serial_manager.send_command("moving table", f"TRSTP{int(y_fwd):06d}")
            self.serial_manager.send_command("moving table", "TRSLY000000")
            self.serial_manager.send_command_wait_ok("moving table", "TRFWD000000")


        print("[Scan] Finished.")


    def _format_float_command(self, cmd_prefix, value):
        integer_part = int(abs(value))
        decimal_part = int(round((abs(value) - integer_part) * 10000))
        param = f"{integer_part:02d}{decimal_part:04d}"
        return f"{cmd_prefix}{param}"