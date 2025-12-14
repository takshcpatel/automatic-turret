#define X_LIMIT_PIN 9
#define X_STEP_PIN 2
#define X_DIR_PIN 5

#define Y_STEP_PIN 3
#define Y_DIR_PIN 6

#define ALL_ENABLE_PIN 8

const float ANG_PER_STEP = 0.1125;
int tilt_angle = 0;
int pan_angle = 180;

int LIMIT_STATUS = 0;

void setup() {
  Serial.begin(115200);

  pinMode(X_STEP_PIN, OUTPUT);
  pinMode(X_DIR_PIN, OUTPUT);
  pinMode(X_LIMIT_PIN, INPUT_PULLUP);

  pinMode(Y_DIR_PIN, OUTPUT);
  pinMode(Y_STEP_PIN, OUTPUT);

  pinMode(ALL_ENABLE_PIN, OUTPUT);

  digitalWrite(ALL_ENABLE_PIN, LOW);  // enable driver (LOW = ON)
  delay(3000);
  homeX();
  delay(1000);
  gotoXY(50, 50);
  gotoXY(0, 0);
}

char rxBuf[32];
byte rxIdx = 0;

void loop() {
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

void homeX() {
  // Serial.println("Homing X...");

  while (digitalRead(X_LIMIT_PIN) == LOW) {
    stepY(0);
    delay(5);
  }
  delay(50);

  // Serial.println("limit hit, backing off...");

  for (int i = 0; i < 30; i++) {
    stepY(1);
    delay(5);
  }

  // Serial.println("switch released");

  tilt_angle = 0;
  LIMIT_STATUS = 0;
  Serial.println("[!] Homed X");
  delay(200);
}

void parseGcode(char *cmd) {

  int gcode;
  int x, y;

  Serial.print("RX: [");
  Serial.print(cmd);
  Serial.println("]");

  // parse: G<number> <x> <y>
  int count = sscanf(cmd, "G%d %d %d", &gcode, &x, &y);

  if (count != 3) {
    Serial.println("[ERR] Bad command format");
    return;
  }

  if (gcode == 0) {
    Serial.println("[G0] Incremental move");
    moveX(x);
    moveY(y);
  }
  else if (gcode == 1) {
    Serial.println("[G1] Coordinated move");
    gotoXY(x, y);
  }
  else {
    Serial.println("[ERR] Unsupported G code");
  }
}


void gotoXY(int x_deg, int y_deg) {
  int dx = x_deg - pan_angle;
  int dy = y_deg - tilt_angle;

  long stepsX = abs(round(dx / ANG_PER_STEP));
  long stepsY = abs(round(dy / ANG_PER_STEP));

  int dirX = (dx >= 0) ? 1 : 0;
  int dirY = (dy >= 0) ? 1 : 0;

  long maxSteps = max(stepsX, stepsY);

  long x_acc = 0;
  long y_acc = 0;

  for (long i = 0; i < maxSteps; i++) {
    x_acc += stepsX;
    y_acc += stepsY;

    if (x_acc >= maxSteps) {
      stepX(dirX);
      x_acc -= maxSteps;
    }

    if (y_acc >= maxSteps) {
      if (digitalRead(X_LIMIT_PIN) == HIGH) {
        Serial.println("[!!!] LIMIT PRESSED");
        break;
      }
      stepY(dirY);
      y_acc -= maxSteps;
    }
    delayMicroseconds(600);  // speed control
  }
  pan_angle = x_deg;
  tilt_angle = y_deg;
  Serial.println("[!] Completed gotoXY");
}

void gotoX(int degrees) {
  int angleError = (degrees - pan_angle);
  moveX(angleError);
  pan_angle = degrees;
}

void gotoY(int degrees) {
  if (degrees < 2) {
    int angleError = (2 - tilt_angle);
    moveY(angleError);
    Serial.println("[!] Reached Soft Limit");
  } else {
    int angleError = (degrees - tilt_angle);
    moveY(angleError);
  }
  tilt_angle = degrees;
}

void moveX(int incremental_degrees) {
  float STEPS_TO_MOVE = incremental_degrees / ANG_PER_STEP;
  STEPS_TO_MOVE = abs(round(STEPS_TO_MOVE));

  int STEP_COUNT = 0;
  int direction = (incremental_degrees < 0) ? 0 : 1;
  incremental_degrees = abs(incremental_degrees);
  for (int STEP_COUNT = 0; STEP_COUNT < STEPS_TO_MOVE; STEP_COUNT++) {
    stepX(direction);
    delay(2);
  }

  pan_angle += incremental_degrees;
  Serial.println("[!] Completed moveX");
}

void moveY(int incremental_degrees) {
  float STEPS_TO_MOVE = incremental_degrees / ANG_PER_STEP;
  STEPS_TO_MOVE = abs(round(STEPS_TO_MOVE));

  int STEP_COUNT = 0;
  int direction = (incremental_degrees < 0) ? 0 : 1;
  incremental_degrees = abs(incremental_degrees);
  for (int STEP_COUNT = 0; STEP_COUNT < STEPS_TO_MOVE; STEP_COUNT++) {
    if (digitalRead(X_LIMIT_PIN) == LOW) {
      stepY(direction);
      delay(2);
    } else {
      Serial.println("[!!!] LIMIT PRESSED");
      LIMIT_STATUS = 1;
      break;
    }
  }
  if (LIMIT_STATUS == 0) {
    tilt_angle += incremental_degrees;
    Serial.println("[!] Completed moveY");
  }
}

void stepX(int dir) {
  if (dir == 1) {
    digitalWrite(X_DIR_PIN, HIGH);
  } else {
    digitalWrite(X_DIR_PIN, LOW);
  }
  digitalWrite(X_STEP_PIN, HIGH);
  delayMicroseconds(600);
  digitalWrite(X_STEP_PIN, LOW);
  delayMicroseconds(600);
}

void stepY(int dir) {
  if (dir == 1) {
    digitalWrite(Y_DIR_PIN, HIGH);
  } else {
    digitalWrite(Y_DIR_PIN, LOW);
  }
  digitalWrite(Y_STEP_PIN, HIGH);
  delayMicroseconds(600);
  digitalWrite(Y_STEP_PIN, LOW);
  delayMicroseconds(600);
}