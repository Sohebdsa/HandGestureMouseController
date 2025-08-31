import pyautogui
import numpy as np
import time
import threading
from collections import deque

class CursorController:
    def __init__(self):
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0
        self.screen_width, self.screen_height = pyautogui.size()
        
        # Movement settings with anti-jitter
        self.smoothing_factor = 0.2
        self.acceleration_factor = 1.2
        self.velocity_smoothing = 0.15
        
        # Enhanced movement tracking
        self.prev_x, self.prev_y = 0, 0
        self.velocity_x, self.velocity_y = 0, 0
        self.movement_threshold = 3
        self.max_velocity = 80
        self.prediction_factor = 0.2
        self.jitter_filter_size = 3
        self.position_history = deque(maxlen=self.jitter_filter_size)
        
        # Cursor control toggle system
        self.cursor_enabled = True  # Cursor movement enabled by default
        self.last_fist_time = 0
        self.fist_double_click_window = 1.0  # 1 second window for double fist
        self.fist_count = 0
        
        # Adaptive settings
        self.inverse_cursor = False
        self.adaptive_sensitivity = 1.0
        self.adaptive_smoothing = 0.2
        self.adaptive_acceleration = 1.2
        
        # Click and hold state
        self.is_holding = False
        self.last_click_time = 0
        self.click_cooldown = 0.15
        self.hold_start_time = 0
        self.hold_threshold = 0.3
        
        # Scroll settings
        self.last_scroll_time = 0
        self.scroll_cooldown = 0.1
        
        # Performance tracking
        self.movement_history = deque(maxlen=50)
        
    def toggle_cursor_movement(self):
        """Toggle cursor movement on/off"""
        self.cursor_enabled = not self.cursor_enabled
        status = "ENABLED" if self.cursor_enabled else "DISABLED"
        print(f"Cursor movement {status}")
        return self.cursor_enabled
    
    def handle_fist_toggle(self):
        """Handle double fist gesture for cursor toggle"""
        current_time = time.time()
        
        # Check if this fist is within the double-click window
        if current_time - self.last_fist_time < self.fist_double_click_window:
            self.fist_count += 1
            if self.fist_count >= 2:
                # Double fist detected - toggle cursor
                self.toggle_cursor_movement()
                self.fist_count = 0
                return True  # Indicate toggle occurred
        else:
            # Reset count if too much time passed
            self.fist_count = 1
        
        self.last_fist_time = current_time
        return False  # No toggle occurred
    
    def set_adaptive_settings(self, sensitivity, smoothing, acceleration):
        """Set adaptive settings based on optimization"""
        self.adaptive_sensitivity = max(0.3, min(2.0, sensitivity))
        self.adaptive_smoothing = max(0.1, min(0.8, smoothing))
        self.adaptive_acceleration = max(1.0, min(3.0, acceleration))
        self.smoothing_factor = self.adaptive_smoothing
        print(f"Settings updated: S={sensitivity:.2f}, Sm={smoothing:.2f}, A={acceleration:.2f}")
    
    def set_cursor_inversion(self, invert):
        """Set cursor movement inversion"""
        self.inverse_cursor = invert
        
    def apply_jitter_filter(self, x, y):
        """Apply anti-jitter filtering"""
        self.position_history.append((x, y))
        
        if len(self.position_history) < 2:
            return x, y
        
        weights = np.linspace(0.3, 1.0, len(self.position_history))
        weights = weights / np.sum(weights)
        
        filtered_x = sum(pos[0] * weight for pos, weight in zip(self.position_history, weights))
        filtered_y = sum(pos[1] * weight for pos, weight in zip(self.position_history, weights))
        
        return filtered_x, filtered_y
    
    def map_coordinates(self, hand_x, hand_y, frame_width, frame_height):
        """Enhanced coordinate mapping with toggle support"""
        if not self.cursor_enabled:
            return int(self.prev_x), int(self.prev_y)  # Return last position if disabled
        
        start_time = time.time()
        
        # Enhanced margins for stability
        margin_x, margin_y = 40, 40
        effective_width = frame_width - (2 * margin_x)
        effective_height = frame_height - (2 * margin_y)
        
        # Normalize with margins
        norm_x = np.clip((hand_x - margin_x) / effective_width, 0, 1)
        norm_y = np.clip((hand_y - margin_y) / effective_height, 0, 1)
        
        # Apply inversion
        if self.inverse_cursor:
            norm_x = 1 - norm_x
            norm_y = 1 - norm_y
        
        # Map to screen coordinates
        target_x = norm_x * self.screen_width * self.adaptive_sensitivity
        target_y = norm_y * self.screen_height * self.adaptive_sensitivity
        
        # Apply jitter filter
        filtered_x, filtered_y = self.apply_jitter_filter(target_x, target_y)
        
        # Initialize if first run
        if self.prev_x == 0 and self.prev_y == 0:
            self.prev_x, self.prev_y = filtered_x, filtered_y
            return int(filtered_x), int(filtered_y)
        
        # Calculate smooth velocity
        velocity_x = filtered_x - self.prev_x
        velocity_y = filtered_y - self.prev_y
        
        # Apply velocity smoothing
        smooth_velocity_x = (self.velocity_x * self.velocity_smoothing + 
                           velocity_x * (1 - self.velocity_smoothing))
        smooth_velocity_y = (self.velocity_y * self.velocity_smoothing + 
                           velocity_y * (1 - self.velocity_smoothing))
        
        # Apply acceleration for significant movements
        velocity_magnitude = np.sqrt(smooth_velocity_x**2 + smooth_velocity_y**2)
        if velocity_magnitude > 15:
            smooth_velocity_x *= self.adaptive_acceleration
            smooth_velocity_y *= self.adaptive_acceleration
        
        # Calculate final position
        final_x = self.prev_x + smooth_velocity_x
        final_y = self.prev_y + smooth_velocity_y
        
        # Clamp to screen bounds
        final_x = max(0, min(self.screen_width - 1, final_x))
        final_y = max(0, min(self.screen_height - 1, final_y))
        
        # Update tracking variables
        self.velocity_x = smooth_velocity_x
        self.velocity_y = smooth_velocity_y
        self.prev_x, self.prev_y = final_x, final_y
        
        return int(final_x), int(final_y)
    
    def move_cursor(self, x, y):
        """Move cursor only if enabled"""
        if not self.cursor_enabled:
            return
            
        try:
            current_x, current_y = pyautogui.position()
            distance = np.sqrt((x - current_x)**2 + (y - current_y)**2)
            if distance > self.movement_threshold:
                pyautogui.moveTo(x, y, duration=0, _pause=False)
        except Exception as e:
            print(f"Cursor movement error: {e}")
    
    def handle_pinch_gesture(self, is_pinch_active):
        """Enhanced pinch handling"""
        current_time = time.time()
        
        if is_pinch_active:
            if not self.is_holding:
                if self.hold_start_time == 0:
                    self.hold_start_time = current_time
                elif current_time - self.hold_start_time > self.hold_threshold:
                    try:
                        pyautogui.mouseDown(_pause=False)
                        self.is_holding = True
                        print("Started holding (drag mode)")
                    except Exception as e:
                        print(f"Hold start error: {e}")
        else:
            if self.is_holding:
                try:
                    pyautogui.mouseUp(_pause=False)
                    self.is_holding = False
                    print("Released hold")
                except Exception as e:
                    print(f"Hold release error: {e}")
            elif self.hold_start_time > 0:
                hold_duration = current_time - self.hold_start_time
                if hold_duration < self.hold_threshold and current_time - self.last_click_time > self.click_cooldown:
                    try:
                        pyautogui.click(_pause=False)
                        self.last_click_time = current_time
                        print("Quick click")
                    except Exception as e:
                        print(f"Click error: {e}")
            self.hold_start_time = 0
    
    def click(self):
        """Perform regular left click"""
        current_time = time.time()
        if current_time - self.last_click_time > self.click_cooldown:
            try:
                pyautogui.click(_pause=False)
                self.last_click_time = current_time
            except Exception as e:
                print(f"Click error: {e}")
    
    def right_click(self):
        """Perform right click"""
        current_time = time.time()
        if current_time - self.last_click_time > self.click_cooldown:
            try:
                pyautogui.rightClick(_pause=False)
                self.last_click_time = current_time
            except Exception as e:
                print(f"Right click error: {e}")
    
    def scroll(self, direction):
        """Enhanced scrolling"""
        current_time = time.time()
        if current_time - self.last_scroll_time > self.scroll_cooldown:
            try:
                if direction == "up":
                    pyautogui.scroll(3, _pause=False)
                elif direction == "down":
                    pyautogui.scroll(-3, _pause=False)
                self.last_scroll_time = current_time
            except Exception as e:
                print(f"Scroll error: {e}")
    
    def double_click(self):
        """Perform double click"""
        current_time = time.time()
        if current_time - self.last_click_time > self.click_cooldown:
            try:
                pyautogui.doubleClick(_pause=False)
                self.last_click_time = current_time
            except Exception as e:
                print(f"Double click error: {e}")
    
    def key_press(self, key):
        """Press a keyboard key"""
        try:
            pyautogui.press(key)
        except Exception as e:
            print(f"Key press error: {e}")
    
    def key_combination(self, *keys):
        """Press key combination (e.g., ctrl+c)"""
        try:
            pyautogui.hotkey(*keys)
        except Exception as e:
            print(f"Key combination error: {e}")
    
    def reset_state(self):
        """Reset controller state"""
        if self.is_holding:
            try:
                pyautogui.mouseUp(_pause=False)
            except:
                pass
        self.is_holding = False
        self.hold_start_time = 0
        self.position_history.clear()
        self.movement_history.clear()
        self.velocity_x = self.velocity_y = 0
        self.prev_x = self.prev_y = 0
        self.fist_count = 0
