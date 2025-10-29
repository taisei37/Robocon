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
FIELD_W, FIELD_H = 500.0, 500.0

# --- カメラ位置と姿勢（フィールド座標系[m]）---
cam_pos_field = np.array([0, 0, 0.80])  # m単位
cam_euler = np.deg2rad([0, -70, 0])           # ピッチ （下向き）
cam_R = R.from_euler('xyz', cam_euler).as_matrix()

# --- カメラ座標 → フィールド座標 ---
def camera_to_field(tag_t_cam, cam_pos_field, cam_R):
    # 転置を使ってカメラ→フィールド座標変換
    
    tag_field_pos = cam_R.T @ tag_t_cam + cam_pos_field
    return tag_field_pos
# 投影変換
def estimate_position(circle, h, r, theta):
    x_i, y_i = circle[0][0], circle[0][1]
    
    tan0 = np.tan(np.radians(20))
    tan1 = (cy - y_i) / fy
    yw  = (800 - r) * (tan0 + tan1) / (1 - tan0 * tan1)
    hypo = np.sqrt((800-r) ** 2 + yw ** 2)
    xw = ((x_i - cx) * hypo) / fx
    return xw, yw


# --- フィールド描画 ---
def draw_field(ax):
    vertices = [(-FIELD_W / 2 ,0), (FIELD_W / 2,0), (FIELD_W / 2,FIELD_H), (-FIELD_W / 2,FIELD_H)]
    ax.add_patch(Polygon(vertices, closed=True, fill=False, edgecolor='black', linewidth=2))
    ax.set_xlim(-FIELD_W / 2, FIELD_W / 2)
    ax.set_ylim(0, FIELD_H)
    ax.set_aspect('equal')
    ax.set_xlabel("X [mm]")
    ax.set_ylabel("Y [mm]")
    ax.set_title("Field Map")

# --- Apriltag検出 ---
detector = Detector(families='tag36h11')
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("カメラを開けませんでした")

# --- 描画ウィンドウ設定 ---
plt.ion()
fig_cam = plt.figure("Camera View")
fig_map = plt.figure("Field Map")

# --- Escで終了 ---
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
    centers = [tag.center for tag in tags]
    #print(centers)
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
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,0,0), 2)
    plt.imshow(img_rgb)
    plt.axis("off")
    plt.title("Camera View")

    # --- Field Map ---
    plt.figure("Field Map")
    plt.clf()
    ax = plt.gca()
    draw_field(ax)

    # カメラ位置をマップに表示
    ax.plot(cam_pos_field[0]*1000, cam_pos_field[1]*1000, "bo", label="Camera")
    ax.legend()
#cam_pos_field = np.array([-0.25, 0.25, 0.80])  # m単位
    for tag in tags:
        if tag.pose_t is not None:
            #tag_field_pos = camera_to_field(centers, cam_pos_field, cam_R)
            tag_field_pos = estimate_position(centers, cam_pos_field[2], 1.0, np.deg2rad(80))
            x_mm, y_mm = (tag_field_pos[0] - cam_pos_field[0]), (tag_field_pos[1] - cam_pos_field[1])

            # マップ範囲に関係なく描画
            ax.plot(x_mm, y_mm, "ro")
            ax.text(x_mm+5, y_mm+5, f"ID {tag.tag_id}", fontsize=6, color='red')

            # ターミナル出力
            print(f"Tag ID {tag.tag_id}: Field X={x_mm:.1f} mm, Y={y_mm:.1f} mm")

    plt.pause(0.1)

cap.release()
plt.ioff()
plt.close()
