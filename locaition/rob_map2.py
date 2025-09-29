import cv2
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from pyapriltags import Detector

# --- カメラ設定 ---
DEVICE = 0  # 使うカメラ番号
cap = cv2.VideoCapture(DEVICE)
if not cap.isOpened():
    raise RuntimeError("カメラを開けませんでした")

# --- AprilTag 検出器 ---
detector = Detector(families="tag36h11")

# --- Matplotlib 準備 ---
fig, (ax_cam, ax_map) = plt.subplots(
    1, 2, 
    figsize=(18, 9),  # 全体を大きく
    gridspec_kw={'width_ratios': [1, 2]}  # カメラ:マップ = 1:2
)

ax_cam.set_title("Camera")
ax_map.set_title("Bird's Eye Map")
ax_map.set_xlim(-2, 2)
ax_map.set_ylim(-2, 2)
ax_map.set_aspect("equal")

# AprilTag の位置を保持
tag_positions = {}

def update(frame):
    global tag_positions

    ret, img = cap.read()
    if not ret:
        return

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    tags = detector.detect(gray)

    # 💡 フレームごとに新しい位置を記録する辞書を用意
    current_positions = {}

    # カメラ映像に描画
    for tag in tags:
        corners = tag.corners.astype(int)
        for i in range(4):
            cv2.line(img, tuple(corners[i]), tuple(corners[(i+1)%4]), (0,255,0), 2)
        c = tag.center.astype(int)
        cv2.circle(img, tuple(c), 5, (0,0,255), -1)
        cv2.putText(img, str(tag.tag_id), tuple(c), cv2.FONT_HERSHEY_SIMPLEX, 
                    0.6, (255,0,0), 2)

        # 正規化してマップに配置
        norm_x = (c[0] / img.shape[1]) * 4 - 2
        norm_y = (c[1] / img.shape[0]) * 4 - 2
        current_positions[tag.tag_id] = (norm_x, -norm_y)

    # 💡 このフレームの検出結果で更新（消えたタグは自動で消える）
    tag_positions = current_positions

    # --- カメラ画像を Matplotlib に表示 ---
    ax_cam.clear()
    ax_cam.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    ax_cam.axis("off")
    ax_cam.set_title("Camera")

    # --- 鳥瞰図を更新 ---
    ax_map.clear()
    ax_map.set_xlim(-2, 2)
    ax_map.set_ylim(-2, 2)
    ax_map.set_aspect("equal")
    ax_map.set_title("Bird's Eye Map")

    for tid, pos in tag_positions.items():
        ax_map.plot(pos[0], pos[1], "ro")
        ax_map.text(pos[0]+0.05, pos[1]+0.05, f"ID {tid}", fontsize=8)


ani = FuncAnimation(fig, update, interval=100)
plt.show()

cap.release()

