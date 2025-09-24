import numpy as np
import tifffile as tiff

def shift_rows_array(arr, target_rows='odd', direction='left', shift_px=0, origin_one_based=True):
    """
    arr: numpy array, shape (H, W) or (H, W, C)
    target_rows: 'odd' 或 'even'
    direction: 'left' 或 'right'
    shift_px: 平移像素数
    origin_one_based: True 表示第一行是1行(奇数)，False 表示顶行是0行
    """
    if shift_px <= 0:
        return arr.copy()

    H, W = arr.shape[:2]
    s = min(shift_px, W)

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
                row_shifted = row[s:]
            else:  # right
                row_shifted = row[:-s]
        else:
            # 未移动的行也要裁剪保持对齐
            if direction == 'left':
                row_shifted = row[:-s]
            else:
                row_shifted = row[s:]
        out_rows.append(row_shifted)

    return np.stack(out_rows, axis=0)

if __name__ == "__main__":
    infile = "input.tiff"
    outfile = "output.tiff"

    # 读取原始 tiff
    arr = tiff.imread(infile)

    # 参数设置
    shifted = shift_rows_array(
        arr,
        target_rows='odd',      # 'odd' 或 'even'
        direction='right',       # 'left' 或 'right'
        shift_px=8,            # 移动的像素数
        origin_one_based=True   # True: 顶行为第1行，False: 顶行为第0行
    )

    # 保存为新 tiff
    tiff.imwrite(outfile, shifted)
    print(f"保存完成: {outfile}")
