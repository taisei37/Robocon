import cv2
import numpy as np
import os

# ---------- 設定 ----------
image_folder = "/home/taisei37/apriltags/tag36h11"  # 元画像フォルダ
output_folder = "apriltag_single333"                   # 出力フォルダ
TAG_FAMILY = "tag36_11"                             # タグファミリ名
DPI = 300                                           # 印刷用解像度
MM_PER_INCH = 25.4

# タグIDと実際のサイズ(mm)の対応リスト
tags_info = [
    {"id": 0, "size_mm": 80},
    {"id": 0, "size_mm": 90},
    {"id": 0, "size_mm": 100},
    # 必要に応じてここに追加
]

os.makedirs(output_folder, exist_ok=True)

# ---------- タグごとに処理 ----------
for tag in tags_info:
    TAG_ID = tag["id"]
    size_mm = tag["size_mm"]

    tag_filename = f"{TAG_FAMILY}_{TAG_ID:05d}.png"
    tag_path = os.path.join(image_folder, tag_filename)

    if not os.path.exists(tag_path):
        print(f"❌ タグ画像が見つかりません: {tag_path}")
        continue

    base_img = cv2.imread(tag_path, cv2.IMREAD_GRAYSCALE)
    if base_img is None:
        print(f"❌ 画像の読み込みに失敗しました: {tag_path}")
        continue

    # mm → inch → pixel変換
    size_inch = size_mm / MM_PER_INCH
    pixels = int(size_inch * DPI)

    # リサイズ（拡大・縮小）
    resized = cv2.resize(base_img, (pixels, pixels), interpolation=cv2.INTER_NEAREST)

    # 白背景キャンバスに配置（余白付き）
    margin = pixels // 10  # 周囲に1割の余白
    canvas = np.ones((pixels + 2 * margin, pixels + 2 * margin), dtype=np.uint8) * 255
    canvas[margin:margin + pixels, margin:margin + pixels] = resized

    # ファイル保存
    output_path = os.path.join(output_folder, f"{TAG_FAMILY}_{TAG_ID}_{size_mm}mm.png")
    cv2.imwrite(output_path, canvas)
    print(f"✅ 保存完了: {output_path}")

    # 表示
    cv2.imshow("AprilTag", canvas)
    print(f"{size_mm} mm タグを表示中。キーを押すと次へ進みます（ESCで終了）")
    key = cv2.waitKey(0)
    if key == 27:  # ESCキーで終了
        break

cv2.destroyAllWindows()
print("🎉 完了しました！")

