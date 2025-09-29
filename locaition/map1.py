import json
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon

# ---------- パラメータ ----------
FIELD_W, FIELD_H = 2065.0, 2300.0  # フィールド全体

# 四角形の頂点
field_vertices = [
    (265, 0),
    (2065, 0),
    (2065, 1800), 
    (265, 1800)
]

# フィールド枠線（縦線と横線）
x_lines = [300, 1800]
y_lines = [0, 1800]

# 中央ブロック
central_block_width = 280.0
central_block_height = 900.0
central_block_center = (FIELD_W/2, FIELD_H/2)

# ゴール箱（左側）
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
with open("field_map.json", "w", encoding="utf-8") as f:
    json.dump(elements, f, indent=2, ensure_ascii=False)
print("Saved field_map.json")

# ---------- 可視化 ----------
fig, ax = plt.subplots(figsize=(10, 10))

# 外枠フィールドを描画
polygon = Polygon(field_vertices, closed=True, fill=False, edgecolor="black", linewidth=3)
ax.add_patch(polygon)

# 中央ブロック
cb = elements["central_block"]
ax.add_patch(Rectangle(
    (cb["cx"] - cb["w"]/2, cb["cy"] - cb["h"]/2),
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

# X軸ラベルを上に移動
ax.xaxis.set_label_position('top')  # ラベルの位置
ax.xaxis.tick_top()                 # 目盛りも上に

# 目盛り
ax.set_xticks([0,265,600,900,1200,1500,1800,2065])
ax.set_yticks([0,500,1000,1500,1800,2300])

# 必要なら上下反転
plt.gca().invert_yaxis()

ax.set_title("Field Map")
plt.show()

