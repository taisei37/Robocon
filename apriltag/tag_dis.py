import cv2
from pyapriltags import Detector
import numpy as np

# ---------- カメラ設定 ----------
DEVICE = 0
cap = cv2.VideoCapture(DEVICE)

if not cap.isOpened():
    print(f"カメラ {DEVICE} を開けません")
    exit()

# ---------- 最新キャリブレーション結果 ----------
camera_matrix = np.array([
    [1194.08741, 0.0, 602.932566],
    [0.0, 1206.03102, 325.538922],
    [0.0, 0.0, 1.0]
])
dist_coeffs = np.array([0.04022942, 0.32673529, -0.00922231, -0.01283776, -0.89408179])

fx, fy = camera_matrix[0, 0], camera_matrix[1, 1]
cx, cy = camera_matrix[0, 2], camera_matrix[1, 2]
camera_params = (fx, fy, cx, cy)

# ---------- Apriltag 設定 ----------
tag_size = 0.06  # [m]
detector = Detector(families='tag36h11')

cv2.namedWindow('AprilTag Detection', cv2.WINDOW_NORMAL)

# タグ描画色（共通）
tag_color = (0, 255, 0)  # 緑

# 複数フレームで平均化するためのリスト
distance_list = []

# 距離補正係数（実測距離 / 推定距離）
correction_factor = 0.6667

while True:
    ret, frame = cap.read()
    if not ret:
        print("カメラから映像を取得できません")
        break

    # ---------- 歪み補正 ----------
    frame_undistorted = cv2.undistort(frame, camera_matrix, dist_coeffs)
    gray = cv2.cvtColor(frame_undistorted, cv2.COLOR_BGR2GRAY)

    # タグ検出
    tags = detector.detect(gray, estimate_tag_pose=True,
                           camera_params=camera_params,
                           tag_size=tag_size)

    if tags:
        for tag in tags:
            # 並進ベクトルからZ距離を取得し補正
            if tag.pose_t is not None:
                t = tag.pose_t.flatten()
                z = t[2]  # 推定距離
                z_corrected = z * correction_factor  # 補正後距離

                # 複数フレーム平均（直近5フレーム）
                distance_list.append(z_corrected)
                if len(distance_list) > 5:
                    distance_list.pop(0)
                z_avg = np.mean(distance_list)

                # 画面に距離を描画
                center = tuple(map(int, tag.center))
                cv2.putText(frame_undistorted, f"{z_avg:.2f} m",
                            (center[0]+10, center[1]-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, tag_color, 2)

            # タグ枠を描画（共通色）
            corners = tag.corners
            for i in range(4):
                pt1 = tuple(map(int, corners[i]))
                pt2 = tuple(map(int, corners[(i + 1) % 4]))
                cv2.line(frame_undistorted, pt1, pt2, tag_color, 2)

    # ---------- 表示 ----------
    cv2.imshow('AprilTag Detection', frame_undistorted)

    # ESCキーで終了
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()

