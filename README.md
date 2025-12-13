# Vision-Guided Automatic Turret

An automated vision-guided turret built as a learning project to explore precise camera-to-motor control, real-time human detection, tracking, and system-level decision logic. The project focuses on integrating computer vision with embedded control systems in a controlled, experimental setup.

---

## ⚠️ Disclaimer

This project is for educational and experimental purposes only.  
It uses a non-lethal airsoft (plastic BB) mechanism and is **not intended for real-world security, harm, or weaponization**.  
The system is developed purely to study robotics, control systems, and computer vision concepts.

---

## Project Overview

This turret uses a camera-based vision system to detect and track humans in real time.  
It differentiates between **registered** and **unregistered** individuals and follows a staged response logic:

1. Detect human presence using computer vision  
2. Verify whether the detected person is registered  
3. Issue multiple warning stages if unregistered  
4. If warnings are ignored, the system tracks the target and shoots the target

The emphasis of this project is on **accuracy, timing, and coordination** between vision data and motor control rather than on the output mechanism itself.

---

## Key Learning Objectives

- Precise camera-to-motor calibration
- Real-time object detection and tracking
- Vision-based target following
- State-machine based decision making
- Embedded motor control (pan/tilt systems)
- Hardware–software integration
- Safety-aware system design

---

## Features 

- Real-time human detection using computer vision  
- Registered vs unregistered target differentiation  
- Multi-stage warning system  
- Smooth pan–tilt tracking control  
- Non-lethal airsoft actuation for testing  
- Modular and expandable architecture  

---

## System Architecture (Not Completed fully!)

- **Vision Module**  
  - Camera input  
  - Human detection and tracking  
  - Target position estimation  

- **Control Module**  
  - Pan–tilt motor control  
  - PID / motion smoothing (if implemented)  
  - Camera-to-motor mapping  

- **Decision Logic**  
  - Registration checks  
  - Warning stages  
  - Engagement  

- **Actuation Module**  
  - Non-lethal airsoft mechanism  
  - Triggered only after logic conditions are met  

---

## Technologies Used

- OpenCV
- RaspberryPi 5 and Arduino Uno R3
- Nema17 Stepper Motors with A4988 Drivers
- RaspberryPi Camera Module 3 (Wide)
- Python / C++ 
- Serial Communication for Arduino <--> RaspberryPi
- WiFi Communication HMI <--> RaspberryPi 

---

## Current Status

🚧 **Work in Progress**  

Implentations so far include:
- Homing
- Go-To Angle for Tilt
- GUI made with PyQT5
- HMI <--> RaspberryPi

---

## License

Free to use 😉, just mention name in sources and send me updates too!
---

## Author

Built as a personal robotics learning project.  
Feel free to explore, learn, and adapt the concepts — responsibly.
