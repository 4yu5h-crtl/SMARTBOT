# 🤖 SMARTBOT - Intelligent Mobile-Controlled Robot

<div align="center">
  <img src="https://img.shields.io/badge/Platform-Arduino-blue" alt="Platform">
  <img src="https://img.shields.io/badge/Language-Python-green" alt="Language">
  <img src="https://img.shields.io/badge/ML-Computer%20Vision-orange" alt="ML">
  <img src="https://img.shields.io/badge/Control-Natural%20Language-yellow" alt="Control">
</div>

## 📋 Overview

SMARTBOT is an innovative robot control system that combines natural language processing, computer vision, and voice recognition to create an intuitive and intelligent control interface. The system uses a mobile phone as the primary interface, allowing users to control the robot through natural language commands and hand gestures.

## ✨ Key Features

- 🤖 **Natural Language Control**: Control your robot using voice commands and text input
- 👋 **Hand Gesture Recognition**: Control the robot using hand movements
- 📱 **Mobile Interface**: Cross-platform mobile app for easy control
- 🧠 **Local LLM Processing**: On-device language model for command interpretation
- 🎥 **Real-time Camera Feed**: Process and analyze camera input in real-time
- 🔊 **Voice Feedback**: Get audio feedback for your commands
- 🔄 **Real-time Control**: Instant response to commands and gestures

## 🛠️ System Architecture

```
[Phone App] <-> [Local LLM Server] <-> [Robot Control Server] <-> [ESP32 Robot]
```

### Components

1. **Mobile Application**
   - Flutter-based cross-platform app
   - Camera feed processing
   - Natural language input
   - Voice output
   - Robot control interface

2. **Local LLM Server**
   - TinyLlama model (1.1B parameters)
   - Local inference engine
   - Context-aware processing
   - Command interpretation

3. **Robot Control Server**
   - HTTP server
   - Command routing
   - Status monitoring
   - Error handling

4. **ESP32 Robot**
   - Motor control
   - Sensor integration
   - Web server
   - Command execution

## 📁 Project Structure

```
SMARTBOT/
├── Smartbot-ino/           # Arduino implementation
│   ├── SMARTBOT.ino        # Main robot control code
│   ├── DataParser.h        # Data parsing header
│   └── DataParser.cpp      # Data parsing implementation
├── Handtracker/            # Hand tracking implementation
│   └── handtracker.py      # Hand gesture recognition
└── keyboard_cam/           # Keyboard camera control
```

## 🚀 Getting Started

### Prerequisites

- Arduino IDE
- Python 3.x
- ESP32 Development Board
- Mobile device with camera
- Required Python packages:
  ```
  pip install opencv-python
  pip install mediapipe
  pip install numpy
  ```

### Installation

1. **Robot Setup**
   - Upload the `SMARTBOT.ino` sketch to your ESP32 board
   - Connect motors and sensors according to the pin configuration

2. **Hand Tracking Setup**
   - Install required Python packages
   - Run the handtracker.py script:
     ```bash
     python Handtracker/handtracker.py
     ```

3. **Mobile App Setup**
   - Install the Flutter app on your mobile device
   - Connect to the robot's WiFi network
   - Configure the app settings

## 🎮 Usage

1. **Natural Language Control**
   - Open the mobile app
   - Use voice or text input to give commands
   - The robot will respond to your commands

2. **Hand Gesture Control**
   - Run the hand tracking script
   - Use predefined hand gestures to control the robot
   - View real-time camera feed with gesture detection

3. **Keyboard Control**
   - Use the keyboard_cam interface for manual control
   - View live camera feed while controlling the robot

## 🔧 Configuration

### Robot Configuration
- Motor pins
- Sensor pins
- WiFi credentials
- Control parameters

### Hand Tracking Configuration
- Gesture recognition parameters
- Camera settings
- Control sensitivity


## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.
