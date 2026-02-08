# BOB THE GUN
This is an automatic turret inspired by the tf2's engineer's sentry gun. It detects and shoots threats if they do not comply from warning. I have made this project to learn about CAD, mechanical, computer vision, software->hardware communication, etc.

## Links
YouTube :- [Quack Robotics](https://www.youtube.com/@QuackRobotics)

Instagram :- [@quackrobotics](https://www.instagram.com/quackrobotics)

OnShape :- [OnShape CAD View](https://cad.onshape.com/documents/a227c9c3e91dedc730053277/w/3ffe9ea86f039fb92ebcc4d6/e/9ef318677793f062c9bceb51?renderMode=0&uiState=6988989fe881a3d28d2be3f7)

Hackclub Blueprint :- [Bob the Gun](https://blueprint.hackclub.com/projects/9715)

Hackclub Flavortown :- [Bob the Gun](https://flavortown.hackclub.com/projects/8451)


![Image of gun](https://github.com/takshcpatel/automatic-turret/blob/main/Image%20And%20Videos/IMG_4446.JPG?raw=true)

![Image of CAD](https://github.com/takshcpatel/automatic-turret/blob/main/Image%20And%20Videos/CAD.jpg?raw=true)

## Working 
### Mechanical
This is an electric airsoft gun ( EAG ) type of mechanism mounted on a Pan / Tilt Mechanism. It is has a pan freedom of **∞**º and a tilt freedom of about 70-80º. Uses a lazy susan bearing for the infinite pan motion and the camera is connected to a SG-90 Servo for a independent tilt motion.

### Software 
The computer vision and calculations are done in the [RaspberryPi 5](https://www.raspberrypi.com/products/raspberry-pi-5/). It receives frames from the [RaspberryPi Camera 3 Wide](https://www.raspberrypi.com/products/camera-module-3/). (For now) It detects an object based on color (currently yellow) and calculates the direction to move. It has a deadzone system for determining when to shoot.

### Hardware controlling 
The Nema17 motors are controlled by an Arduino Uno with the CNC Shield V3. The Arduino is connected to the RPi using a standard USB Type A - USB Type B. The RPi sends G-Code like commands to the Arduino to control the motors. 

The human interface is controlled directly from the python script using either ethernet cable (restricts movement) or by Wi-Fi  local network, it works completely offline if you want it. 

### Power 
I have used a 12V+ 10000mAh Li-Po battery which connects to the CNC Shield and a XH-M404 Buck converter. The XH-M404 outputs 5.25V+ for the RaspberryPi and the Servo Motors.

## Use cases and applications
- If built with better parts and task specifics, it can be a use-case of riot-control. Sounds absurd but something like a paintball bullet or similar can be used to mark out people who are to be arrested for adding violence to the riot.

- Similarly, It can be used for drone defense if used with a guns / signal jammers / net launchers, etc.

- Can used for home security. This type can be equipped with rubber bullets so it hurts enough the robbers / intruders but doesn't. Of course it will have some kind of manual confirmation before shooting. 

- There can be other similar use case in many fields, mainly for security but more is yet to be discovered.

## Hardware List
- RaspberryPi 5 8Gb

- RaspberryPi Camera 3 Wide

- Arduino Uno

- Arduino Uno CNC Shield 

- Orange NMC 18650 11.1V 10000mAh Battery

- Lazy Susan Bearing

- 3D Printed CAD Models

## Libraries

- OpenCV

- NumPy

- PyQt5

## Licenses 
Just use it however you want in your project. This is just an educational project made so that I can learn different things. 

## Inspiration 
![Cs2 Engineer](https://wiki.teamfortress.com/w/images/thumb/6/6a/Engineertaunt1.PNG/350px-Engineertaunt1.PNG)


## Contact 
E-Mail :- takshcpatel@gmail.com
Discord :- mrcjoc
 
