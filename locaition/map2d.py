import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np

# --- フィールド設定（mm） ---
FIELD_W, FIELD_H = 500.0, 500.0
field_corners = np.array([
    [0.0, 0.0],          # 左下
    [FIELD_W, 0.0],      # 右下
    [FIELD_W, FIELD_H],  # 右上
    [0.0, FIELD_H]       # 左上
])

# --- カメラ設定（例：あなたの値） ---
camera_pos = np.array([250.0, -200.0])  # mm (x, y)
camera_height = 800.0                   # mm（今回は2D投影なので表示用のみ）
fov_deg = 120.0
fov_rad = np.deg2rad(fov_deg)

# カメラが見る「注視点」（ここではフィールド中心）
target = np.array([FIELD_W/2.0, FIELD_H/2.0])
direction = target - camera_pos
center_angle = np.arctan2(direction[1], direction[0])  # カメラ向き角（ラジアン）

# 判定関数：点がFOV内か（2D平面、視線は中心角）
def is_point_in_fov(pt, cam_pos, center_angle, half_fov_rad):
    vec = pt - cam_pos
    ang = np.arctan2(vec[1], vec[0])
    # 差を -pi..pi に正規化
    diff = (ang - center_angle + np.pi) % (2*np.pi) - np.pi
    return abs(diff) <= half_fov_rad, diff, ang

# 描画用の視線長さ（図示用）
# 適切な長さ：カメラから各コーナーまでの最遠距離に少し余裕を加える
dists = np.linalg.norm(field_corners - camera_pos, axis=1)
view_length = dists.max() * 1.2

# 左右の視界端の角度
left_angle = center_angle - fov_rad/2
right_angle = center_angle + fov_rad/2
left_ray = camera_pos + view_length * np.array([np.cos(left_angle), np.sin(left_angle)])
right_ray = camera_pos + view_length * np.array([np.cos(right_angle), np.sin(right_angle)])

# 判定と表示準備
half_fov = fov_rad / 2
inside_flags = []
corner_infos = []
for i, c in enumerate(field_corners):
    inside, diff, ang = is_point_in_fov(c, camera_pos, center_angle, half_fov)
    inside_flags.append(inside)
    corner_infos.append((i, c, inside, np.rad2deg(diff)))

all_inside = all(inside_flags)

# --- 描画 ---
fig, ax = plt.subplots(figsize=(7,7))
ax.set_aspect('equal')

# フィールド（黒枠）
rect = plt.Rectangle((0, 0), FIELD_W, FIELD_H, fill=False, color='black', lw=2)
ax.add_patch(rect)
ax.text(FIELD_W/2, FIELD_H/2, "Field 500×500", ha='center', va='center', fontsize=10, color='gray')

# カメラ位置
ax.plot(camera_pos[0], camera_pos[1], 'ro', label='Camera')
ax.text(camera_pos[0], camera_pos[1]-20, "Camera", ha='center', color='red')

# 視線方向（中心）
ax.plot([camera_pos[0], camera_pos[0] + view_length*np.cos(center_angle)],
        [camera_pos[1], camera_pos[1] + view_length*np.sin(center_angle)], 'r-', lw=1)

# 視野端（破線）と視野領域（薄い三角）
ax.plot([camera_pos[0], left_ray[0]], [camera_pos[1], left_ray[1]], 'r--')
ax.plot([camera_pos[0], right_ray[0]], [camera_pos[1], right_ray[1]], 'r--')
fov_poly = plt.Polygon([camera_pos, left_ray, right_ray], color='r', alpha=0.12)
ax.add_patch(fov_poly)

# 各コーナーをプロット（FOV内は緑、外はオレンジ）
labels = ['BL', 'BR', 'TR', 'TL']  # bottom-left, bottom-right, top-right, top-left
for idx, corner, inside, ang_diff_deg in corner_infos:
    color = 'lime' if inside else 'orange'
    ax.plot(corner[0], corner[1], 'o', color=color)
    ax.text(corner[0]+6, corner[1]+6, f"{labels[idx]} ({int(corner[0])},{int(corner[1])})\nΔ={ang_diff_deg:.1f}°",
            color='black', fontsize=8, bbox=dict(facecolor='white', alpha=0.6, edgecolor='none'))

# 表示域を調整（カメラが外にあるので余裕を取る）
pad = 200
xmin = min(-300, camera_pos[0]-pad)
xmax = max(800, camera_pos[0]+pad)
ymin = min(-400, camera_pos[1]-pad)
ymax = max(800, camera_pos[1]+pad)
ax.set_xlim(xmin, xmax)
ax.set_ylim(ymin, ymax)
ax.grid(True)
ax.set_xlabel("X (mm)")
ax.set_ylabel("Y (mm)")
ax.set_title(f"Camera FOV {fov_deg}° top-down check — All corners inside: {all_inside}")

plt.legend(loc='upper right')
plt.show()

# ターミナル出力
for idx, corner, inside, ang_diff_deg in corner_infos:
    print(f"{labels[idx]} corner {corner} -> inside={inside}, angular_offset={ang_diff_deg:.1f}°")

print("\nSummary:", "ALL CORNERS INSIDE FOV" if all_inside else "NOT ALL INSIDE")
