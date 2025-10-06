import cv2

for i in range(5):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"✅ カメラ {i} が利用可能です")
        cap.release()
    else:
        print(f"❌ カメラ {i} は開けません")

