import cv2
import mediapipe as mp
import numpy as np
import math
import time  # ← Missing import added

class HandTracker:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Landmark indices
        self.tip_ids = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
        self.pip_ids = [3, 6, 10, 14, 18]
        self.mcp_ids = [2, 5, 9, 13, 17]
        
        # Cursor control finger (can switch between index and pinky)
        self.cursor_finger = 'index'  # 'index' or 'pinky'
        
        # Gesture stability
        self.gesture_history = []
        self.history_size = 5
        self.pinch_history = []
        self.pinch_stability_count = 3
        self.pinch_threshold = 40
        
    def set_cursor_finger(self, finger_type):
        """Set which finger to use for cursor control"""
        if finger_type in ['index', 'pinky']:
            self.cursor_finger = finger_type
            print(f"Cursor control switched to {finger_type} finger")
    
    def find_hands(self, frame):
        """Detect hands with improved processing"""
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)
            return results
        except Exception as e:
            print(f"Hand detection error: {e}")
            return None
    
    def get_landmarks(self, frame, results):
        """Extract hand landmarks with better visualization"""
        landmarks = []
        if results and results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                try:
                    # Draw landmarks with better visibility
                    self.mp_drawing.draw_landmarks(
                        frame, 
                        hand_landmarks, 
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3),
                        self.mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=2)
                    )
                    
                    # Extract positions
                    height, width, _ = frame.shape
                    for id, landmark in enumerate(hand_landmarks.landmark):
                        x, y = int(landmark.x * width), int(landmark.y * height)
                        landmarks.append([id, x, y])
                        
                        # Highlight cursor control finger
                        cursor_id = 8 if self.cursor_finger == 'index' else 20
                        if id == cursor_id:
                            cv2.circle(frame, (x, y), 8, (0, 255, 255), -1)  # Yellow highlight
                            
                except Exception as e:
                    print(f"Landmark extraction error: {e}")
                    continue
        
        return landmarks
    
    def get_finger_positions(self, landmarks):
        """Get finger positions with cursor finger highlighting"""
        if len(landmarks) < 21:
            return {}
        
        finger_positions = {}
        finger_names = ['thumb', 'index', 'middle', 'ring', 'pinky']
        
        try:
            for i, tip_id in enumerate(self.tip_ids):
                if tip_id < len(landmarks):
                    finger_positions[finger_names[i]] = {
                        'x': landmarks[tip_id][1],
                        'y': landmarks[tip_id][2],
                        'tip_id': tip_id
                    }
            
            # Add cursor control finger specific data
            cursor_tip_id = 8 if self.cursor_finger == 'index' else 20
            cursor_pip_id = 6 if self.cursor_finger == 'index' else 18
            
            if cursor_tip_id < len(landmarks):
                finger_positions['cursor_finger'] = {
                    'x': landmarks[cursor_tip_id][1],
                    'y': landmarks[cursor_tip_id][2],
                    'tip_id': cursor_tip_id
                }
            
            if cursor_pip_id < len(landmarks):
                finger_positions['cursor_finger_pip'] = {
                    'x': landmarks[cursor_pip_id][1],
                    'y': landmarks[cursor_pip_id][2]
                }
            
            # Keep thumb data for pinch detection
            if len(landmarks) > 4:
                finger_positions['thumb_tip'] = {
                    'x': landmarks[4][1],
                    'y': landmarks[4][2]
                }
                
        except Exception as e:
            print(f"Finger position calculation error: {e}")
        
        return finger_positions
    
    def calculate_distance(self, point1, point2):
        """Calculate distance between points"""
        try:
            return math.sqrt((point1['x'] - point2['x'])**2 + (point1['y'] - point2['y'])**2)
        except Exception as e:
            print(f"Distance calculation error: {e}")
            return float('inf')
    
    def is_finger_up(self, landmarks, finger_idx):
        """Enhanced finger detection with error handling"""
        try:
            if finger_idx == 0:  # Thumb
                if len(landmarks) <= 4:
                    return False
                thumb_tip = landmarks[4]
                thumb_ip = landmarks[3]
                wrist = landmarks[0]
                
                tip_dist = math.sqrt((thumb_tip[1] - wrist[1])**2 + (thumb_tip[2] - wrist[2])**2)
                ip_dist = math.sqrt((thumb_ip[1] - wrist[1])**2 + (thumb_ip[2] - wrist[2])**2)
                
                return tip_dist > ip_dist
            else:
                # For other fingers
                if finger_idx >= len(self.tip_ids) or finger_idx >= len(self.pip_ids):
                    return False
                    
                tip_id = self.tip_ids[finger_idx]
                pip_id = self.pip_ids[finger_idx]
                
                if tip_id >= len(landmarks) or pip_id >= len(landmarks):
                    return False
                
                tip = landmarks[tip_id]
                pip = landmarks[pip_id]
                
                return tip[2] < pip[2]  # Tip above PIP
        except Exception as e:
            print(f"Finger detection error for finger {finger_idx}: {e}")
            return False
    
    def detect_gestures(self, landmarks):
        """Enhanced gesture detection with cursor finger awareness"""
        try:
            if len(landmarks) < 21:
                return "no_hand"
            
            finger_positions = self.get_finger_positions(landmarks)
            fingers_up = [self.is_finger_up(landmarks, i) for i in range(5)]
            total_fingers = fingers_up.count(True)
            
            # Pinch detection (always thumb + index for consistency)
            is_pinching, pinch_dist = self.detect_pinch_gesture(landmarks)
            if is_pinching:
                # Switch to pinky for cursor control during pinch
                if self.cursor_finger != 'pinky':
                    self.set_cursor_finger('pinky')
                return "pinch"
            
            # Point gesture - depends on current cursor finger
            cursor_finger_idx = 1 if self.cursor_finger == 'index' else 4  # Index=1, Pinky=4
            
            if cursor_finger_idx < len(fingers_up) and fingers_up[cursor_finger_idx]:
                # Check if only cursor finger (and optionally thumb) is up
                other_fingers = [i for i in range(5) if i != cursor_finger_idx and i != 0]
                if not any(fingers_up[i] for i in other_fingers):
                    # Switch back to index for normal pointing if not already
                    if self.cursor_finger != 'index':
                        self.set_cursor_finger('index')
                    return "point"
            
            # Peace sign - index and middle
            if len(fingers_up) >= 5 and fingers_up[1] and fingers_up[2] and not fingers_up[3] and not fingers_up[4]:
                return "peace"
            
            # Fist - all down
            if total_fingers <= 1:
                return "fist"
            
            # Open hand - most fingers up
            if total_fingers >= 4:
                return "open_hand"
            
            return "other"
            
        except Exception as e:
            print(f"Gesture detection error: {e}")
            return "error"
    
    def detect_pinch_gesture(self, landmarks):
        """Pinch detection with stability and error handling"""
        try:
            if len(landmarks) < 21:
                return False, float('inf')
            
            finger_positions = self.get_finger_positions(landmarks)
            
            if 'thumb_tip' in finger_positions and 'index' in finger_positions:
                thumb_tip = finger_positions['thumb_tip']
                index_tip = finger_positions['index']
                
                pinch_distance = self.calculate_distance(thumb_tip, index_tip)
                
                # Add to history for stability
                self.pinch_history.append(pinch_distance < self.pinch_threshold)
                if len(self.pinch_history) > self.pinch_stability_count:
                    self.pinch_history.pop(0)
                
                # Require consistent detection
                stable_pinch = (len(self.pinch_history) >= self.pinch_stability_count and 
                              sum(self.pinch_history) >= self.pinch_stability_count - 1)
                
                return stable_pinch, pinch_distance
            
            return False, float('inf')
            
        except Exception as e:
            print(f"Pinch detection error: {e}")
            return False, float('inf')
    
    def get_cursor_finger_position(self, landmarks):
        """Get current cursor control finger position with error handling"""
        try:
            if len(landmarks) < 21:
                return {'x': 0, 'y': 0, 'valid': False, 'stability': 0}
            
            # Select finger based on current setting
            tip_id = 8 if self.cursor_finger == 'index' else 20  # Index or pinky
            pip_id = 6 if self.cursor_finger == 'index' else 18
            mcp_id = 5 if self.cursor_finger == 'index' else 17
            
            if tip_id >= len(landmarks) or pip_id >= len(landmarks) or mcp_id >= len(landmarks):
                return {'x': 0, 'y': 0, 'valid': False, 'stability': 0}
            
            tip = landmarks[tip_id]
            pip = landmarks[pip_id]
            mcp = landmarks[mcp_id]
            
            tip_x, tip_y = tip[1], tip[2]
            pip_x, pip_y = pip[1], pip[2]
            mcp_x, mcp_y = mcp[1], mcp[2]
            
            # Calculate stability
            finger_length = math.sqrt((tip_x - mcp_x)**2 + (tip_y - mcp_y)**2)
            length_stability = min(finger_length / 80, 1.0)
            
            # Check if finger is extended
            is_extended = tip_y < pip_y
            extension_stability = 1.0 if is_extended else 0.3
            
            stability = (length_stability + extension_stability) / 2
            is_valid = finger_length > 20 and stability > 0.4
            
            return {
                'x': tip_x,
                'y': tip_y,
                'valid': is_valid,
                'stability': stability,
                'finger_type': self.cursor_finger
            }
            
        except Exception as e:
            print(f"Cursor finger position error: {e}")
            return {'x': 0, 'y': 0, 'valid': False, 'stability': 0}
    
    def get_index_finger_position(self, landmarks):
        """Compatibility method - now uses cursor finger"""
        return self.get_cursor_finger_position(landmarks)
    
    def is_pinch_active(self, landmarks):
        """Check if pinch is active with error handling"""
        try:
            is_pinching, _ = self.detect_pinch_gesture(landmarks)
            return is_pinching
        except Exception as e:
            print(f"Pinch active check error: {e}")
            return False
    
    def reset_tracking_state(self):
        """Reset tracking state"""
        try:
            self.gesture_history.clear()
            self.pinch_history.clear()
            self.cursor_finger = 'index'  # Reset to default
        except Exception as e:
            print(f"State reset error: {e}")
