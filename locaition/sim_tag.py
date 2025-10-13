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
tag_size = 0.05  # [m] 実際のタグサイズに合わせて

# --- フィールド図描画関数 ---
def draw_field(ax):
    FIELD_W, FIELD_H = 2065.0, 2300.0
    field_vertices = [ (265, 0), (2065, 0), (2065, 1800), (265, 1800) ]
    central_block_vertices = [ (865, 500), (1165, 500), (1165, 1400), (865, 1400) ]
    goal_boxes = [
        {"x": 265.0-265.0, "y": 100.0,  "w": 265.0, "h": 300.0, "color": "blue"},
        {"x": 265.0-265.0, "y": 750.0,  "w": 265.0, "h": 300.0, "color": "yellow"},
        {"x": 265.0-265.0, "y": 1400.0, "w": 265.0, "h": 300.0, "color": "red"},
        {"x": 265.0, "y": 1800, "w": 500.0, "h": 500.0, "color": "none"}
    ]
    # 外枠
    polygon = Polygon(field_vertices, closed=True, fill=False, edgecolor="black", linewidth=2)
    ax.add_patch(polygon)
    # 中央ブロック
    polygon = Polygon(central_block_vertices, closed=True, facecolor='lightgray', edgecolor='black', linewidth=1.0)
    ax.add_patch(polygon)
    # ゴール箱
    for g in goal_boxes:
        ax.add_patch(Rectangle((g["x"], g["y"]), g["w"], g["h"], fill=(g["color"]!="none"), facecolor=(g["color"] if g["color"]!="none" else "none"), edgecolor='black', linewidth=2))
    # ガイドライン
    ax.add_line(mlines.Line2D([565, 565], [400, 1550], color="black", linewidth=4))
    ax.add_line(mlines.Line2D([1605, 1605], [400, 1800], color="black", linewidth=4))
    ax.add_line(mlines.Line2D([715, 1455], [250, 250], color="black", linewidth=4))
    arc1 = Arc((715, 400), 300, 300, theta1=180, theta2=270, color="black", linewidth=4)
    ax.add_patch(arc1)
    arc2 = Arc((1455, 400), 300, 300, theta1=270, theta2=360, color="black", linewidth=4)
    ax.add_patch(arc2)
    ax.add_line(mlines.Line2D([1455, 1755],[500,500],  color="black", linewidth=4))
    ax.add_line(mlines.Line2D([415, 715], [900, 900], color="black", linewidth=4))
    ax.add_line(mlines.Line2D([415, 715], [1560, 1560], color="black", linewidth=4))
    ax.add_line(mlines.Line2D([1455, 1755], [1750, 1750], color="black", linewidth=4))
    ax.add_line(mlines.Line2D([315, 315], [100, 400], color="black", linewidth=4))
    ax.add_line(mlines.Line2D([315, 315], [750, 1050], color="black", linewidth=4))
    ax.add_line(mlines.Line2D([315, 315], [1400, 1700], color="black", linewidth=4))
    ax.add_line(mlines.Line2D([865, 865], [100, 400], color="black", linewidth=4))
    ax.set_xlim(-100, FIELD_W + 100)
    ax.set_ylim(-100, FIELD_H + 100)
    ax.set_aspect('equal')
    ax.set_xlabel("X [mm]", fontsize=12)
    ax.set_ylabel("Y [mm]", fontsize=12)
    ax.tick_params(axis='both', which='major', labelsize=10)
    ax.xaxis.set_label_position('top')
    ax.xaxis.tick_top()
    ax.set_xticks([0, 265, 565, 865, 1145, 1605, 2065])
    ax.set_yticks([0, 250, 900, 1550, 1800, 2300])
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
            # フィールド座標系に変換（例: 1m=1000mm, 原点調整など必要に応じて）
            x_mm = t[0]*1000 + 1000  # 仮: フィールド中心を(1000,1000)に
            y_mm = t[2]*1000 + 1150  # 仮: Z軸をYに
            ax_map.plot(x_mm, y_mm, "ro")
            ax_map.text(x_mm+20, y_mm+20, f"ID {tag.tag_id}", fontsize=10)

ani = FuncAnimation(fig, update, interval=100)
plt.show()
