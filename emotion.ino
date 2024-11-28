#include <LiquidCrystal.h>

// กำหนดพอร์ตที่เชื่อมต่อกับ LCD
LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

void setup() {
  Serial.begin(9600); // เริ่มการเชื่อมต่อ Serial
  lcd.begin(16, 2);   // กำหนดขนาดของ LCD
}

void loop() {
  if (Serial.available() > 0) {
    String emotion = Serial.readStringUntil('\n'); // อ่านข้อมูลอารมณ์จาก Serial

    // แสดงอิโมจิตามอารมณ์
    if (emotion == "happy") {
      displayEmoji("😊");
    } else if (emotion == "sad") {
      displayEmoji("😢");
    } else if (emotion == "angry") {
      displayEmoji("😠");
    } else if (emotion == "fear") {
      displayEmoji("😨");
    } else if (emotion == "surprise") {
      displayEmoji("😮");
    } else if (emotion == "disgust") {
      displayEmoji("🤢");
    } else if (emotion == "neutral") {
      displayEmoji("😐");
    } else {
      displayEmoji("❓"); // สำหรับอารมณ์ที่ไม่รู้จัก
    }
  }
}

void displayEmoji(String emoji) {
  lcd.clear(); // ล้างหน้าจอ LCD
  lcd.setCursor(0, 0); // ตั้งตำแหน่งการแสดงผล
  lcd.print(emoji); // แสดงอิโมจิ
}
