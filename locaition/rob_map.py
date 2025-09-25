import cv2
import numpy as np
from math import radians, cos, sin
from pyapriltags import Detector
import matplotlib.pyplot as plt

# -------------------- フィールド設定 --------------------
FIELD_W = 1800.0  # mm
FIELD_H = 1800.0  # mm

# カメラパラメータ（キャリブレーション結果を入れてください）
K = np.array([
    [1400.0, 0.0, 640.0],
    [0.0, 1400.0, 360.0],
    [0.0, 0.0, 1.0]
], dtype=np.float64)
dist = np.zeros(5, dtype=np.float64)

# カメラ位置と姿勢
cam_pos = np.array([900.0, 900.0, 900.0], dtype=np.float64)  # 中央上空900mm
pitch_deg, yaw_deg, roll_deg = -90.0, 0.0, 0.0
# -------------------------------------------------------

def euler_to_R(pitch, yaw, roll):
    cp, sp = cos(pitch), sin(pitch)
    cy, sy = cos(yaw), sin(yaw)
    cr, sr = cos(roll), sin(roll)
    Rz = np.array([[cy, -sy, 0],[sy, cy, 0],[0,0,1]])
    Ry = np.array([[cp, 0, sp],[0,1,0],[-sp,0,cp]])
    Rx = np.array([[1,0,0],[0,cr,-sr],[0,sr,cr]])
    return Rz @ Ry @ Rx

pitch = radians(pitch_deg); yaw = radians(yaw_deg); roll = radians(roll_deg)
R_cam_to_world = euler_to_R(pitch, yaw, roll)
R_world_to_cam = R_cam_to_world.T
rvec, _ = cv2.Rodrigues(R_world_to_cam)
tvec = -R_world_to_cam @ cam_pos.reshape(3,1)

# フィールド四隅
field_corners_world = np.array([
    [0.0, 0.0, 0.0],
    [FIELD_W, 0.0, 0.0],
    [FIELD_W, FIELD_H, 0.0],
    [0.0, FIELD_H, 0.0]
], dtype=np.float64)

# Apriltag detector
detector = Detector(families='tag36h11')

# カメラ起動
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("カメラを開けませんでした")

# ---- 鳥瞰図用の描画準備 ----
plt.ion()
fig, ax = plt.subplots()
ax.set_xlim(0, FIELD_W)
ax.set_ylim(0, FIELD_H)
ax.set_aspect('equal')
ax.set_title("Field Top View (mm)")
field_outline = plt.Rectangle((0,0), FIELD_W, FIELD_H, fill=False, color="red")
ax.add_patch(field_outline)
points_plot, = ax.plot([], [], 'go')  # タグ座標の点
plt.show()

def update_topview(xs, ys):
    points_plot.set_data(xs, ys)
    fig.canvas.draw()
    fig.canvas.flush_events()

while True:
    ret, frame = cap.read()
    if not ret: break

    # フィールド枠を画像に描画
    img_pts, _ = cv2.projectPoints(field_corners_world, rvec, tvec, K, dist)
    img_pts = img_pts.reshape(-1,2).astype(int)
    cv2.polylines(frame, [img_pts], True, (0,0,255), 2)

    # Apriltag検出
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    detections = detector.detect(gray)
    tag_xs, tag_ys = [], []

    for det in detections:
        u,v = det.center
        cv2.circle(frame, (int(u),int(v)), 6, (0,255,0), -1)

        pts = np.array([[[u,v]]], dtype=np.float64)
        undist = cv2.undistortPoints(pts, K, dist, P=K)
        x_und, y_und = undist[0,0,0], undist[0,0,1]
        uv1 = np.array([x_und, y_und, 1.0])

        dir_cam = np.linalg.inv(K) @ uv1
        dir_world = R_cam_to_world @ dir_cam
        if abs(dir_world[2]) < 1e-6: continue
        s = (0 - cam_pos[2]) / dir_world[2]
        Pw = cam_pos + s * dir_world
        Xw,Yw,_ = Pw
        tag_xs.append(Xw); tag_ys.append(Yw)

        label = f"ID{det.tag_id}: {int(Xw)},{int(Yw)}"
        cv2.putText(frame, label, (int(u)+6,int(v)-6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0),1, cv2.LINE_AA)

    # 鳥瞰図更新
    update_topview(tag_xs, tag_ys)

    cv2.imshow("camera", frame)
    if cv2.waitKey(1) & 0xFF == 27: break

cap.release()
cv2.destroyAllWindows()

