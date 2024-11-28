#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// กำหนดที่อยู่ของ LCD (เช่น 0x27)
LiquidCrystal_I2C lcd(0x27, 16, 2);

// กำหนดอิโมจิสำหรับอารมณ์ต่างๆ
byte happy[8] = {
    0b00000,
    0b00100,
    0b01010,
    0b00000,
    0b10001,
    0b01110,
    0b00000,
    0b00000
};

byte sad[8] = {
    0b00000,
    0b00100,
    0b01010,
    0b00000,
    0b10001,
    0b00110,
    0b00000,
    0b00000
};

byte angry[8] = {
    0b00000,
    0b01110,
    0b10001,
    0b00110,
    0b10001,
    0b01110,
    0b00000,
    0b00000
};

byte surprised[8] = {
    0b00000,
    0b00100,
    0b01010,
    0b10001,
    0b01110,
    0b00000,
    0b00000,
    0b00000
};

// สร้างอิโมจิตามอารมณ์
void setup() {
    lcd.begin();
    lcd.backlight();
    lcd.createChar(0, happy);      // สร้างอิโมจิ "happy"
    lcd.createChar(1, sad);        // สร้างอิโมจิ "sad"
    lcd.createChar(2, angry);      // สร้างอิโมจิ "angry"
    lcd.createChar(3, surprised);   // สร้างอิโมจิ "surprised"
    Serial.begin(9600);            // เริ่มต้น Serial
}

void loop() {
    // สมมติว่าคุณรับข้อมูลอารมณ์จาก Serial
    if (Serial.available() > 0) {
        String emotion = Serial.readStringUntil('\n');
        displayEmoji(emotion);
    }
}

void displayEmoji(String emotion) {
    lcd.clear();
    if (emotion == "happy") {
        lcd.write(0); // แสดงอิโมจิ "happy"
    } else if (emotion == "sad") {
        lcd.write(1); // แสดงอิโมจิ "sad"
    } else if (emotion == "angry") {
        lcd.write(2); // แสดงอิโมจิ "angry"
    } else if (emotion == "surprised") {
        lcd.write(3); // แสดงอิโมจิ "surprised"
    } else {
        lcd.clear();
        lcd.print("Unknown"); // แสดงข้อความถ้าไม่รู้จักอารมณ์
    }
}
