import os
from glob import glob
from reportlab.platypus import SimpleDocTemplate, Image, Paragraph, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors

# 設定
image_folder = "/home/taisei37/apriltags/tag36h11"
output_file = "apriltag_sheet_9tags.pdf"
tags_per_row = 3
max_tags = 9
image_size_mm = 60

# スタイル
styles = getSampleStyleSheet()
caption_style = ParagraphStyle(
    'Caption',
    parent=styles['Normal'],
    fontSize=10,
    alignment=1  # 中央揃え
)

# PNGファイル一覧から最大9個取得
images = sorted(glob(os.path.join(image_folder, "*.png")))[:max_tags]

if len(images) == 0:
    print("⚠️ PNGファイルが見つかりません。")
    exit(1)

table_data = []
row = []

for i, img_path in enumerate(images):
    tag_id = os.path.splitext(os.path.basename(img_path))[0].split('_')[-1]
    img = Image(img_path, width=image_size_mm * mm, height=image_size_mm * mm)
    caption = Paragraph(f"ID: {int(tag_id)}", caption_style)

    # 画像とキャプションを縦に並べる
    cell_data = [[img], [caption]]
    cell = Table(cell_data, colWidths=[image_size_mm * mm])
    cell.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    row.append(cell)

    if len(row) == tags_per_row:
        table_data.append(row)
        row = []

if row:
    table_data.append(row)

# PDF作成
doc = SimpleDocTemplate(output_file, pagesize=A4)
elements = []

if table_data:
    table = Table(table_data, hAlign='CENTER')
    elements.append(table)
    doc.build(elements)
    print(f"✅ PDF生成完了: {output_file}")
else:
    print("❌ table_data が空です。")

