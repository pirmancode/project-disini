#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Inisialisasi LCD I2C dengan alamat 0x27 dan ukuran 16x2
LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
    lcd.init();        // Inisialisasi LCD
    lcd.backlight();   // Nyalakan lampu latar LCD
}

void loop() {
    String text = "fida bocil<3";
    int len = text.length();
    int lcdWidth = 16;
    
    for (int pos = -len; pos <= lcdWidth; pos++) {
        lcd.clear();
        lcd.setCursor(pos, 0); // Set posisi teks
        lcd.print(text);
        delay(300); // Delay untuk efek scrolling
    }
}
