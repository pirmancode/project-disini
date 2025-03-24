#include <Wire.h>
#include <LiquidCrystal_I2C.h>

#define ledRed1 2
#define ledRed2 4  
#define ledRed3 7  
#define ledRed4 8  // Menambahkan satu lampu merah lagi

LiquidCrystal_I2C lcd(0x27, 16, 2); // Alamat I2C bisa 0x27 atau 0x3F tergantung modul

void setup() {
  pinMode(ledRed1, OUTPUT);
  pinMode(ledRed2, OUTPUT);
  pinMode(ledRed3, OUTPUT);
  pinMode(ledRed4, OUTPUT); // Inisialisasi LED baru
  
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("LED Controller");
}

void loop() {
  lcd.setCursor(0, 1);
  lcd.print("Red LED 1  ");
  digitalWrite(ledRed1, HIGH);
  delay(800);
  digitalWrite(ledRed1, LOW);
  delay(800);

  lcd.setCursor(0, 1);
  lcd.print("Red LED 2  ");
  digitalWrite(ledRed2, HIGH);
  delay(800);
  digitalWrite(ledRed2, LOW);
  delay(800);

  lcd.setCursor(0, 1);
  lcd.print("Red LED 3  ");
  digitalWrite(ledRed3, HIGH);
  delay(800);
  digitalWrite(ledRed3, LOW);
  delay(800);
  
  lcd.setCursor(0, 1);
  lcd.print("Red LED 4  "); // Menampilkan teks untuk LED baru
  digitalWrite(ledRed4, HIGH);
  delay(800);
  digitalWrite(ledRed4, LOW);
  delay(800);
}

