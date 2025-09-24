
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageSequence
import numpy as np
import os

# ---------------- Image processing core ---------------- #

def shift_rows_array(arr, target_rows='odd', direction='left', shift_px=0, origin_one_based=True):
    """
    Shift odd/even rows strictly by slicing, without modifying pixel values.
    """
    if shift_px <= 0:
        return arr.copy()

    H, W = arr.shape[:2]
    s = min(shift_px, W)

    # helper: 判断行是否目标行
    def is_target_row(i):
        if origin_one_based:
            return ((i + 1) % 2 == 1) if target_rows == 'odd' else ((i + 1) % 2 == 0)
        else:
            return (i % 2 == 1) if target_rows == 'odd' else (i % 2 == 0)

    out_rows = []
    for i in range(H):
        row = arr[i]
        if is_target_row(i):
            if direction == 'left':
                # 直接切片
                row_shifted = row[s:]
            else:  # right
                row_shifted = row[:-s]
        else:
            # 未移动的行
            if direction == 'left':
                row_shifted = row[:-s]
            else:
                row_shifted = row[s:]
        out_rows.append(row_shifted)

    return np.stack(out_rows, axis=0)

def pil_to_np(img):
    """Convert PIL Image to numpy array, preserving channels."""
    if img.mode in ['L', 'I;16', 'I']:
        return np.array(img)
    else:
        return np.array(img.convert('RGBA')) if img.mode not in ['RGB', 'RGBA'] else np.array(img)

def np_to_pil(arr, original_mode):
    """Convert numpy array back to PIL Image, trying to preserve original mode when possible."""
    if len(arr.shape) == 2:
        # Grayscale or 16-bit grayscale
        if original_mode == 'I;16' and arr.dtype != np.uint16:
            arr = arr.astype(np.uint16, copy=False)
        return Image.fromarray(arr)
    else:
        # Color
        if arr.shape[2] == 4:
            img = Image.fromarray(arr, 'RGBA')
            if original_mode == 'RGB':
                img = img.convert('RGB')
            return img
        elif arr.shape[2] == 3:
            return Image.fromarray(arr, 'RGB')
        else:
            # Unexpected channels; fall back to RGB
            return Image.fromarray(arr[:, :, :3], 'RGB')

def process_pil_page(img, target_rows, direction, shift_px, origin_one_based):
    arr = pil_to_np(img)
    shifted = shift_rows_array(arr, target_rows, direction, shift_px, origin_one_based)
    return np_to_pil(shifted, img.mode)

# ---------------- GUI ---------------- #

class RowShiftGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TIFF 行移位与裁切工具")
        self.geometry("1050x700")
        self.minsize(900, 600)

        self.original_frames = []  # list of PIL Images (pages)
        self.processed_frames = [] # list of PIL Images (pages) after processing
        self.preview_photo = None  # ImageTk.PhotoImage for preview
        self.current_preview_index = 0
        self.loaded_path = None

        self._build_widgets()

    def _build_widgets(self):
        # Controls panel
        ctrl_frame = ttk.Frame(self, padding=10)
        ctrl_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Load & info
        load_btn = ttk.Button(ctrl_frame, text="打开 TIFF...", command=self.load_tiff)
        load_btn.pack(fill=tk.X, pady=(0, 8))

        self.info_var = tk.StringVar(value="未加载图像")
        info_label = ttk.Label(ctrl_frame, textvariable=self.info_var, wraplength=260, justify='left')
        info_label.pack(fill=tk.X, pady=(0, 12))

        # Target rows
        ttk.Label(ctrl_frame, text="目标行：").pack(anchor='w')
        self.target_rows_var = tk.StringVar(value='odd')
        ttk.Radiobutton(ctrl_frame, text="奇数行", variable=self.target_rows_var, value='odd').pack(anchor='w')
        ttk.Radiobutton(ctrl_frame, text="偶数行", variable=self.target_rows_var, value='even').pack(anchor='w')

        # Direction
        ttk.Label(ctrl_frame, text="方向：").pack(anchor='w', pady=(8, 0))
        self.direction_var = tk.StringVar(value='left')
        ttk.Radiobutton(ctrl_frame, text="向左", variable=self.direction_var, value='left').pack(anchor='w')
        ttk.Radiobutton(ctrl_frame, text="向右", variable=self.direction_var, value='right').pack(anchor='w')

        # Shift amount
        ttk.Label(ctrl_frame, text="移动像素 (x)：").pack(anchor='w', pady=(8, 0))
        self.shift_var = tk.StringVar(value='10')
        shift_entry = ttk.Entry(ctrl_frame, textvariable=self.shift_var)
        shift_entry.pack(fill=tk.X)

        # Origin
        ttk.Label(ctrl_frame, text="行编号起点：").pack(anchor='w', pady=(8, 0))
        self.origin_var = tk.StringVar(value='1')
        origin_combo = ttk.Combobox(ctrl_frame, textvariable=self.origin_var, values=['0', '1'], state='readonly')
        origin_combo.pack(fill=tk.X)
        ttk.Label(ctrl_frame, text="说明：选择 1 表示第一行(顶行)视为第1行；选择 0 表示顶行为第0行。").pack(anchor='w', pady=(2, 8))

        # Page selector
        self.page_var = tk.IntVar(value=1)
        self.page_spin = ttk.Spinbox(ctrl_frame, from_=1, to=1, textvariable=self.page_var, width=8, command=self.on_page_change)
        ttk.Label(ctrl_frame, text="预览页码：").pack(anchor='w', pady=(8, 0))
        self.page_spin.pack(anchor='w')

        # Buttons
        preview_btn = ttk.Button(ctrl_frame, text="应用到预览页", command=self.apply_to_preview)
        preview_btn.pack(fill=tk.X, pady=(12, 4))

        proc_all_btn = ttk.Button(ctrl_frame, text="应用到所有页", command=self.apply_to_all)
        proc_all_btn.pack(fill=tk.X, pady=(4, 12))

        save_btn = ttk.Button(ctrl_frame, text="另存为 TIFF...", command=self.save_tiff)
        save_btn.pack(fill=tk.X)

        # Preview area
        right_frame = ttk.Frame(self, padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(right_frame, bg="#202225")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", lambda e: self.refresh_preview())

        # Status bar
        self.status_var = tk.StringVar(value="准备就绪")
        status = ttk.Label(self, textvariable=self.status_var, anchor='w')
        status.pack(side=tk.BOTTOM, fill=tk.X)

        # Style
        style = ttk.Style(self)
        try:
            self.tk.call("source", "sun-valley.tcl")
            style.theme_use("sun-valley-dark")
        except Exception:
            # Fallback to default
            pass

    # --------------- Helpers --------------- #

    def load_tiff(self):
        path = filedialog.askopenfilename(
            title="选择 TIFF 文件",
            filetypes=[("TIFF images", "*.tif *.tiff"), ("All files", "*.*")]
        )
        if not path:
            return

        try:
            img = Image.open(path)
            frames = [frame.copy() for frame in ImageSequence.Iterator(img)]
            img.close()

            if not frames:
                raise ValueError("无法读取任何页面")

            self.original_frames = frames
            self.processed_frames = [f.copy() for f in frames]
            self.loaded_path = path

            self.page_spin.config(to=len(frames))
            self.page_var.set(1)
            self.current_preview_index = 0

            w, h = self.original_frames[0].size
            mode = self.original_frames[0].mode
            self.info_var.set(f"已加载：{os.path.basename(path)}\n页数：{len(frames)}\n尺寸：{w}×{h}\n模式：{mode}")
            self.status_var.set("图像已加载")

            self.refresh_preview()
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件：{e}")

    def on_page_change(self):
        idx = int(self.page_var.get()) - 1
        idx = max(0, min(idx, len(self.processed_frames) - 1))
        self.current_preview_index = idx
        self.refresh_preview()

    def _get_params(self):
        # Validate and fetch parameters
        target_rows = self.target_rows_var.get()
        direction = self.direction_var.get()
        try:
            shift_px = int(self.shift_var.get())
            if shift_px < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("参数错误", "移动像素 (x) 必须是非负整数。")
            return None

        origin_one_based = (self.origin_var.get() == '1')
        return target_rows, direction, shift_px, origin_one_based

    def apply_to_preview(self):
        if not self.processed_frames:
            messagebox.showinfo("提示", "请先打开TIFF文件。")
            return

        params = self._get_params()
        if params is None:
            return
        target_rows, direction, shift_px, origin_one_based = params

        idx = self.current_preview_index
        try:
            self.status_var.set("处理中(预览页)...")
            self.update_idletasks()

            self.processed_frames[idx] = process_pil_page(
                self.original_frames[idx],
                target_rows, direction, shift_px, origin_one_based
            )
            self.status_var.set("预览页处理完成")
            self.refresh_preview()
        except Exception as e:
            messagebox.showerror("错误", f"处理失败：{e}")
            self.status_var.set("处理失败")

    def apply_to_all(self):
        if not self.processed_frames:
            messagebox.showinfo("提示", "请先打开TIFF文件。")
            return

        params = self._get_params()
        if params is None:
            return
        target_rows, direction, shift_px, origin_one_based = params

        try:
            self.status_var.set("处理中(所有页)...")
            self.update_idletasks()

            self.processed_frames = [
                process_pil_page(fr, target_rows, direction, shift_px, origin_one_based)
                for fr in self.original_frames
            ]
            self.status_var.set("全部页面处理完成")
            self.refresh_preview()
        except Exception as e:
            messagebox.showerror("错误", f"处理失败：{e}")
            self.status_var.set("处理失败")

    def refresh_preview(self):
        if not self.processed_frames:
            self.canvas.delete("all")
            return

        img = self.processed_frames[self.current_preview_index]

        # Fit image into canvas while preserving aspect ratio
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        if cw < 10 or ch < 10:
            return

        iw, ih = img.size
        scale = min(cw / iw, ch / ih)
        new_w = max(1, int(iw * scale))
        new_h = max(1, int(ih * scale))

        disp = img.resize((new_w, new_h), Image.NEAREST)
        self.preview_photo = ImageTk.PhotoImage(disp)

        self.canvas.delete("all")
        self.canvas.create_image(cw // 2, ch // 2, image=self.preview_photo, anchor="center")

        self.canvas.create_text(
            10, 10,
            text=f"预览 第 {self.current_preview_index+1}/{len(self.processed_frames)} 页  显示尺寸: {new_w}×{new_h}",
            anchor="nw",
            fill="#DDDDDD",
            font=("Arial", 10)
        )

    def save_tiff(self):
        if not self.processed_frames:
            messagebox.showinfo("提示", "没有可保存的页面，请先处理图像。")
            return

        save_path = filedialog.asksaveasfilename(
            title="另存为",
            defaultextension=".tif",
            filetypes=[("TIFF image", "*.tif *.tiff")]
        )
        if not save_path:
            return

        try:
            first = self.processed_frames[0]
            extra = self.processed_frames[1:] if len(self.processed_frames) > 1 else []
            save_params = {}
            # Preserve basic metadata when possible
            if "dpi" in first.info:
                save_params["dpi"] = first.info["dpi"]

            first.save(
                save_path,
                save_all=bool(extra),
                append_images=extra,
                compression="tiff_deflate",
                **save_params
            )
            self.status_var.set(f"已保存：{os.path.basename(save_path)}")
            messagebox.showinfo("完成", f"文件已保存：\n{save_path}")
        except Exception as e:
            messagebox.showerror("错误", f"保存失败：{e}")

def main():
    app = RowShiftGUI()
    app.mainloop()

if __name__ == "__main__":
    main()
