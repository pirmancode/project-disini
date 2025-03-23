#define ledRed 2
#define ledGreen 4
#define ledBlue 7  // Tambahkan LED baru

void setup() {
  pinMode(ledRed, OUTPUT);
  pinMode(ledGreen, OUTPUT);
  pinMode(ledBlue, OUTPUT); // Inisialisasi LED baru
}

void loop() {
  digitalWrite(ledRed, HIGH);
  delay(100);
  digitalWrite(ledRed, LOW);

  digitalWrite(ledGreen, HIGH);
  delay(100);
  digitalWrite(ledGreen, LOW);

  digitalWrite(ledBlue, HIGH); // Menyalakan LED baru
  delay(100);
  digitalWrite(ledBlue, LOW);  // Mematikan LED baru
}
