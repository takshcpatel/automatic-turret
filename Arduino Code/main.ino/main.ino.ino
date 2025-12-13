#define X_LIMIT_PIN 9
#define X_STEP_PIN 2
#define X_DIR_PIN 5
#define X_ENABLE_PIN 8

const float ANG_PER_STEP = 0.1125;
int x_angle = 95;

int LIMIT_STATUS = 0;

void setup() {
  Serial.begin(115200);
  pinMode(X_STEP_PIN, OUTPUT);
  pinMode(X_DIR_PIN, OUTPUT);
  pinMode(X_ENABLE_PIN, OUTPUT);
  pinMode(X_LIMIT_PIN, INPUT_PULLUP);

  digitalWrite(X_ENABLE_PIN, LOW);  // Enable driver (LOW = ON)
  delay(3000);
  homeX();
  delay(1000);
  moveX(50);
  delay(20);
  moveX(-60);
}

void loop() {
}

void homeX() {
  // Serial.println("Homing X...");

  while (digitalRead(X_LIMIT_PIN) == LOW) {
    stepX(0);
    delay(5);
  }
  delay(50);

  // Serial.println("limit hit, backing off...");

  for (int i = 0; i < 30; i++) {
    stepX(1);
    delay(5);
  }

  // Serial.println("switch released");

  x_angle = 90;
  LIMIT_STATUS = 0;
  Serial.println("[!] Homed X");
  delay(200);
}


void moveX(int degrees) {
  float STEPS_TO_MOVE = degrees / ANG_PER_STEP;
  STEPS_TO_MOVE = abs(round(STEPS_TO_MOVE));

  int STEP_COUNT = 0;
  int direction = (degrees < 0) ? 0 : 1;
  degrees = abs(degrees);
  for (int STEP_COUNT = 0; STEP_COUNT < STEPS_TO_MOVE; STEP_COUNT++) {
    if (digitalRead(X_LIMIT_PIN) == LOW) {
      stepX(direction);
      delay(2);
    } else {
      Serial.println("[!!!] LIMIT PRESSED");
      LIMIT_STATUS = 1;
      break;
    }
  }
  if (LIMIT_STATUS == 0) {
    Serial.println("[!] Completed moveX");
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