#include <AccelStepper.h>

#define X_STEP_PIN 2
#define X_DIR_PIN  5

#define Y_STEP_PIN 3
#define Y_DIR_PIN  6

#define X_LIMIT_PIN 9
#define ALL_ENABLE_PIN 8

const float ANG_PER_STEP = 0.1125;

int pan_angle  = 180;
int tilt_angle = 0;

bool LIMIT_STATUS = false;

AccelStepper stepperX(AccelStepper::DRIVER, X_STEP_PIN, X_DIR_PIN);
AccelStepper stepperY(AccelStepper::DRIVER, Y_STEP_PIN, Y_DIR_PIN);

char rxBuf[32];
byte rxIdx = 0;

void setup() {
  Serial.begin(115200);

  pinMode(X_LIMIT_PIN, INPUT_PULLUP);
  pinMode(ALL_ENABLE_PIN, OUTPUT);
  digitalWrite(ALL_ENABLE_PIN, LOW);

  stepperX.setMaxSpeed(1500);
  stepperX.setAcceleration(800);

  stepperY.setMaxSpeed(1500);
  stepperY.setAcceleration(800);

  delay(2000);

  homeX();
  delay(500);

  gotoXY(50, 50);
  gotoXY(0, 0);
}

void loop() {
  stepperX.run();
  stepperY.run();

  while (Serial.available()) {
    char c = Serial.read();

    if (c == '\n') {
      rxBuf[rxIdx] = '\0';
      rxIdx = 0;
      parseGcode(rxBuf);
    } else if (rxIdx < sizeof(rxBuf) - 1) {
      rxBuf[rxIdx++] = c;
    }
  }
}

long angleToSteps(int deg) {
  return lround((float)deg / ANG_PER_STEP);
}

void homeX() {
  stepperY.setSpeed(-400);

  while (digitalRead(X_LIMIT_PIN) == LOW) {
    stepperY.runSpeed();
  }

  stepperY.move(40);
  stepperY.runToPosition();

  tilt_angle = 0;
  LIMIT_STATUS = false;
}

void moveX(int inc_deg) {
  long steps = angleToSteps(inc_deg) * 6.5;
  stepperX.move(steps);
  stepperX.runToPosition();

  pan_angle += inc_deg;
}

void moveY(int inc_deg) {
  if (digitalRead(X_LIMIT_PIN) == HIGH) {
    LIMIT_STATUS = true;
    return;
  }

  long steps = angleToSteps(inc_deg);
  stepperY.move(steps);
  stepperY.runToPosition();

  tilt_angle += inc_deg;
}

void gotoXY(int x_deg, int y_deg) {
  int dx = x_deg - pan_angle;
  int dy = y_deg - tilt_angle;

  long sx = angleToSteps(dx);
  long sy = angleToSteps(dy);

  stepperX.move(sx);
  stepperY.move(sy);

  while (stepperX.distanceToGo() != 0 ||
         stepperY.distanceToGo() != 0) {

    if (digitalRead(X_LIMIT_PIN) == HIGH) {
      stepperX.stop();
      stepperY.stop();
      LIMIT_STATUS = true;
      break;
    }

    stepperX.run();
    stepperY.run();
  }

  pan_angle  = x_deg;
  tilt_angle = y_deg;
}

void parseGcode(char *cmd) {
  int g, x, y;

  int count = sscanf(cmd, "G%d %d %d", &g, &x, &y);
  if (count != 3) return;

  if (g == 0) {
    moveX(x);
    moveY(y);
  }
  else if (g == 1) {
    gotoXY(x, y);
  }
}
