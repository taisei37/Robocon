import json
import matplotlib.pyplot as plt

# ---------- パラメータ ----------
FIELD_W, FIELD_H = 500.0, 500.0  # フィールド全体サイズ [mm]

# ---------- フィールド要素 ----------
elements = {
    "field_boundary": {
        "x_lines": [0, FIELD_W],
        "y_lines": [0, FIELD_H]
    }
}

# ---------- JSON出力 ----------
with open("field_map.json", "w", encoding="utf-8") as f:
    json.dump(elements, f, indent=2, ensure_ascii=False)
print("Saved field_map.json")

# ---------- 可視化 ----------
fig, ax = plt.subplots(figsize=(8, 8))

# 軸範囲と比率設定
ax.set_xlim(-50, FIELD_W + 50)
ax.set_ylim(-50, FIELD_H + 50)
ax.set_aspect('equal')

# 軸ラベル・目盛り
ax.set_xlabel("X [mm]", fontsize=12)
ax.set_ylabel("Y [mm]", fontsize=12)
ax.tick_params(axis='both', which='major', labelsize=10)

# X軸を上に移動
ax.xaxis.set_label_position('top')
ax.xaxis.tick_top()

# グリッド間隔
ax.set_xticks(range(0, int(FIELD_W) + 1, 100))
ax.set_yticks(range(0, int(FIELD_H) + 1, 100))

# Y軸反転（画像座標系風に）
plt.gca().invert_yaxis()

# ---------- フィールド枠線 ----------
ax.plot(
    [0, FIELD_W, FIELD_W, 0, 0],
    [0, 0, FIELD_H, FIELD_H, 0],
    color='black', linewidth=2
)

# ---------- タイトルと表示 ----------
ax.set_title("Field Map (500mm x 500mm)")
plt.show()
