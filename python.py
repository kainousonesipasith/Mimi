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
    connection_error = True  # ใช้ตัวแปรนี้เพื่อตรวจสอบการแสดงข้อความบนเฟรม
else:
    connection_error = False

# สร้างตัวตรวจจับอารมณ์
detector = FER(mtcnn=True)

# เปิดกล้อง
cap = cv2.VideoCapture(0)
last_send_time = None
timeout_duration = 3  # กำหนดเวลาในการหน่วงสำหรับส่งข้อมูล (3 วินาที)

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

    # แสดงข้อความบนเฟรมเมื่อไม่สามารถเชื่อมต่อกับ Arduino ตั้งแต่แรก
    if connection_error:
        cv2.putText(frame, "connect to board not successful", 
                    (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    # แสดงเฟรมที่มีการตรวจจับอารมณ์
    cv2.imshow("Emotion Detection", frame)

    # กด 'q' เพื่อออกจากโปรแกรม
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ปิดกล้องและเชื่อมต่อ Serial
cap.release()
cv2.destroyAllWindows()
if arduino:
    arduino.close()
