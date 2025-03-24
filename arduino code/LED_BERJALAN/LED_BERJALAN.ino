void setup()
{
  for (int i = 2; i <= 6; i++) {
    pinMode(i, OUTPUT);
  }
}

void loop()
{
  // 1. Efek Berjalan Maju-Mundur (Seperti Ular)
  for (int i = 2; i <= 6; i++) {
    nyalakanLED(i);
  }
  for (int i = 5; i >= 2; i--) {
    nyalakanLED(i);
  }

  // 2. Efek Gelombang (Dua LED Bersamaan)
  for (int i = 2; i <= 5; i++) {
    digitalWrite(i, HIGH);
    digitalWrite(i + 1, HIGH);
    delay(150);
    digitalWrite(i, LOW);
    digitalWrite(i + 1, LOW);
  }

  // 3. Efek Strobe Cepat (Semua LED Berkedip Cepat)
  for (int j = 0; j < 5; j++) {
    semuaLED(HIGH);
    delay(50);
    semuaLED(LOW);
    delay(50);
  }
}

// Fungsi untuk menyalakan 1 LED dan mematikan lainnya
void nyalakanLED(int pin) {
  semuaLED(LOW);
  digitalWrite(pin, HIGH);
  delay(100);
}

// Fungsi untuk menyalakan atau mematikan semua LED
void semuaLED(int state) {
  for (int i = 2; i <= 6; i++) {
    digitalWrite(i, state);
  }
}

