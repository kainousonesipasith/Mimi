import cv2
import serial
import time
from fer import FER

# ตั้งค่าการเชื่อมต่อ Serial กับ Arduino
try:
    arduino = serial.Serial('COM3', 9600, timeout=1)
    time.sleep(2)
    print("ເຊື່ອມຕໍ່ກັບ Arduino ສຳເລັດ!")
except serial.SerialException:
    print("ບໍ່ສາມາດເຊື່ອມຕໍ່ Arduino ກະລຸນາກວດອບການເຊື່ອມຕໍ່")
    arduino = None
    connection_error = True
else:
    connection_error = False

# สร้างตัวตรวจจับอารมณ์
detector = FER(mtcnn=True)

# โหลดรูปภาพสำหรับแต่ละอารมณ์ (ครบ 7 อารมณ์)
emotion_images = {
    "happy": cv2.imread("emotionpic/mimi-happy.png"),
    "sad": cv2.imread("emotionpic/mimi-sad.png"),
    "angry": cv2.imread("emotionpic/mimi-angry.png"),
    "surprise": cv2.imread("emotionpic/mimi-surprise.png"),
    "disgust": cv2.imread("emotionpic/mimi-disgust.png"),
    "fear": cv2.imread("emotionpic/mimi-fear.png"),
    "neutral": cv2.imread("emotionpic/mimi-neutral.png"),
}

# เปิดกล้อง
cap = cv2.VideoCapture(0)
last_send_time = None
timeout_duration = 3  # กำหนดเวลาในการหน่วงสำหรับส่งข้อมูล (3 วินาที)
current_emotion_image = None  # ใช้เก็บรูปภาพอารมณ์ที่แสดงอยู่
# ตั้งค่า fullscreen flag
fullscreen = False
# เริ่มต้นการแสดงหน้าต่างที่สอง
cv2.namedWindow("Emotion Image", cv2.WINDOW_NORMAL)

while True:
    # อ่านเฟรมจากกล้อง
    ret, frame = cap.read()
    if not ret:
        break

    # พลิกเฟรมเพื่อให้แสดงเหมือนกล้องหน้า
    frame = cv2.flip(frame, 1)

    # ตรวจจับอารมณ์ในเฟรม
    result = detector.detect_emotions(frame)
    
    if result:
        # หาค่าที่มีคะแนนสูงสุดและดึงกรอบใบหน้า
        emotions = result[0]["emotions"]
        box = result[0]["box"]
        emotion, score = max(emotions.items(), key=lambda item: item[1])

        # วาดกรอบใบหน้าและแสดงผลอารมณ์
        x, y, w, h = box
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, f"{emotion}: {score:.2f}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

        # ส่งอารมณ์ไปยัง Arduino และแสดงข้อความเมื่อไม่มีการเชื่อมต่อ
        current_time = time.time()
        if arduino:
            if last_send_time is None or (current_time - last_send_time > timeout_duration):
                try:
                    arduino.write((emotion + '\n').encode())
                    last_send_time = current_time
                except serial.SerialException:
                    arduino = None
                    connection_error = True  # เปิดใช้งานการแสดงข้อความเมื่อไม่มีการเชื่อมต่อ
        else:
            # แสดงข้อความบนเฟรมเมื่อไม่มีการเชื่อมต่อกับ Arduino
            cv2.putText(frame, f"can't send '{emotion}' to Arduino", 
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    # อัปเดตรูปภาพอารมณ์ในหน้าต่างที่สอง
        new_emotion_image = emotion_images.get(emotion)
        if new_emotion_image is not None and new_emotion_image is not current_emotion_image:
            current_emotion_image = new_emotion_image
            
    # แสดงข้อความบนเฟรมเมื่อไม่สามารถเชื่อมต่อกับ Arduino ตั้งแต่แรก
    if connection_error:
        cv2.putText(frame, "connect to board not successful", 
                    (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    # แสดงหน้าต่างที่ 1: วิดีโอจากกล้อง
    cv2.imshow("Emotion Detection", frame)

    # แสดงหน้าต่างที่ 2: รูปภาพอารมณ์
    # if current_emotion_image is not None:
    #     if fullscreen:
    #         cv2.setWindowProperty("Emotion Image", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    #     else:
    #         cv2.setWindowProperty("Emotion Image", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)

    #     cv2.imshow("Emotion Image", current_emotion_image)

    # ตรวจสอบกดปุ่ม F11 เพื่อเปลี่ยนโหมดเต็มจอ
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):  # กด 'q' เพื่อออกจากโปรแกรม
        break
    elif key == 0xFF and cv2.getWindowProperty("Emotion Image", cv2.WND_PROP_FULLSCREEN) == -1:
        # หากกด F11 หรือคลิกที่หน้าต่างเพื่อทำให้มันเต็มจอ
        fullscreen = not fullscreen

    # กด 'q' เพื่อออกจากโปรแกรม
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ปิดกล้องและเชื่อมต่อ Serial
cap.release()
cv2.destroyAllWindows()
if arduino:
    arduino.close()
