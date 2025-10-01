import cv2
from pyapriltags import Detector
import numpy as np

# カメラ起動
cap = cv2.VideoCapture(0)

# --- カメラ内部パラメータ（仮の例） ---
# fx, fy: 焦点距離（画素単位）
# cx, cy: 画像中心座標（画素単位）
fx = 600
fy = 600
cx = 320
cy = 240
camera_params = (fx, fy, cx, cy)

# タグの実際の一辺の長さ [m]（例: 5cm = 0.05m）
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
        print(f"=== Detected {len(tags)} AprilTags ===")
        for tag in tags:
            # タグのIDと中心座標
            print(f"[Tag ID: {tag.tag_id}] Center: {tag.center}")
            print(f"Corners: {tag.corners}")

            if tag.pose_R is not None:
                # 回転行列 R, 並進ベクトル t
                R = tag.pose_R
                t = tag.pose_t

                # ロール・ピッチ・ヨーに変換
                rvec, _ = cv2.Rodrigues(R)
                roll, pitch, yaw = rvec.flatten()

                print(f"Translation (x,y,z): {t.flatten()}")
                print(f"Rotation (roll,pitch,yaw): {roll:.3f}, {pitch:.3f}, {yaw:.3f}")

    # 検出結果を描画
    for tag in tags:
        corners = tag.corners
        for i in range(4):
            pt1 = tuple(map(int, corners[i]))
            pt2 = tuple(map(int, corners[(i + 1) % 4]))
            cv2.line(frame, pt1, pt2, (0, 255, 0), 2)
        center = tuple(map(int, tag.center))
        cv2.putText(frame, str(tag.tag_id), center,
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # 姿勢ベクトルが得られていればカメラ座標系の軸を描画
        if tag.pose_R is not None:
            R = tag.pose_R
            t = tag.pose_t
            axis_len = 0.03  # 3cmの軸を描画

            # 3D座標軸を2Dに投影
            axis_points = np.float32([
                [0, 0, 0],
                [axis_len, 0, 0],
                [0, axis_len, 0],
                [0, 0, axis_len]
            ])
            axis_img, _ = cv2.projectPoints(axis_points, cv2.Rodrigues(R)[0], t,
                                            np.array([[fx, 0, cx],
                                                      [0, fy, cy],
                                                      [0, 0, 1]]), None)

            axis_img = axis_img.reshape(-1, 2).astype(int)
            origin = tuple(axis_img[0])

            cv2.line(frame, origin, tuple(axis_img[1]), (0, 0, 255), 2)  # X: 赤
            cv2.line(frame, origin, tuple(axis_img[2]), (0, 255, 0), 2)  # Y: 緑
            cv2.line(frame, origin, tuple(axis_img[3]), (255, 0, 0), 2)  # Z: 青

    cv2.imshow('AprilTag Detection', frame)
    if cv2.waitKey(1) & 0xFF == 27:  # Escキーで終了
        break

cap.release()
cv2.destroyAllWindows()

