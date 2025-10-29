import cv2
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from pyapriltags import Detector
from scipy.spatial.transform import Rotation as R

# -----------------------------
# 座標変換クラス
# -----------------------------
class SimpleTF:
    def __init__(self):
        self.transforms = {}
    def set_transform(self, from_frame, to_frame, R_mat, t_vec):
        self.transforms[f"{from_frame}->{to_frame}"] = {'R': R_mat, 't': t_vec}
    def transform_point(self, from_frame, to_frame, point):
        tf = self.transforms[f"{from_frame}->{to_frame}"]
        return (tf['R'] @ np.array(point).reshape(3,1) + tf['t'].reshape(3,1)).flatten()

# -----------------------------
# フィールド描画関数
# -----------------------------
FIELD_W, FIELD_H = 500.0, 500.0  # mm

def draw_field(ax):
    ax.add_patch(Polygon([(0,0),(FIELD_W,0),(FIELD_W,FIELD_H),(0,FIELD_H)], 
                         closed=True, fill=False, edgecolor='black', linewidth=2))
    ax.set_xlim(-50, FIELD_W+50)
    ax.set_ylim(-50, FIELD_H+50)
    ax.set_aspect('equal')
    ax.set_xlabel("X [mm]")
    ax.set_ylabel("Y [mm]")
    plt.gca().invert_yaxis()
    ax.set_title("Field Map")

# -----------------------------
# カメラパラメータ
# -----------------------------
camera_matrix = np.array([
    [1194.08741, 0.0, 602.932566],
    [0.0, 1206.03102, 325.538922],
    [0.0, 0.0, 1.0]
])
dist_coeffs = np.array([0.04022942, 0.32673529, -0.00922231, -0.01283776, -0.89408179])
fx, fy = camera_matrix[0,0], camera_matrix[1,1]
cx, cy = camera_matrix[0,2], camera_matrix[1,2]
camera_params = (fx, fy, cx, cy)
tag_size = 0.095  # m

# -----------------------------
# カメラ → フィールド変換
# -----------------------------
tf = SimpleTF()

# カメラの角度：cam_to_field_R　
# カメラの位置：cam_to_field_t　（ｘ，ｙ，ｚ）
cam_to_field_R = R.from_euler('xyz', [0, -70, 0], degrees=True).as_matrix()
cam_to_field_t = np.array([0.25, 0, 0.79])  # [m]

tf.set_transform('camera_link', 'field', cam_to_field_R, cam_to_field_t)

# -----------------------------
# Apriltag Detector
# -----------------------------
detector = Detector(families='tag36h11')

# -----------------------------
# カメラ設定
# -----------------------------
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("カメラを開けませんでした")

# -----------------------------
# 描画設定
# -----------------------------
plt.ion()
fig_cam = plt.figure("Camera View", figsize=(6,4))
fig_map = plt.figure("Field Map", figsize=(5,5))
stop_flag = {"stop": False}

def on_key(event):
    if event.key == 'escape':
        stop_flag["stop"] = True
fig_cam.canvas.mpl_connect('key_press_event', on_key)
fig_map.canvas.mpl_connect('key_press_event', on_key)

# -----------------------------
# メインループ
# -----------------------------
while True:
    ret, img = cap.read()
    if not ret or stop_flag["stop"]:
        break

    # 歪み補正
    h, w = img.shape[:2]
    new_cam_mtx, _ = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coeffs, (w,h), 1)
    undistorted = cv2.undistort(img, camera_matrix, dist_coeffs, None, new_cam_mtx)

    gray = cv2.cvtColor(undistorted, cv2.COLOR_BGR2GRAY)
    tags = detector.detect(gray, estimate_tag_pose=True, camera_params=camera_params, tag_size=tag_size)

    # Camera View
    plt.figure("Camera View"); plt.clf()
    img_rgb = cv2.cvtColor(undistorted, cv2.COLOR_BGR2RGB)
    for tag in tags:
        corners = tag.corners.astype(int)
        for i in range(4):
            cv2.line(img_rgb, tuple(corners[i]), tuple(corners[(i+1)%4]), (0,255,0), 2)
        cv2.putText(img_rgb, f"ID {tag.tag_id}", tuple(corners[0]-[0,5]), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,0,0), 2)
    plt.imshow(img_rgb); plt.axis("off"); plt.title("Camera View")

    # Field Map
    plt.figure("Field Map"); plt.clf(); ax = plt.gca()
    draw_field(ax)

    for tag in tags:
        if tag.pose_t is not None:
            tag_field = tf.transform_point('camera_link', 'field', tag.pose_t.flatten())
            x_mm, y_mm = tag_field[0]*1000, tag_field[1]*1000
            if 0 <= x_mm <= FIELD_W and 0 <= y_mm <= FIELD_H:
                ax.plot(x_mm, y_mm, "ro")
                ax.text(x_mm+5, y_mm+5, f"ID {tag.tag_id}", fontsize=6, color='red')

    plt.pause(0.03)

cap.release()
plt.ioff()
plt.close('all')
