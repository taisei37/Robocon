import json
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon

# ---------- パラメータ ----------
FIELD_W, FIELD_H = 500.0, 500.0  # フィールド全体

# 中央ブロックの例（四角形）
central_block_vertices = [
    (200, 200),
    (300, 200),
    (300, 300),
    (200, 300)
]

# ゴールボックスサイズ
goal_box_w, goal_box_h = 50, 50

# ---------- フィールド要素作成 ----------
elements = {
    "field_boundary": {"x_lines": [0, FIELD_W], "y_lines": [0, FIELD_H]},
    "central_block": {
        "type": "polygon",
        "vertices": central_block_vertices
    },
    "goal_boxes": [
        {"type": "rect", "x": 50, "y": 50,  "w": goal_box_w, "h": goal_box_h, "color": "blue"},
        {"type": "rect", "x": 50, "y": 400, "w": goal_box_w, "h": goal_box_h, "color": "yellow"}
    ]
}

# ---------- JSON出力 ----------
with open("field_map.json", "w", encoding="utf-8") as f:
    json.dump(elements, f, indent=2, ensure_ascii=False)
print("Saved field_map.json")

# ---------- 可視化 ----------
fig, ax = plt.subplots(figsize=(8, 8))

# 軸範囲
ax.set_xlim(-50, FIELD_W + 50)
ax.set_ylim(-50, FIELD_H + 50)
ax.set_aspect('equal')

# 軸ラベルと目盛り
ax.set_xlabel("X [mm]", fontsize=12)
ax.set_ylabel("Y [mm]", fontsize=12)
ax.tick_params(axis='both', which='major', labelsize=10)

# X軸ラベルを上に移動
ax.xaxis.set_label_position('top')
ax.xaxis.tick_top()

# 目盛り
ax.set_xticks(range(0, int(FIELD_W)+1, 100))
ax.set_yticks(range(0, int(FIELD_H)+1, 100))

# 上下反転（必要なら）
plt.gca().invert_yaxis()

# フィールド枠線
ax.plot([0, FIELD_W, FIELD_W, 0, 0],
        [0, 0, FIELD_H, FIELD_H, 0],
        color='black', linewidth=2)


ax.set_title("Field Map")
plt.show()

