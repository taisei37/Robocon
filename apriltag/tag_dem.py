import cv2
import apriltag

# カメラ起動
cap = cv2.VideoCapture(0)
detector = apriltag.Detector()

while True:
    ret, frame = cap.read()
    if not ret:
        print("カメラから映像を取得できません")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    tags = detector.detect(gray)

    if tags:
        print(f"=== Detected {len(tags)} AprilTags ===")
        for tag in tags:
            print(f"[Tag ID: {tag.tag_id}]")
            print(f"  Center : ({tag.center[0]:.2f}, {tag.center[1]:.2f})")
            print("  Corners:")
            for corner in tag.corners:
                print(f"    ({corner[0]:.2f}, {corner[1]:.2f})")
            print()
    else:
        print("No tags detected")

    for tag in tags:
        corners = tag.corners
        for i in range(4):
            pt1 = tuple(map(int, corners[i]))
            pt2 = tuple(map(int, corners[(i + 1) % 4]))
            cv2.line(frame, pt1, pt2, (0, 255, 0), 2)
        center = tuple(map(int, tag.center))
        cv2.putText(frame, str(tag.tag_id), center, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    cv2.imshow('AprilTag Detection', frame)

    if cv2.waitKey(1) & 0xFF == 27:  # Escキーで終了
        break

cap.release()
cv2.destroyAllWindows()

