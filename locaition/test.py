import cv2
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

# 白い画像を作成
img = 255 * np.ones((200, 200, 3), np.uint8)

# OpenCVのBGRをRGBに変換して表示
plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
plt.title("Matplotlib Display Test")
plt.axis("off")
plt.show()

