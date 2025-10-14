import matplotlib
matplotlib.use('TkAgg')
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle, Polygon, Arc
import matplotlib.lines as mlines
from pyapriltags import Detector

# --- カメラパラメータ（要調整） ---
fx, fy = 600, 600
cx, cy = 320, 240
camera_params = (fx, fy, cx, cy)
tag_size = 0.075  # [m] 実際のタグサイズに合わせて

# --- フィールド図描画関数 ---
def draw_field(ax):
    FIELD_W, FIELD_H = 1000.0, 1000.0
    # 外枠（左上原点, 時計回り）
    field_vertices = [ (0,0), (1000,0), (1000,1000), (0,1000) ]
    polygon = Polygon(field_vertices, closed=True, fill=False, edgecolor="black", linewidth=2)
    ax.add_patch(polygon)
    # ガイドライン
    ax.set_xlim(-100, FIELD_W + 100)
    ax.set_ylim(-100, FIELD_H + 100)
    ax.set_aspect('equal')
    ax.set_xlabel("X [mm]", fontsize=12)
    ax.set_ylabel("Y [mm]", fontsize=12)
    ax.tick_params(axis='both', which='major', labelsize=10)
    ax.xaxis.set_label_position('top')
    ax.xaxis.tick_top()
    ax.set_xticks([0 , 250, 500 ,750 ,1000] )
    ax.set_yticks([0 , 250, 500 ,750 ,1000])
    plt.gca().invert_yaxis()
    ax.set_title("Field Map")

# --- AprilTag検出器 ---
detector = Detector(families='tag36h11')
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("カメラを開けませんでした")

fig, (ax_cam, ax_map) = plt.subplots(1, 2, figsize=(18, 9), gridspec_kw={'width_ratios': [1, 2]})
ax_cam.set_title("Camera")
ax_map.set_title("Field Map")

# --- メイン更新関数 ---
def update(frame):
    ret, img = cap.read()
    if not ret:
        return
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    tags = detector.detect(gray, estimate_tag_pose=True, camera_params=camera_params, tag_size=tag_size)
    # カメラ画像描画
    ax_cam.clear()
    ax_cam.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    ax_cam.axis("off")
    ax_cam.set_title("Camera")
    # フィールド図描画
    ax_map.clear()
    draw_field(ax_map)
    # タグ位置をフィールド座標で描画
    for tag in tags:
        if tag.pose_t is not None:
            t = tag.pose_t.flatten()  # [m]
            # フィールド中心(500,500)を原点とし、1m=1000mm換算
            x_mm = t[0]*1000 + 500  # X方向
            y_mm = t[2]*1000 + 500  # Z方向をYに
            ax_map.plot(x_mm, y_mm, "ro")
            ax_map.text(x_mm+20, y_mm+20, f"ID {tag.tag_id}", fontsize=10)

ani = FuncAnimation(fig, update, interval=100)
plt.show()

