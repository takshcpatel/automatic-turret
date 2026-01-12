#include <AccelStepper.h>
#include <Servo.h>
#include <Arduino.h> 

#define X_STEP_PIN 2
#define X_DIR_PIN 5

#define Y_STEP_PIN 3
#define Y_DIR_PIN 6

#define Z_STEP_PIN 4
#define Z_DIR_PIN 7

#define X_LIMIT_PIN 9
#define ALL_ENABLE_PIN 8
#define SERVO_PIN 11

Servo tiltServo;

const float ANG_PER_STEP = 0.1125;

int pan_angle = 0;
int tilt_angle = 0;
int tiltServo_angle = 93;

int X_SPEED = 5000;
int Y_SPEED = 3000;
bool LIMIT_STATUS = false;
bool SNAP_ACTIVE = false;
bool SHOOT_READY = false;


AccelStepper stepperX(AccelStepper::DRIVER, X_STEP_PIN, X_DIR_PIN);
AccelStepper stepperY(AccelStepper::DRIVER, Y_STEP_PIN, Y_DIR_PIN);
AccelStepper stepperZ(AccelStepper::DRIVER, Z_STEP_PIN, Z_DIR_PIN);

char rxBuf[32];
byte rxIdx = 0;

void homeX();
void moveXY(int x_deg, int y_deg);
void gotoXY(int x_deg, int y_deg);
void snapMoveXY(int x_deg, int y_deg);
void shoot();
void parseGcode(char *cmd);

long angleToSteps(int deg)
{
  return lround((float)deg / ANG_PER_STEP);
}

void setup()
{
  Serial.begin(115200);

  tiltServo.attach(SERVO_PIN);
  tiltServo.write(tiltServo_angle);

  pinMode(X_LIMIT_PIN, INPUT_PULLUP);
  pinMode(ALL_ENABLE_PIN, OUTPUT);
  digitalWrite(ALL_ENABLE_PIN, LOW);

  stepperX.setMaxSpeed(5000);
  stepperX.setAcceleration(800);

  stepperY.setMaxSpeed(1500);
  stepperY.setAcceleration(800);

  stepperZ.setMaxSpeed(1500);
  stepperZ.setAcceleration(800);

  delay(2000);
  homeX();
}

void loop()
{
  if (!SNAP_ACTIVE)
  {
    stepperX.run();
    stepperY.run();
  }
  // keep Z running in background when SHOOT_READY
  if (SHOOT_READY) {
    stepperZ.runSpeed();
  }

  while (Serial.available())
  {
    char c = Serial.read();
    if (c == '\n')
    {
      rxBuf[rxIdx] = '\0';
      rxIdx = 0;
      parseGcode(rxBuf);
    }
    else if (rxIdx < sizeof(rxBuf) - 1)
    {
      rxBuf[rxIdx++] = c;
    }
  }

  shoot();
}

void homeX()
{
  stepperY.setSpeed(-400);
  while (digitalRead(X_LIMIT_PIN) == LOW)
  {
    stepperY.runSpeed();
    if (SHOOT_READY) stepperZ.runSpeed();
  }

  tiltServo.write(93);
  tiltServo_angle = 93;
  stepperY.move(40);
  stepperY.runToPosition();
  tilt_angle = 0;
  LIMIT_STATUS = false;
}

void moveXY(int x_deg, int y_deg)
{
  long sx = angleToSteps(x_deg) * 6.5;
  long sy = angleToSteps(y_deg) * 2;

  stepperX.move(sx);
  stepperY.move(sy);

  while (stepperX.distanceToGo() != 0 ||
         stepperY.distanceToGo() != 0)
  {
    if (digitalRead(X_LIMIT_PIN) == HIGH)
    {
      stepperX.stop();
      stepperY.stop();
      LIMIT_STATUS = true;
      break;
    }
    stepperX.run();
    stepperY.run();
    if (SHOOT_READY) stepperZ.runSpeed();
  }

  pan_angle += x_deg;
  tilt_angle += y_deg;
}

void gotoXY(int x_deg, int y_deg)
{
  int dx = x_deg - pan_angle;
  int dy = y_deg - tilt_angle;

  long sx = angleToSteps(dx) * 6.5;
  long sy = angleToSteps(dy) * 2;

  stepperX.move(sx);
  stepperY.move(sy);

  while (stepperX.distanceToGo() != 0 ||
         stepperY.distanceToGo() != 0)
  {
    if (digitalRead(X_LIMIT_PIN) == HIGH)
    {
      stepperX.stop();
      stepperY.stop();
      LIMIT_STATUS = true;
      break;
    }
    stepperX.run();
    stepperY.run();
    if (SHOOT_READY) stepperZ.runSpeed();
  }

  pan_angle = x_deg;
  tilt_angle = y_deg;
}

int tiltToServo(int tilt_deg)
{
  tilt_deg = constrain(tilt_deg, 0, 70);
  return 93 + (tilt_deg * 87) / 70;
}

void snapMoveXY(int x_deg, int y_deg)
{
  SNAP_ACTIVE = true;
  
  long sx = angleToSteps(x_deg) * 6.5;
  long tx = stepperX.currentPosition() + sx;

  long sy = angleToSteps(y_deg) * 2;
  long ty = stepperY.currentPosition() + sy;

  stepperX.setSpeed((sx > 0) ? X_SPEED : -X_SPEED);
  stepperY.setSpeed((sy > 0) ? Y_SPEED : -Y_SPEED);

  if (tilt_angle + y_deg >= 0)
  {
    while (stepperX.currentPosition() != tx ||
           stepperY.currentPosition() != ty)
    {
      if (digitalRead(X_LIMIT_PIN) == HIGH)
      {
        stepperX.stop();
        LIMIT_STATUS = true;
        break;
      }
      if (stepperX.currentPosition() != tx) stepperX.runSpeed();
      if (stepperY.currentPosition() != ty) stepperY.runSpeed();
      if (SHOOT_READY) stepperZ.runSpeed();
    }

    tilt_angle += y_deg;
    tilt_angle = constrain(tilt_angle, 0, 70);
  }
  else
  {
    tilt_angle = 0;
    Serial.println("[!!] Min Tilt Reached ignoring remaining path");
  }

  stepperX.setSpeed(0);
  stepperY.setSpeed(0);
  pan_angle += x_deg;

  tiltServo_angle = tiltToServo(tilt_angle);
  tiltServo.write(tiltServo_angle);

  SNAP_ACTIVE = false;
}

// void shoot(){
//   if (SHOOT_READY){
//     stepperZ.runSpeed();
//   }
// }

void disableBonner()
{
  digitalWrite(ALL_ENABLE_PIN, HIGH);
}

void enableBonner()
{
  digitalWrite(ALL_ENABLE_PIN, LOW);
}

void parseGcode(char *cmd)
{
  int g = -1, x = 0, y = 0, x_spd = 0, y_spd = 0;
  int count = sscanf(cmd, "G%d %d %d %d", &g, &x, &y, &x_spd, &y_spd);
  if (count < 1) return;

  if (g == 0 && count == 3)
    moveXY(x, y);
  else if (g == 1 && count == 3)
    gotoXY(x, y);
  else if (g == 2 && count == 4){
    snapMoveXY(x, y);
    X_SPEED = x_spd;
    Y_SPEED = y_spd;}
  else if (g == 11){
    stepperZ.setSpeed(300);
    SHOOT_READY = true;}
  else if (g == 12){
    stepperZ.setSpeed(0);
    SHOOT_READY = false;}
  else if (g == 28)
    homeX();
  else if (g == 98)
    enableBonner();
  else if (g == 99)
    disableBonner();
}
