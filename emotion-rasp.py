import cv2
import time
from fer import FER
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os

# ตรวจสอบและติดตั้งไดรเวอร์ของหน้าจอ MHS-3.5 นิ้วก่อน
# เช่น sudo apt-get install python3-pillow

# ตั้งค่าและเปิดการเชื่อมต่อกล้อง
detector = FER(mtcnn=True)
cap = cv2.VideoCapture(0)

# สร้างฟังก์ชันสำหรับแสดงอารมณ์บนหน้าจอ MHS-3.5 นิ้ว
def display_emotion_on_screen(emotion):
    # สร้างพื้นหลังสีดำให้กับหน้าจอ
    image = Image.new("RGB", (480, 320), (0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # เลือกฟอนต์และขนาด
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 50)
    
    # วาดข้อความอารมณ์ที่กลางหน้าจอ
    text = f"{emotion}"
    text_width, text_height = draw.textsize(text, font=font)
    draw.text(
        ((480 - text_width) // 2, (320 - text_height) // 2),
        text,
        font=font,
        fill=(255, 255, 255)
    )
    
    # แปลงภาพให้สามารถแสดงบนหน้าจอ MHS-3.5 นิ้วได้
    screen = np.array(image)
    screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)
    cv2.imshow("Emotion Display", screen)
    cv2.waitKey(1)  # อัพเดตหน้าจอ

while True:
    # อ่านเฟรมจากกล้อง
    ret, frame = cap.read()
    if not ret:
        break

    # ตรวจจับอารมณ์ในเฟรม
    result = detector.detect_emotions(frame)
    
    if result:
        # หาค่าที่มีคะแนนสูงสุด
        emotions = result[0]["emotions"]
        emotion, score = max(emotions.items(), key=lambda item: item[1])

        # แสดงผลอารมณ์ในกรอบ
        cv2.putText(frame, f"{emotion}: {score:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        
        # แสดงอารมณ์บนหน้าจอ MHS-3.5 นิ้ว
        display_emotion_on_screen(emotion)

    # แสดงเฟรมที่มีการตรวจจับอารมณ์
    cv2.imshow("Emotion Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# ปิดการทำงานของกล้อง
cap.release()
cv2.destroyAllWindows()
