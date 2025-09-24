import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

# 读取 tiff 并转灰度
img = Image.open("input.tiff").convert("L")
Z = np.array(img, dtype=float)

# 创建网格
X, Y = np.meshgrid(np.arange(Z.shape[1]), np.arange(Z.shape[0]))

# 绘制 3D
fig = plt.figure()
ax = fig.add_subplot(111, projection="3d")
ax.plot_surface(X, Y, Z, cmap="gray")

plt.show()
