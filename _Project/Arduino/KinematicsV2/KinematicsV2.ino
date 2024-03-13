//// ---- Import libraries
#include "pin.h"
#include <Servo.h>


//// ---- Variables
Servo servo;
int link_lg, link_sh;
int msg;


//// ---- Functions
void moveTo(int pin, int dir_pin, int dir, int spd, int degree) {
  int steps = degree / microStep;
  Serial.println(steps);

  // 1: clockwise
  // 0: counter-clockwise
  digitalWrite(dir_pin, dir);
  for (int i = 0; i < steps; ++i) {
    digitalWrite(pin, HIGH);
    delay(spd);
    digitalWrite(pin, LOW);
    delay(spd);
  }

  //  delay(500);
}

void moveToSimo(int dir1, int deg1, int dir2, int deg2, int spd) {
  int steps1 = deg1 / microStep;
  int steps2 = deg2 / microStep;

  int cur1 = 0, cur2 = 0;
  bool done1 = false, done2 = false;

  digitalWrite(link_lg_dir, dir1);
  digitalWrite(link_sh_dir, dir2);

  while (true) {
    if (cur1 != steps1) {
      cur1++;
      digitalWrite(link_lg_pin, HIGH);
      delay(spd);
      digitalWrite(link_lg_pin, LOW);
      delay(spd);
    } else {
      done1 = true;
    }

    if (cur2 != steps2) {
      cur2++;
      digitalWrite(link_sh_pin, HIGH);
      delay(spd);
      digitalWrite(link_sh_pin, LOW);
      delay(spd);
    } else {
      done2 = true;
    }

    if (done1 && done2) {
      break;
    }
  }
}

void moveMid(int dir) {
  // Pos before move must be 25 degree
  int steps = 70 / microStep;
  Serial.println(steps);

  digitalWrite(link_lg_dir, dir);
  digitalWrite(link_sh_dir, !dir);

  for (int i = 0; i < steps; ++i) {
    digitalWrite(link_lg_pin, HIGH);
    digitalWrite(link_sh_pin, HIGH);
    delay(linkSpeed_5);
    digitalWrite(link_lg_pin, LOW);
    digitalWrite(link_sh_pin, LOW);
    delay(linkSpeed_5);
  }
}

bool readBtn() {
  return !digitalRead(startBtn);
}

//// ---- Main
void setup() {
  Serial.begin(115200);

  // Set pins
  pinMode(en, OUTPUT);
  pinMode(link_lg_pin, OUTPUT);
  pinMode(link_lg_dir, OUTPUT);
  pinMode(link_sh_pin, OUTPUT);
  pinMode(link_sh_dir, OUTPUT);
  pinMode(feeder_pin, OUTPUT);
  pinMode(feeder_dir, OUTPUT);
  pinMode(eject, OUTPUT);
  pinMode(airPump, OUTPUT);
  pinMode(startBtn, INPUT);
  servo.attach(servoPin);

  // Reset every actuator
  servo.write(origin);
  digitalWrite(en, LOW);
  digitalWrite(eject, LOW);
  digitalWrite(airPump, LOW);

  // Wait for start btn
  while (!readBtn) {
    delay(100);
  }
}

void loop() {

  // Feed ball
  moveTo(feeder_pin, feeder_dir, 1, linkSpeed_4, 60);
  delay(1000);

  // Send responce to CPU
  Serial.println("Begin");

  // Wait for command from CPU
  while (true) {
    if (Serial.available()) {
      msg = Serial.parseInt();
      if (msg == 2 || msg == 1) {
        break;
      }
    }
  }

  switch (msg) {
    // Qualified
    case 2:

      // Activate air pump
      digitalWrite(airPump, HIGH);

      // Move to inspection zone
      moveTo(link_sh_pin, link_sh_dir, 0, linkSpeed_5, 90);
      moveToSimo(0, 75, 0, 105, linkSpeed_5);
      delay(500);

      // Grab the ball
      servo.write(outStroke);
      delay(2000);
      servo.write(origin);
      delay(500);

      // Move to drop zone
      moveTo(link_sh_pin, link_sh_dir, 1, linkSpeed_5, 105);
      moveToSimo(0, 90, 0, 15, linkSpeed_4);
      delay(1000);
      moveMid(0);

      // Deativate air pump
      digitalWrite(airPump, LOW);
      delay(1000);

      // Back to original position
      moveMid(1);
      moveTo(link_sh_pin, link_sh_dir, 1, linkSpeed_5, 105);
      moveToSimo(1, 165, 1, 105, linkSpeed_4);
      break;

    // Ejected
    case 1:
      digitalWrite(eject, HIGH);
      delay(1000);
      digitalWrite(eject, LOW);
      break;
  }
}
