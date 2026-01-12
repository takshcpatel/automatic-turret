# Vision-Guided Automatic Turret

An automated vision-guided turret built as a learning project to leanr and experiment with camera-to-motor control, real-time detection, tracking, and confidence in decision logic.

---

## ⚠️ Disclaimer

This project is for educational and experimental purposes only.  
It uses a non-lethal airsoft (plastic BB) mechanism and is **not intended for real-world security, harm, or weaponization**.  
The system is developed purely to study robotics, control systems, and computer vision concepts.

---

## Project Overview

This turret uses a camera-based vision system to detect and track humans in real time. ( I wish to add a time of flight camera for distance to target measurement )
It differentiates between actions that are **lethal** and **non-lethal** and responds accordingly:

1. Detect human presence using computer vision  
2. Track human actions to see if it is lethal to the machine or its briefcase ( tf2 reference )   
3. Alert using buzzer or LEDs  
4. If alerts are ignored, the system tracks the target and shoots the target

The emphasis of this project is on **accuracy, timing, and coordination** between vision data and motor control rather than on the output mechanism itself. (copium btw)

---

## Key Learning Objectives

- Camera to motor control 
- Real-time object detection and tracking
- Vision-based target following
- Confidence based decision making ( not yet developed )
- Mechanical CAD ( its my first time doing CAD for a big project )
- Develop HMI

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
  - Action detection 
  - Warning stages  
  - Engagement  

- **Actuation Module**  
  - Airsoft mechanism  
  - Triggered only after logic conditions are met  

---

## Things Used

- OpenCV
- RaspberryPi 5 and Arduino Uno R3 ( with CNC Shield )
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
- Tracking ( color based )
- Shooting ( A little inaccurate but increasing barrel lenght should fix it )
- GUI made with PyQT5
- HMI <--> RaspberryPi

---

## License

Free to use 😉, just mention name in sources and send me updates too!
---

## Author

** Taksh Patel **

Built as a personal robotics learning project.  
Feel free to explore and use.
