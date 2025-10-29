import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.widgets import Slider
import numpy as np
from scipy.spatial.transform import Rotation as R

# --- フィールドサイズ [m] ---
FIELD_W, FIELD_H = 0.5, 0.5

# --- カメラ位置 [x, y, z] ---
cam_pos = np.array([0.25, 0.495, 0.8])

# --- 初期カメラ姿勢（degrees） ---
init_roll, init_pitch, init_yaw = 0, -95, 0

# --- サンプルタグ位置 ---
tags = np.array([
    [0.1, 0.2, 0.0],
    [0.4, 0.3, 0.0],
    [0.35, 0.45, 0.0]
])

# --- 描画関数 ---
def update_view(roll, pitch, yaw):
    ax.cla()  # 前回描画クリア

    # フィールド平面
    ax.plot([0, FIELD_W, FIELD_W, 0, 0],
            [0, 0, FIELD_H, FIELD_H, 0],
            [0, 0, 0, 0, 0], 'k-', linewidth=2)

    # カメラ回転行列
    cam_euler = np.deg2rad([roll, pitch, yaw])
    cam_R = R.from_euler('xyz', cam_euler).as_matrix()

    # カメラ前方ベクトル
    fov_length = 0.3
    view_vec = cam_R @ np.array([0, 0, 1])  # カメラ座標系の前方向
    view_vec = view_vec * fov_length  # 長さを調整

    # カメラ表示
    ax.scatter(cam_pos[0], cam_pos[1], cam_pos[2], c='blue', s=100, label='Camera')
    ax.quiver(cam_pos[0], cam_pos[1], cam_pos[2],
              view_vec[0], view_vec[1], view_vec[2],
              color='blue', arrow_length_ratio=0.2, linewidth=2, label='Camera Front')

    # タグ表示
    ax.scatter(tags[:,0], tags[:,1], tags[:,2], c='red', s=50, label='Tags')
    for i, tag in enumerate(tags):
        ax.text(tag[0]+0.01, tag[1]+0.01, tag[2]+0.01, f'ID {i}', color='red')

    # 軸ラベルと範囲
    ax.set_xlabel("X [m]")
    ax.set_ylabel("Y [m]")
    ax.set_zlabel("Z [m]")
    ax.set_title("3D Field Map with Camera Orientation")
    ax.set_xlim(0, FIELD_W)
    ax.set_ylim(0, FIELD_H)
    ax.set_zlim(0, 1.0)
    ax.legend()
    plt.draw()

# --- 3D図とスライダー領域 ---
fig = plt.figure(figsize=(10,8))
ax = fig.add_subplot(111, projection='3d')
plt.subplots_adjust(bottom=0.35)  # スライダー用スペース確保

# --- スライダー追加 ---
ax_roll = plt.axes([0.15, 0.25, 0.7, 0.03])
ax_pitch = plt.axes([0.15, 0.20, 0.7, 0.03])
ax_yaw = plt.axes([0.15, 0.15, 0.7, 0.03])

slider_roll = Slider(ax_roll, 'Roll', -180, 180, valinit=init_roll)
slider_pitch = Slider(ax_pitch, 'Pitch', 0, 180, valinit=init_pitch)
slider_yaw = Slider(ax_yaw, 'Yaw', -180, 180, valinit=init_yaw)

# --- スライダー更新関数 ---
def slider_update(val):
    update_view(slider_roll.val, slider_pitch.val, slider_yaw.val)

slider_roll.on_changed(slider_update)
slider_pitch.on_changed(slider_update)
slider_yaw.on_changed(slider_update)

# --- 初回描画 ---
update_view(init_roll, init_pitch, init_yaw)
plt.show()
