#include <WiFi.h>
#include <WebServer.h>
#include <Arduino.h>
#include "DataParser.h"

// WiFi credentials
const char* ssid = "JioFiber-4G";
const char* password = "123456789";

// Static IP configuration
IPAddress staticIP(192, 168, 29, 100);  // Robot's new static IP
IPAddress gateway(192, 168, 29, 1);     // Your router's gateway
IPAddress subnet(255, 255, 255, 0);     // Your subnet mask
IPAddress dns(8, 8, 8, 8);              // Optional: Google's DNS

// Create a web server on port 80
WebServer server(80);

DataParser dataParser;

// Motor control pins
int in1 = 27;  // Left motor input 1
int in2 = 26;  // Left motor input 2
int ena = 14;  // Left motor enable
int in3 = 25;  // Right motor input 1
int in4 = 33;  // Right motor input 2
int enb = 32;  // Right motor enable

int Speed = 50;       // Default speed value
int Right_speed = 0;  // Right motor speed value
int Left_speed = 0;   // Left motor speed value

// HTML for the web interface
const char index_html[] PROGMEM = R"rawliteral(
<!DOCTYPE HTML>
<html>
<head>
  <title>Freebot Control Panel</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { font-family: Arial, sans-serif; text-align: center; margin: 0; padding: 20px; }
    .controls { display: flex; flex-direction: column; align-items: center; gap: 10px; margin: 20px auto; }
    .row { display: flex; justify-content: center; gap: 10px; }
    button {
      width: 80px;
      height: 80px;
      font-size: 24px;
      border-radius: 10px;
      border: none;
      background-color: #4CAF50;
      color: white;
      cursor: pointer;
      touch-action: manipulation;
    }
    button:active { background-color: #388E3C; }
    #stopBtn { background-color: #F44336; width: 120px; height: 60px; margin-top: 10px; }
    #stopBtn:active { background-color: #D32F2F; }
    .speed-control { margin: 20px auto; width: 80%; max-width: 300px; }
    input[type="range"] { width: 100%; }
    #speedValue { font-size: 24px; margin: 10px 0; }
  </style>
</head>
<body>
  <h1>Freebot Control Panel</h1>
  
  <div class="controls">
    <div class="row">
      <button id="forwardBtn" ontouchstart="sendCommand('f')" ontouchend="sendCommand('s')" onmousedown="sendCommand('f')" onmouseup="sendCommand('s')">F</button>
    </div>
    <div class="row">
      <button id="leftBtn" ontouchstart="sendCommand('l')" ontouchend="sendCommand('s')" onmousedown="sendCommand('l')" onmouseup="sendCommand('s')">L</button>
      <button id="stopBtn" onclick="sendCommand('s')">STOP</button>
      <button id="rightBtn" ontouchstart="sendCommand('r')" ontouchend="sendCommand('s')" onmousedown="sendCommand('r')" onmouseup="sendCommand('s')">R</button>
    </div>
    <div class="row">
      <button id="backwardBtn" ontouchstart="sendCommand('b')" ontouchend="sendCommand('s')" onmousedown="sendCommand('b')" onmouseup="sendCommand('s')">B</button>
    </div>
  </div>
  
  <div class="speed-control">
    <h2>Speed Control</h2>
    <input type="range" id="speedSlider" min="0" max="255" value="50" oninput="updateSpeed(this.value)">
    <div id="speedValue">Speed: 50</div>
  </div>

  <script>
    var currentSpeed = 50;
    
    function updateSpeed(speed) {
      currentSpeed = speed;
      document.getElementById('speedValue').innerHTML = 'Speed: ' + speed;
    }
    
    function sendCommand(cmd) {
      var xhr = new XMLHttpRequest();
      xhr.open('GET', '/control?command=' + cmd + '&speed=' + currentSpeed, true);
      xhr.send();
    }
  </script>
</body>
</html>
)rawliteral";

void setup() {
  Serial.begin(115200);
  
  // Set motor control pins as outputs
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  pinMode(ena, OUTPUT);
  pinMode(in3, OUTPUT);
  pinMode(in4, OUTPUT);
  pinMode(enb, OUTPUT);
  
  // Stop motors at startup
  Stop();
  
  // Configure static IP
  if (!WiFi.config(staticIP, gateway, subnet, dns)) {
    Serial.println("Static IP configuration failed");
  }
  
  // Connect to WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println();
  Serial.print("Connected to WiFi! IP address: ");
  Serial.println(WiFi.localIP());
  
  // Define web server routes
  server.on("/", HTTP_GET, handleRoot);
  server.on("/control", HTTP_GET, handleControl);
  
  // Start web server
  server.begin();
  Serial.println("Web server started");
  Serial.println("Visit this IP in your browser to control the robot: " + WiFi.localIP().toString());
}

void loop() {
  server.handleClient();
}

// Serve the main web page
void handleRoot() {
  server.send(200, "text/html", index_html);
}

// Process control commands
void handleControl() {
  String command = server.arg("command");
  String speedStr = server.arg("speed");
  
  // Parse speed value
  int speedValue = 50; // Default
  if (speedStr.length() > 0) {
    speedValue = speedStr.toInt();
  }
  
  // Set speeds for both motors
  Left_speed = speedValue;
  Right_speed = speedValue;
  
  // Execute command
  if (command == "f") {
    forward(Left_speed, Right_speed);
    Serial.println("Forward");
  } 
  else if (command == "b") {
    backward(Left_speed, Right_speed);
    Serial.println("Backward");
  } 
  else if (command == "l") {
    left(Left_speed, Right_speed);
    Serial.println("Left");
  } 
  else if (command == "r") {
    right(Left_speed, Right_speed);
    Serial.println("Right");
  } 
  else if (command == "s") {
    Stop();
    Serial.println("Stop");
  }
  
  // Send OK response
  server.send(200, "text/plain", "OK");
}

// Motor control functions
void forward(int left_speed, int right_speed) {
  digitalWrite(in1, HIGH);
  digitalWrite(in2, LOW);
  digitalWrite(in3, HIGH);
  digitalWrite(in4, LOW);
  analogWrite(ena, left_speed);
  analogWrite(enb, right_speed);
}

void backward(int left_speed, int right_speed) {
  digitalWrite(in1, LOW);
  digitalWrite(in2, HIGH);
  digitalWrite(in3, LOW);
  digitalWrite(in4, HIGH);
  analogWrite(ena, left_speed);
  analogWrite(enb, right_speed);
}

void left(int left_speed, int right_speed) {
  digitalWrite(in1, HIGH);
  digitalWrite(in2, LOW);
  digitalWrite(in3, LOW);
  digitalWrite(in4, HIGH);
  analogWrite(ena, left_speed);
  analogWrite(enb, right_speed);
}

void right(int left_speed, int right_speed) {
  digitalWrite(in1, LOW);
  digitalWrite(in2, HIGH);
  digitalWrite(in3, HIGH);
  digitalWrite(in4, LOW);
  analogWrite(ena, left_speed);
  analogWrite(enb, right_speed);
}

void motor_speed(int Right_Speed, int Left_Speed) {
  Left_speed = Left_Speed;
  Right_speed = Right_Speed;
}

void Stop() {
  digitalWrite(in1, LOW);
  digitalWrite(in2, LOW);
  digitalWrite(in3, LOW);
  digitalWrite(in4, LOW);
  analogWrite(ena, 0);
  analogWrite(enb, 0);
}