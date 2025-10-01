import cv2
from pyapriltags import Detector
import numpy as np

# カメラ起動
cap = cv2.VideoCapture(0)

# --- カメラ内部パラメータ（仮の値） ---
fx, fy = 600, 600
cx, cy = 320, 240
camera_params = (fx, fy, cx, cy)

# タグの一辺の長さ [m]
tag_size = 0.05

# Apriltag ディテクタ作成
detector = Detector(families='tag36h11')

cv2.namedWindow('AprilTag Detection', cv2.WINDOW_NORMAL)

while True:
    ret, frame = cap.read()
    if not ret:
        print("カメラから映像を取得できません")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    tags = detector.detect(gray, estimate_tag_pose=True,
                           camera_params=camera_params,
                           tag_size=tag_size)

    if tags:
        for tag in tags:
            if tag.pose_t is not None:
                # 並進ベクトル（カメラ座標系での位置）
                t = tag.pose_t.flatten()
                z = t[2]   # Z方向の距離 [m]

                print(f"[Tag ID: {tag.tag_id}] Z方向の距離: {z:.3f} m")

                # 画面に描画
                center = tuple(map(int, tag.center))
                cv2.putText(frame, f"{z:.2f} m",
                            (center[0]+10, center[1]-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                            (0, 255, 255), 2)

            # タグ枠を描画
            corners = tag.corners
            for i in range(4):
                pt1 = tuple(map(int, corners[i]))
                pt2 = tuple(map(int, corners[(i + 1) % 4]))
                cv2.line(frame, pt1, pt2, (0, 255, 0), 2)

    cv2.imshow('AprilTag Detection', frame)
    if cv2.waitKey(1) & 0xFF == 27:  # Escキーで終了
        break

cap.release()
cv2.destroyAllWindows()

