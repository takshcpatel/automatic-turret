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

bool LIMIT_STATUS = false;
bool SNAP_ACTIVE = false;
bool CUMSHOT_READY = false;

AccelStepper stepperX(AccelStepper::DRIVER, X_STEP_PIN, X_DIR_PIN);
AccelStepper stepperY(AccelStepper::DRIVER, Y_STEP_PIN, Y_DIR_PIN);
AccelStepper stepperZ(AccelStepper::DRIVER, Z_STEP_PIN, Z_DIR_PIN);

char rxBuf[32];
byte rxIdx = 0;

void homeX();
void snapMoveXY(int x_deg, int y_deg);
void cumshot();
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

  stepperY.setMaxSpeed(4000);
  stepperY.setAcceleration(800);

  stepperZ.setMaxSpeed(5000);
  stepperZ.setAcceleration(300);

  delay(2000);
  homeX();
}

void loop()
{
  if (LIMIT_STATUS){
    homeX();
  }
  if (!SNAP_ACTIVE)
  {
    stepperX.run();
    stepperY.run();
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
  cumshot();
}

void homeX()
{
  stepperY.setSpeed(-400);
  while (digitalRead(X_LIMIT_PIN) == LOW)
  {
    stepperY.runSpeed();
  }

  tiltServo.write(93);
  tiltServo_angle = 93;
  stepperY.move(40);
  stepperY.runToPosition();
  tilt_angle = 0;
  LIMIT_STATUS = false;
}

int tiltToServo(int tilt_deg)
{
  tilt_deg = constrain(tilt_deg, 0, 70);
  return 93 + (tilt_deg * 87) / 70;
}

void snapMoveXY(int x_deg, int y_deg, int x_speed, int y_speed)
{
  SNAP_ACTIVE = true;
  
  long sx = angleToSteps(x_deg) * 6.5;
  long tx = stepperX.currentPosition() + sx;

  long sy = angleToSteps(y_deg) * 2;
  long ty = stepperY.currentPosition() + sy;

  stepperX.setSpeed((sx > 0) ? x_speed : -x_speed);
  stepperY.setSpeed((sy > 0) ? y_speed : -y_speed);

  if (tilt_angle + y_deg >= 0)
  {
    while (stepperX.currentPosition() != tx ||
           stepperY.currentPosition() != ty)
    {      
      if (digitalRead(X_LIMIT_PIN) == HIGH)
      {
        stepperX.stop();
        stepperY.stop();
        LIMIT_STATUS = true;
        break;
      }
      if (stepperX.currentPosition() != tx) stepperX.runSpeed();
      if (stepperY.currentPosition() != ty) stepperY.runSpeed();

      cumshot();
    }

    tilt_angle += y_deg;
    tilt_angle = constrain(tilt_angle, 0, 70);
  }
  else
  {
    tilt_angle = 0;
    // Serial.println("[!!] Min Tilt Reached ignoring remaining path");
  }

  stepperX.setSpeed(0);
  stepperY.setSpeed(0);
  pan_angle += x_deg;

  tiltServo_angle = tiltToServo(tilt_angle);
  tiltServo.write(tiltServo_angle);

  SNAP_ACTIVE = false;
}

void cumshot(){
  if(CUMSHOT_READY){
    stepperZ.setSpeed(300);
    stepperZ.runSpeed();
  } else {
    stepperZ.setSpeed(0);
    stepperZ.runSpeed();
  }
}

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
  int g = -1, x = 0, y = 0, x_speed = 0, y_speed = 0;
  int count = sscanf(cmd, "G%d %d %d %d %d", &g, &x, &y, &x_speed, &y_speed);
  if (count < 1) return;

  else if (g == 2 && count == 5)
    snapMoveXY(x, y, x_speed, y_speed);
  else if (g == 11)
    CUMSHOT_READY = true;
  else if (g == 12)
    CUMSHOT_READY = false;
  else if (g == 28)
    homeX();
  else if (g == 98)
    enableBonner();
  else if (g == 99)
    disableBonner();
}
