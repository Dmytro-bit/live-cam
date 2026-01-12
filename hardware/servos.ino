#include <Servo.h>

Servo s1, s2;

void setup() {
  Serial.begin(9600);
  s1.attach(9);
  s2.attach(10);
}

void loop() {
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');

    int a1, a2;
    if (sscanf(line.c_str(), "%d %d", &a1, &a2) == 2) {
      if (a1 >= 0 && a1 <= 180) s1.write(a1);
      if (a2 >= 0 && a2 <= 180) s2.write(a2);
    }
  }
}
