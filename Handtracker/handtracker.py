import cv2
import mediapipe as mp
import math
import requests
import numpy as np
from collections import deque
from datetime import datetime
import time

# Robot HTTP settings
robot_url = "http://192.168.29.100/control"

# Initialize MediaPipe Hands with higher accuracy settings
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.8,
    min_tracking_confidence=0.8
)
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles  # Add drawing styles for better visualization

# Initialize VideoCapture
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# Set window size
cv2.namedWindow('Hand Tracking', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Hand Tracking', 1280, 720)

# Frame dimensions
height = 720
width = 1280

# Calculate box coordinates
center_x = width // 2
center_y = height // 2
top_box_top_left = (center_x - 100, 0)
top_box_bottom_right = (center_x + 100, 200)
bottom_box_top_left = (center_x - 100, height - 200)
bottom_box_bottom_right = (center_x + 100, height)

class GestureParams:
    def __init__(self):
        self.angle_buffer = deque(maxlen=3)
        self.command_buffer = deque(maxlen=3)
        self.last_command = "s"
        self.last_command_time = datetime.now()
        self.command_cooldown = 0.05
        self.default_speed = 160
        # Add tracking parameters
        self.min_detection_confidence = 0.8
        self.min_tracking_confidence = 0.8

gesture_params = GestureParams()

def calculate_finger_positions(landmarks):
    """Calculate normalized finger positions for better tracking"""
    try:
        # Convert landmarks to numpy arrays for easier calculation
        points = np.array([[lm.x, lm.y, lm.z] for lm in landmarks])
        
        # Get key finger positions
        index_tip = points[8]
        middle_tip = points[12]
        ring_tip = points[16]
        
        # Calculate relative positions to wrist
        wrist = points[0]
        relative_positions = {
            'index': index_tip - wrist,
            'middle': middle_tip - wrist,
            'ring': ring_tip - wrist
        }
        
        return relative_positions
    except Exception as e:
        print(f"Error calculating finger positions: {e}")
        return None

def sendToRobot(command, speed=160):
    """Send command to robot via HTTP"""
    try:
        url = f"{robot_url}?command={command}&speed={speed}"
        print(f"Sending: {url}")
        response = requests.get(url, timeout=1)
        if response.status_code == 200:
            print("Command sent successfully")
            return True
        else:
            print(f"Failed to send command: {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"Error sending command: {e}")
        return False

def process_frame(frame, params):
    """Process frame with enhanced tracking and box-based gesture detection"""
    try:
        # Convert to RGB
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(image_rgb)
        
        command = "s"  # Default command
        label = "Stop"
        speed = params.default_speed
        turn = False
        
        # Draw boxes with transparency
        overlay = frame.copy()
        cv2.rectangle(overlay, top_box_top_left, top_box_bottom_right, (0, 0, 255), -1)
        cv2.rectangle(overlay, bottom_box_top_left, bottom_box_bottom_right, (0, 0, 255), -1)
        cv2.addWeighted(overlay, 0.2, frame, 0.8, 0, frame)  # Add transparent overlay
        
        # Draw box outlines
        cv2.rectangle(frame, top_box_top_left, top_box_bottom_right, (0, 0, 255), 2)
        cv2.rectangle(frame, bottom_box_top_left, bottom_box_bottom_right, (0, 0, 255), 2)
        
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            
            # Enhanced landmark visualization
            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style()
            )
            
            # Get landmark coordinates with improved precision
            landmarks = []
            for landmark in hand_landmarks.landmark:
                x = int(landmark.x * width)
                y = int(landmark.y * height)
                landmarks.append((x, y))
            
            # Calculate finger positions for better tracking
            finger_positions = calculate_finger_positions(hand_landmarks.landmark)
            
            # Key landmarks with enhanced precision
            wrist = landmarks[0]
            middle_mcp = landmarks[9]
            ring_mcp = landmarks[13]
            
            # Draw palm direction line with enhanced visibility
            cv2.line(frame, wrist, middle_mcp, (0, 255, 0), 3)  # Thicker line
            cv2.circle(frame, wrist, 5, (0, 255, 0), -1)  # Add point at wrist
            cv2.circle(frame, middle_mcp, 5, (0, 255, 0), -1)  # Add point at MCP
            
            # Calculate rotation angle with improved precision
            angle = math.atan2(wrist[1] - middle_mcp[1], wrist[0] - middle_mcp[0])
            angle = math.degrees(angle) - 90
            if angle <= -180:
                angle += 360
            elif angle > 180:
                angle -= 360
            
            # Smooth angle with weighted average
            params.angle_buffer.append(angle)
            weights = np.array([0.5, 0.3, 0.2])  # More weight to recent angles
            smoothed_angle = np.average(list(params.angle_buffer), weights=weights[:len(params.angle_buffer)])
            
            # Enhanced angle visualization
            cv2.putText(frame, f"Angle: {smoothed_angle:.1f}°", (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Improved turning detection with deadzone
            if smoothed_angle > 20:
                command = "r"
                label = "Right"
                turn = True
            elif smoothed_angle < -20:
                command = "l"
                label = "Left"
                turn = True
            else:
                turn = False
            
            # Box-based forward/backward logic with improved precision
            if not turn:
                if (top_box_top_left[0] < landmarks[9][0] < top_box_bottom_right[0] and
                    top_box_top_left[1] < landmarks[9][1] < top_box_bottom_right[1] and
                    top_box_top_left[0] < landmarks[13][0] < top_box_bottom_right[0] and
                    top_box_top_left[1] < landmarks[13][1] < top_box_bottom_right[1]):
                    command = "f"
                    label = "Forward"
                elif (bottom_box_top_left[0] < landmarks[9][0] < bottom_box_bottom_right[0] and
                      bottom_box_top_left[1] < landmarks[9][1] < bottom_box_bottom_right[1] and
                      bottom_box_top_left[0] < landmarks[13][0] < bottom_box_bottom_right[0] and
                      bottom_box_top_left[1] < landmarks[13][1] < bottom_box_bottom_right[1]):
                    command = "b"
                    label = "Backward"
            
            # Enhanced command visualization
            cv2.putText(frame, label, (wrist[0], wrist[1] - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Command: {label}", (50, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, f"Speed: {speed}", (50, 150), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        return command, speed, frame
    
    except Exception as e:
        print(f"Error processing frame: {e}")
        return "s", 0, frame

# Main loop
try:
    print("Starting hand gesture control. Press 'q' to quit.")
    print(f"HTTP Mode - Connecting to robot at {robot_url}")
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        frame = cv2.flip(frame, 1)
        command, speed, processed_frame = process_frame(frame, gesture_params)
        
        # Enhanced command smoothing
        gesture_params.command_buffer.append(command)
        most_common_command = max(set(gesture_params.command_buffer), 
                                key=gesture_params.command_buffer.count)
        
        # Improved command timing
        current_time = datetime.now()
        time_diff = (current_time - gesture_params.last_command_time).total_seconds()
        
        if (most_common_command != gesture_params.last_command and 
            time_diff >= gesture_params.command_cooldown):
            if sendToRobot(most_common_command, speed):
                gesture_params.last_command = most_common_command
                gesture_params.last_command_time = current_time
        
        cv2.imshow('Hand Tracking', processed_frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except Exception as e:
    print(f"Error in main loop: {e}")

finally:
    print("Shutting down...")
    # Send stop command
    sendToRobot("s", 0)
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()