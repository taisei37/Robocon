import cv2
import numpy as np
from pyapriltags import Detector

# ---------- カメラ設定 ----------
DEVICE = 0  # 接続されているカメラ番号
cap = cv2.VideoCapture(DEVICE)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# ---------- AprilTag検出器 ----------
detector = Detector(families='tag36h11')

# ---------- ウィンドウ設定 ----------
cv2.namedWindow('AprilTag Detection', cv2.WINDOW_NORMAL)

# ---------- キャリブレーション結果 ----------
camera_matrix = np.array([
    [1194.08741, 0.0, 602.932566],
    [0.0, 1206.03102, 325.538922],
    [0.0, 0.0, 1.0]
])
dist_coeffs = np.array([0.04022942, 0.32673529, -0.00922231, -0.01283776, -0.89408179])

fx, fy = camera_matrix[0, 0], camera_matrix[1, 1]
cx, cy = camera_matrix[0, 2], camera_matrix[1, 2]

# ---------- タグサイズ ----------
tag_size = 0.06  # m

# ---------- 実行ループ ----------
while True:
    ret, frame = cap.read()
    if not ret:
        print("カメラから映像を取得できません")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    tags = detector.detect(gray)

    for tag in tags:
        corners = np.array(tag.corners, dtype=np.int32)

        # --- タグ面を半透明で塗る ---
        overlay = frame.copy()
        cv2.fillPoly(overlay, [corners], (0, 255, 0))  # 緑で塗り
        alpha = 0.3
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

        # --- タグ外枠 ---
        cv2.polylines(frame, [corners], True, (0,255,0), 2)

        # --- タグ内に格子線（3x3） ---
        for i in range(1, 3):
            # 縦線
            pt1 = tuple(np.int32(corners[0] + (corners[1]-corners[0])*i/3))
            pt2 = tuple(np.int32(corners[3] + (corners[2]-corners[3])*i/3))
            cv2.line(frame, pt1, pt2, (255,0,0), 1)
            # 横線
            pt1 = tuple(np.int32(corners[0] + (corners[3]-corners[0])*i/3))
            pt2 = tuple(np.int32(corners[1] + (corners[2]-corners[1])*i/3))
            cv2.line(frame, pt1, pt2, (255,0,0), 1)

        # --- 中心描画 ---
        center = tuple(map(int, tag.center))
        cv2.circle(frame, center, 5, (0,0,255), -1)
        cv2.putText(frame, f"ID:{tag.tag_id}", (center[0]+10, center[1]),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

        # --- 姿勢推定 ---
        obj_points = np.array([[-tag_size/2, -tag_size/2, 0],
                               [ tag_size/2, -tag_size/2, 0],
                               [ tag_size/2,  tag_size/2, 0],
                               [-tag_size/2,  tag_size/2, 0]], dtype=np.float32)
        img_points = np.array(tag.corners, dtype=np.float32)
        ret_pnp, rvec, tvec = cv2.solvePnP(obj_points, img_points,
                                           camera_matrix, dist_coeffs)
        if ret_pnp:
            R, _ = cv2.Rodrigues(rvec)
            sy = np.sqrt(R[0,0]**2 + R[1,0]**2)
            yaw   = np.arctan2(R[2,1], R[2,2]) * 180/np.pi
            pitch = np.arctan2(-R[2,0], sy) * 180/np.pi
            roll  = np.arctan2(R[1,0], R[0,0]) * 180/np.pi

            cv2.putText(frame, f"Yaw:{yaw:.1f}", (10,30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,0), 2)
            cv2.putText(frame, f"Pitch:{pitch:.1f}", (10,60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,0), 2)
            cv2.putText(frame, f"Roll:{roll:.1f}", (10,90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,0), 2)

    # --- ウィンドウ表示 ---
    cv2.imshow('AprilTag Detection', frame)

    # Escキーで終了
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()

