import matplotlib
matplotlib.use('TkAgg')
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from pyapriltags import Detector
from scipy.spatial.transform import Rotation as R

# --- カメラパラメータ ---
fx, fy = 600, 600
cx, cy = 320, 240
camera_params = (fx, fy, cx, cy)
tag_size = 0.095  # [m]

# --- フィールドサイズ（mm） ---
FIELD_W, FIELD_H = 500.0, 500.0  # フィールド全体

# --- 外部カメラの位置と姿勢 ---
cam_pos_field = np.array([0.25, 0.60, 0.75])  # m単位: X, Y, Z
cam_euler = np.deg2rad([0, -60, 0])          # 下向き45°俯瞰
cam_R = R.from_euler('xyz', cam_euler).as_matrix()

# --- カメラ座標 → フィールド座標 ---
def camera_to_field(tag_t_cam, cam_pos_field, cam_R):
    # カメラ座標系 → フィールド座標系
    return cam_R @ tag_t_cam + cam_pos_field

# --- フィールド座標 → マップ座標（0〜FIELD_W,H mm） ---
def field_to_map(xy_field):
    x_map = (xy_field[0] * 1000)  # m → mm
    y_map = (xy_field[1] * 1000)
    return x_map, y_map

# --- Field Map描画 ---
def draw_field(ax):
    vertices = [(0,0), (FIELD_W,0), (FIELD_W,FIELD_H), (0,FIELD_H)]
    ax.add_patch(Polygon(vertices, closed=True, fill=False, edgecolor='black', linewidth=2))
    ax.set_xlim(0, FIELD_W)
    ax.set_ylim(0, FIELD_H)
    ax.set_aspect('equal')
    ax.set_xlabel("X [mm]")
    ax.set_ylabel("Y [mm]")
    plt.gca().invert_yaxis()
    ax.set_title("Field Map")

# --- Apriltag検出 ---
detector = Detector(families='tag36h11')
cap = cv2.VideoCapture(4)
if not cap.isOpened():
    raise RuntimeError("カメラを開けませんでした")

# --- 描画用 Figure ---
plt.ion()
fig_cam = plt.figure("Camera View")
fig_map = plt.figure("Field Map")

# --- Escキーで終了 ---
stop_flag = {"stop": False}
def on_key(event):
    if event.key == 'escape':
        stop_flag["stop"] = True
fig_cam.canvas.mpl_connect('key_press_event', on_key)
fig_map.canvas.mpl_connect('key_press_event', on_key)

# --- メインループ ---
while True:
    ret, img = cap.read()
    if not ret or stop_flag["stop"]:
        break

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    tags = detector.detect(gray, estimate_tag_pose=True, camera_params=camera_params, tag_size=tag_size)

    # --- Camera View ---
    plt.figure("Camera View")
    plt.clf()
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    for tag in tags:
        corners = tag.corners.astype(int)
        for i in range(4):
            pt1 = tuple(corners[i])
            pt2 = tuple(corners[(i+1)%4])
            cv2.line(img_rgb, pt1, pt2, (0,255,0), 2)
        cv2.putText(img_rgb, f"ID {tag.tag_id}", tuple(corners[0]-[0,5]),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 2)
    plt.imshow(img_rgb)
    plt.axis("off")
    plt.title("Camera View")

    # --- Field Map ---
    plt.figure("Field Map")
    plt.clf()
    ax = plt.gca()
    draw_field(ax)

    for tag in tags:
        if tag.pose_t is not None:
            field_pos = camera_to_field(tag.pose_t.flatten(), cam_pos_field, cam_R)
            x_map, y_map = field_to_map(field_pos)

            # マップ範囲内だけ描画
            if 0 <= x_map <= FIELD_W and 0 <= y_map <= FIELD_H:
                ax.plot(x_map, y_map, "ro")
                ax.text(x_map+5, y_map+5, f"ID {tag.tag_id}", fontsize=6, color='red')

            # ターミナル出力（マップ外でも出力）
            print(f"Tag ID {tag.tag_id}: Field X={x_map:.1f} mm, Y={y_map:.1f} mm")

    plt.pause(0.05)

cap.release()
plt.ioff()
plt.close()
