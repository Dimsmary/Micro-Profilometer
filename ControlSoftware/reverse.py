import os
import numpy as np
from PIL import Image

# 输入和输出文件夹
input_folder = "TIFF"
output_folder = "TIFF_OUT"
os.makedirs(output_folder, exist_ok=True)

# 遍历文件夹中的tiff文件
for filename in os.listdir(input_folder):
    if filename.lower().endswith(".tiff") or filename.lower().endswith(".tif"):
        filepath = os.path.join(input_folder, filename)

        # 读取tiff为数组
        img = Image.open(filepath)
        arr = np.array(img)

        # 找到最大值
        max_val = arr.max()

        # 灰度反转操作：x' = max - x
        arr_new = max_val - arr

        # 保存为tiff
        outpath = os.path.join(output_folder, filename)
        Image.fromarray(arr_new.astype(arr.dtype)).save(outpath)

        print(f"Processed: {filename}")
