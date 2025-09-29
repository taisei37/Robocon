import json
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# ---------- パラメータ ----------
FIELD_W, FIELD_H = 1820.0, 2070.0  # フィールド全体

# フィールド枠線（縦線と横線）
x_lines = [250, 1800, 2065]   # ← 1800 を追加
y_lines = [0, 1800]

# 中央ブロック
central_block_width = 280.0
central_block_height = 900.0
central_block_center = (FIELD_W/2, FIELD_H/2)

# 左側ゴール箱
goal_box_w = 265.0
goal_box_h = 300.0
goal_box_margin_x = 20.0
goal_gap_y = 250.0

# ---------- マップ要素作成 ----------
elements = {
    "field_boundary": {"x_lines": x_lines, "y_lines": y_lines},
    "central_block": {
        "type": "rect_center",
        "cx": central_block_center[0],
        "cy": central_block_center[1],
        "w": central_block_width,
        "h": central_block_height
    },
}

# ゴール箱（左側に縦3つ）
goal_boxes = []
for i in range(3):
    gy = 100.0 + i*(goal_box_h + goal_gap_y)
    goal_boxes.append({
        "type": "rect",
        "x": goal_box_margin_x,
        "y": gy,
        "w": goal_box_w,
        "h": goal_box_h
    })
elements["goal_boxes"] = goal_boxes

# ---------- JSON出力 ----------
with open("field_map.json", "w") as f:
    json.dump(elements, f, indent=2)
print("Saved field_map.json")

# ---------- 可視化 ----------
fig, ax = plt.subplots(figsize=(10,10))

# フィールド枠線（縦線）
for x in x_lines:
    ax.plot([x, x], [y_lines[0], y_lines[1]], color='black', linewidth=3)

# フィールド枠線（横線）
for y in y_lines:
    ax.plot([x_lines[0], x_lines[-1]], [y, y], color='black', linewidth=3)

# 中央ブロック
cb = elements["central_block"]
ax.add_patch(Rectangle(
    (cb["cx"]-cb["w"]/2, cb["cy"]-cb["h"]/2),
    cb["w"], cb["h"],
    facecolor='lightgray', edgecolor='black', linewidth=1.0
))

# ゴール箱
for g in elements["goal_boxes"]:
    ax.add_patch(Rectangle(
        (g["x"], g["y"]), g["w"], g["h"],
        fill=False, edgecolor='blue', linewidth=2
    ))

# 軸範囲
ax.set_xlim(-100, FIELD_W + 100)
ax.set_ylim(-100, FIELD_H + 100)
ax.set_aspect('equal')

# 軸ラベルと目盛り
ax.set_xlabel("X [mm]", fontsize=12)
ax.set_ylabel("Y [mm]", fontsize=12)
ax.tick_params(axis='both', which='major', labelsize=10)

# 100mm刻みの目盛り
ax.set_xticks(range(0, int(FIELD_W)+101, 100))
ax.set_yticks(range(0, int(FIELD_H)+101, 100))

# 軸を反転（必要に応じて）
plt.gca().invert_yaxis()

ax.set_title("Field Map")
plt.show()

