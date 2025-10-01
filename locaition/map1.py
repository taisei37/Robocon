import json
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon

# ---------- パラメータ ----------
FIELD_W, FIELD_H = 2065.0, 2300.0  # フィールド全体

# フィールド外枠（4点座標）
field_vertices = [
    (265, 0),
    (2065, 0),
    (2065, 1800),
    (265, 1800)
]

# フィールド枠線（縦線と横線）
x_lines = [300, 1800]
y_lines = [0, 1800]

# 中央ブロック（4点座標で指定）
central_block_vertices = [
    (865, 500),   # 左下
    (1165, 500),   # 右下
    (1165, 1400),  # 右上
    (865, 1400)   # 左上
]

# ゴール箱の基本サイズ
goal_box_w = 265.0
goal_box_h = 300.0

# ---------- マップ要素作成 ----------
elements = {
    "field_boundary": {"x_lines": x_lines, "y_lines": y_lines},
    "central_block": {
        "type": "polygon",
        "vertices": central_block_vertices
    },
    "goal_boxes": [
        {"type": "rect", "x": 265.0 - goal_box_w, "y": 200.0,  "w": goal_box_w, "h": goal_box_h, "color": "red"},
        {"type": "rect", "x": 265.0 - goal_box_w, "y": 800.0,  "w": goal_box_w, "h": goal_box_h, "color": "blue"},
        {"type": "rect", "x": 265.0 - goal_box_w, "y": 1400.0, "w": goal_box_w, "h": goal_box_h, "color": "yellow"},
        {"type": "rect", "x": 265.0, "y": 1800, "w": 500.0, "h": 500.0, "color": "none"}  # 左下の黒枠箱
    ]
}

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
if cb["type"] == "polygon":
    polygon = Polygon(cb["vertices"], closed=True,
                      facecolor='lightgray', edgecolor='black', linewidth=1.0)
    ax.add_patch(polygon)

# ゴール箱
for g in elements["goal_boxes"]:
    ax.add_patch(Rectangle(
        (g["x"], g["y"]), g["w"], g["h"],
        fill=(g["color"] != "none"),
        facecolor=(g["color"] if g["color"] != "none" else "none"),
        edgecolor='black', linewidth=2
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
ax.xaxis.set_label_position('top')
ax.xaxis.tick_top()

# 目盛り
ax.set_xticks([0, 265, 600, 900, 1200, 1500, 1800, 2065])
ax.set_yticks([0, 500, 1000, 1500, 1800, 2300])

# 必要なら上下反転
plt.gca().invert_yaxis()

ax.set_title("Field Map")
plt.show()

