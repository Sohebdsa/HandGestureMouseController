import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
import threading
import time
from camera_manager import CameraManager


class GUIController:
    def __init__(self, hand_tracker, cursor_controller):
        self.hand_tracker = hand_tracker
        self.cursor_controller = cursor_controller
        self.camera_manager = CameraManager()
        
        self.root = tk.Tk()
        self.root.title("Hand Cursor Control - Professional Edition")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Configure grid weights for responsive design
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Color scheme
        self.colors = {
            'bg': '#f0f0f0',
            'primary': '#2196F3',
            'secondary': '#FFC107',
            'success': '#4CAF50',
            'danger': '#F44336',
            'dark': '#212121',
            'light': '#FFFFFF'
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        self.is_running = False
        self.video_thread = None
        self.current_gesture = "none"
        
        self.setup_styles()
        self.setup_gui()
        
    def setup_styles(self):
        """Configure ttk styles with fallback compatibility"""
        self.style = ttk.Style()
        
        # Get available themes and choose the best one
        themes = self.style.theme_names()
        preferred_themes = ['clam', 'alt', 'default', 'classic']
        
        selected_theme = 'default'
        for theme in preferred_themes:
            if theme in themes:
                selected_theme = theme
                break
        
        try:
            self.style.theme_use(selected_theme)
            print(f"Using theme: {selected_theme}")
        except Exception as e:
            print(f"Theme error: {e}, using default")
            self.style.theme_use('default')
        
        # Configure styles with error handling
        styles_to_configure = [
            ('Primary.TButton', {
                'font': ('Arial', 10, 'bold'),
                'padding': (20, 10)
            }),
            ('Success.TButton', {
                'font': ('Arial', 9, 'bold'),
                'padding': (15, 8)
            }),
            ('Danger.TButton', {
                'font': ('Arial', 9, 'bold'),
                'padding': (15, 8)
            }),
            ('Card.TLabelFrame', {
                'borderwidth': 2,
                'relief': 'raised'
            })
        ]
        
        for style_name, style_config in styles_to_configure:
            try:
                self.style.configure(style_name, **style_config)
            except Exception as e:
                print(f"Could not configure style {style_name}: {e}")
        
    def setup_gui(self):
        """Setup professional GUI layout"""
        # Main container with padding
        main_container = ttk.Frame(self.root, padding="20")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_container.columnconfigure(1, weight=1)
        main_container.rowconfigure(1, weight=1)
        
        # Header
        self.create_header(main_container)
        
        # Main content area with 3 columns
        content_frame = ttk.Frame(main_container)
        content_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=20)
        content_frame.columnconfigure(1, weight=2)  # Center column gets more space
        content_frame.rowconfigure(0, weight=1)
        
        # Left panel - Controls
        self.create_left_panel(content_frame)
        
        # Center panel - Video preview
        self.create_center_panel(content_frame)
        
        # Right panel - Status and settings
        self.create_right_panel(content_frame)
        
        # Footer
        self.create_footer(main_container)
    
    def create_header(self, parent):
        """Create professional header"""
        header_frame = self.create_safe_labelframe(parent, "Header")
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        header_frame.columnconfigure(1, weight=1)
        
        # Logo/Title
        title_label = ttk.Label(header_frame, text="🎯 Hand Cursor Control", 
                               font=('Arial', 16, 'bold'),
                               foreground=self.colors['primary'])
        title_label.grid(row=0, column=0, padx=20, pady=15)
        
        # Status indicator
        self.status_indicator = tk.Canvas(header_frame, width=20, height=20, 
                                         highlightthickness=0, bg=self.colors['light'])
        self.status_indicator.grid(row=0, column=2, padx=20, pady=15)
        self.update_status_indicator(False)
        
    def create_safe_labelframe(self, parent, text, padding="15"):
        """Create LabelFrame with safe styling"""
        try:
            return ttk.LabelFrame(parent, text=text, style='Card.TLabelFrame', padding=padding)
        except tk.TclError:
            return ttk.LabelFrame(parent, text=text, padding=padding)
        
    def create_left_panel(self, parent):
        """Create left control panel with cursor inversion toggle and game integration"""
        left_frame = self.create_safe_labelframe(parent, "Camera & Controls")
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Camera selection
        camera_section = ttk.LabelFrame(left_frame, text="Camera Selection", padding="10")
        camera_section.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.camera_type_var = tk.StringVar(value="local")
        
        ttk.Radiobutton(camera_section, text="📷 Local Webcam", 
                       variable=self.camera_type_var, value="local",
                       command=self.on_camera_type_change).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        ttk.Radiobutton(camera_section, text="📱 DroidCam (Phone)", 
                       variable=self.camera_type_var, value="droidcam",
                       command=self.on_camera_type_change).grid(row=1, column=0, sticky=tk.W, pady=5)
        
        # DroidCam settings
        self.droidcam_frame = ttk.Frame(camera_section)
        self.droidcam_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(self.droidcam_frame, text="Phone IP:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.ip_entry = ttk.Entry(self.droidcam_frame, width=15, font=('Arial', 9))
        self.ip_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=2)
        self.ip_entry.insert(0, "192.168.1.100")
        
        ttk.Label(self.droidcam_frame, text="Port:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.port_entry = ttk.Entry(self.droidcam_frame, width=15, font=('Arial', 9))
        self.port_entry.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=2)
        self.port_entry.insert(0, "4747")
        
        self.test_btn = ttk.Button(self.droidcam_frame, text="Test Connection", 
                                  command=self.test_droidcam_connection)
        self.test_btn.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=10)
        
        self.connection_status = ttk.Label(self.droidcam_frame, text="Not tested", 
                                          foreground="gray")
        self.connection_status.grid(row=5, column=0, pady=5)
        
        self.toggle_droidcam_settings()
        
        # Control buttons section
        control_section = ttk.LabelFrame(left_frame, text="Control", padding="10")
        control_section.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        try:
            self.start_btn = ttk.Button(control_section, text="▶ Start Tracking", 
                                       command=self.start_tracking, style='Success.TButton')
        except tk.TclError:
            self.start_btn = ttk.Button(control_section, text="▶ Start Tracking", 
                                       command=self.start_tracking)
        self.start_btn.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        try:
            self.stop_btn = ttk.Button(control_section, text="⏹ Stop Tracking", 
                                      command=self.stop_tracking, state="disabled", 
                                      style='Danger.TButton')
        except tk.TclError:
            self.stop_btn = ttk.Button(control_section, text="⏹ Stop Tracking", 
                                      command=self.stop_tracking, state="disabled")
        self.stop_btn.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Cursor Inversion Toggle
        self.inverse_var = tk.BooleanVar(value=False)
        self.inverse_btn = ttk.Checkbutton(control_section, 
                                          text="🔄 Invert Cursor Movement",
                                          variable=self.inverse_var,
                                          command=self.toggle_cursor_inversion)
        self.inverse_btn.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Adaptive Training Game Button
        try:
            self.training_btn = ttk.Button(control_section, text="🎮 Adaptive Training Game", 
                                          command=self.open_training_game, 
                                          style='Primary.TButton')
        except tk.TclError:
            self.training_btn = ttk.Button(control_section, text="🎮 Adaptive Training Game", 
                                          command=self.open_training_game)
        self.training_btn.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # Settings section with enhanced controls
        settings_section = ttk.LabelFrame(left_frame, text="Settings", padding="10")
        settings_section.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Sensitivity with better range
        ttk.Label(settings_section, text="Sensitivity:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.sensitivity_var = tk.DoubleVar(value=1.0)
        sensitivity_frame = ttk.Frame(settings_section)
        sensitivity_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.sensitivity_scale = ttk.Scale(sensitivity_frame, from_=0.3, to=2.0, 
                                          variable=self.sensitivity_var, orient=tk.HORIZONTAL)
        self.sensitivity_scale.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.sensitivity_label = ttk.Label(sensitivity_frame, text="1.0")
        self.sensitivity_label.grid(row=0, column=1, padx=(10, 0))
        
        self.sensitivity_scale.configure(command=self.update_sensitivity_label)
        
        # Smoothing with better range
        ttk.Label(settings_section, text="Smoothing:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.smoothing_var = tk.DoubleVar(value=0.6)
        smoothing_frame = ttk.Frame(settings_section)
        smoothing_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.smoothing_scale = ttk.Scale(smoothing_frame, from_=0.1, to=0.9, 
                                        variable=self.smoothing_var, orient=tk.HORIZONTAL)
        self.smoothing_scale.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.smoothing_label = ttk.Label(smoothing_frame, text="0.6")
        self.smoothing_label.grid(row=0, column=1, padx=(10, 0))
        
        self.smoothing_scale.configure(command=self.update_smoothing_label)

    def toggle_cursor_inversion(self):
        """Toggle cursor movement inversion"""
        invert = self.inverse_var.get()
        self.cursor_controller.set_cursor_inversion(invert)
        
        # Update button text to show current state
        state_text = "ON" if invert else "OFF"
        print(f"Cursor inversion toggled: {state_text}")

    def open_training_game(self):
        """Open the adaptive training game with error handling"""
        try:
            # Check if game window already exists and is still open
            if not hasattr(self, 'training_game') or not hasattr(self.training_game, 'game_window') or not self.training_game.game_window.winfo_exists():
                # Import and create new training game instance
                from adaptive_game import TrainingGame
                self.training_game = TrainingGame(self.root, self.cursor_controller)
                print("Adaptive Training Game opened")
            else:
                # Bring existing window to front
                self.training_game.game_window.lift()
                self.training_game.game_window.focus_force()
                print("Training Game window brought to front")
        except ImportError as e:
            messagebox.showerror("Module Error", 
                            f"Could not import adaptive_game module.\n"
                            f"Make sure adaptive_game.py is in the same directory.\n"
                            f"Error: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", 
                            f"Failed to open Training Game.\n"
                            f"Error: {str(e)}")

    def close_training_game(self):
        """Close the training game if it exists"""
        if hasattr(self, 'training_game') and hasattr(self.training_game, 'game_window'):
            try:
                self.training_game.close()
                print("Training Game closed")
            except:
                pass
        
    def create_center_panel(self, parent):
        """Create centered video preview panel"""
        center_frame = self.create_safe_labelframe(parent, "Live Camera Feed")
        center_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10)
        center_frame.columnconfigure(0, weight=1)
        center_frame.rowconfigure(0, weight=1)
        
        # Video container with centered alignment
        video_container = ttk.Frame(center_frame)
        video_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        video_container.columnconfigure(0, weight=1)
        video_container.rowconfigure(0, weight=1)
        
        # Video display with border and centered positioning
        self.video_frame = tk.Frame(video_container, bg=self.colors['dark'], 
                                   relief='sunken', bd=3)
        self.video_frame.grid(row=0, column=0, padx=20, pady=20)
        
        self.video_label = tk.Label(self.video_frame, 
                                   text="📹\n\nCamera Preview\nWill Appear Here\n\nSelect camera and click Start",
                                   font=('Arial', 12),
                                   fg='white',
                                   bg=self.colors['dark'],
                                   width=60,
                                   height=20)
        self.video_label.pack(padx=10, pady=10)
        
        # Gesture overlay
        self.gesture_overlay = tk.Label(center_frame, text="", 
                                       font=('Arial', 14, 'bold'),
                                       fg=self.colors['secondary'],
                                       bg=self.colors['light'])
        self.gesture_overlay.grid(row=1, column=0, pady=10)
        
    def create_right_panel(self, parent):
        """Create right status and info panel"""
        right_frame = self.create_safe_labelframe(parent, "Status & Information")
        right_frame.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0))
        
        # Status section
        status_section = ttk.LabelFrame(right_frame, text="Current Status", padding="10")
        status_section.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        self.status_labels = {}
        
        labels = [
            ("System:", "Ready"),
            ("Camera:", "Not Connected"),
            ("Gesture:", "None"),
            ("Tracking:", "Inactive")
        ]
        
        for i, (label, default) in enumerate(labels):
            ttk.Label(status_section, text=label, font=('Arial', 9, 'bold')).grid(
                row=i, column=0, sticky=tk.W, pady=2)
            self.status_labels[label.rstrip(':')] = ttk.Label(
                status_section, text=default, font=('Arial', 9))
            self.status_labels[label.rstrip(':')].grid(
                row=i, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Gesture guide
        guide_section = ttk.LabelFrame(right_frame, text="Gesture Guide", padding="10")
        guide_section.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        gestures = [
            ("👆", "Point", "Move Cursor"),
            ("🤏", "Pinch", "Click/Hold"),
            ("✊", "Fist", "Left Click"),
            ("✌️", "Peace", "Right Click"),
            ("🖐️", "Open Hand", "Scroll Up"),
        ]
        
        for i, (emoji, gesture, action) in enumerate(gestures):
            gesture_frame = ttk.Frame(guide_section)
            gesture_frame.grid(row=i, column=0, sticky=(tk.W, tk.E), pady=5)
            
            ttk.Label(gesture_frame, text=emoji, font=('Arial', 16)).grid(row=0, column=0, padx=(0, 10))
            ttk.Label(gesture_frame, text=f"{gesture}: {action}", 
                     font=('Arial', 9)).grid(row=0, column=1, sticky=tk.W)
    
    def create_footer(self, parent):
        """Create footer with additional info"""
        footer_frame = ttk.Frame(parent)
        footer_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(20, 0))
        footer_frame.columnconfigure(1, weight=1)
        
        info_btn = ttk.Button(footer_frame, text="ℹ️ Help", command=self.show_help)
        info_btn.grid(row=0, column=0)
        
        self.fps_label = ttk.Label(footer_frame, text="FPS: --", font=('Arial', 8))
        self.fps_label.grid(row=0, column=2, padx=(10, 0))
        
    def update_sensitivity_label(self, value):
        """Update sensitivity label"""
        self.sensitivity_label.config(text=f"{float(value):.1f}")
        
    def update_smoothing_label(self, value):
        """Update smoothing label"""
        self.smoothing_label.config(text=f"{float(value):.1f}")
        
    def update_status_indicator(self, active):
        """Update header status indicator"""
        self.status_indicator.delete("all")
        color = self.colors['success'] if active else self.colors['danger']
        self.status_indicator.create_oval(2, 2, 18, 18, fill=color, outline=color)
        
    def on_camera_type_change(self):
        """Handle camera type selection change"""
        self.toggle_droidcam_settings()
        if self.is_running:
            self.stop_tracking()
    
    def toggle_droidcam_settings(self):
        """Show/hide DroidCam settings"""
        if self.camera_type_var.get() == "droidcam":
            for widget in self.droidcam_frame.winfo_children():
                widget.grid()
        else:
            for widget in self.droidcam_frame.winfo_children():
                widget.grid_remove()
    
    def test_droidcam_connection(self):
        """Test DroidCam connection"""
        ip = self.ip_entry.get().strip()
        port = self.port_entry.get().strip()
        
        if not ip:
            messagebox.showerror("Error", "Please enter phone IP address")
            return
        
        self.connection_status.config(text="Testing...", foreground="orange")
        self.root.update()
        
        def test_connection():
            success = self.camera_manager.test_droidcam_connection(ip, port)
            self.root.after(0, lambda: self.update_connection_status(success))
        
        threading.Thread(target=test_connection, daemon=True).start()
    
    def update_connection_status(self, success):
        """Update connection status display"""
        if success:
            self.connection_status.config(text="✓ Connected", foreground="green")
        else:
            self.connection_status.config(text="✗ Failed", foreground="red")
    
    def start_tracking(self):
        """Start hand tracking with improved error handling"""
        try:
            # Connect to camera
            if self.camera_type_var.get() == "local":
                success = self.camera_manager.connect_local_camera()
                if not success:
                    messagebox.showerror("Error", "Could not connect to local camera")
                    return
            else:
                ip = self.ip_entry.get().strip()
                port = self.port_entry.get().strip()
                
                if not ip:
                    messagebox.showerror("Error", "Please enter phone IP address")
                    return
                
                success = self.camera_manager.connect_droidcam(ip, port)
                if not success:
                    messagebox.showerror("Error", 
                        "Could not connect to DroidCam.\n\n"
                        "Please check:\n"
                        "• DroidCam app is running\n"
                        "• Same WiFi network\n"
                        "• Correct IP address\n"
                        "• Test connection first\n"
                        "• Check firewall settings")
                    return
            
            # Update UI
            self.is_running = True
            self.start_btn.config(state="disabled")
            self.stop_btn.config(state="normal")
            self.update_status_indicator(True)
            
            # Update status labels
            self.status_labels["System"].config(text="Active", foreground=self.colors['success'])
            self.status_labels["Tracking"].config(text="Running", foreground=self.colors['success'])
            
            camera_info = self.camera_manager.get_camera_info()
            self.status_labels["Camera"].config(text=f"{camera_info['type'].title()}", 
                                              foreground=self.colors['success'])
            
            # Start processing
            self.video_thread = threading.Thread(target=self.process_video, daemon=True)
            self.video_thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start tracking: {str(e)}")
    
    def stop_tracking(self):
        """Stop hand tracking"""
        self.is_running = False
        self.camera_manager.disconnect()
        
        # Update UI
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.update_status_indicator(False)
        
        # Reset cursor controller state
        self.cursor_controller.reset_state()
        
        # Reset status labels
        self.status_labels["System"].config(text="Ready", foreground="black")
        self.status_labels["Camera"].config(text="Not Connected", foreground="gray")
        self.status_labels["Gesture"].config(text="None", foreground="gray")
        self.status_labels["Tracking"].config(text="Inactive", foreground="gray")
        
        # Clear video
        self.video_label.config(image="", 
                               text="📹\n\nCamera Preview\nWill Appear Here\n\nSelect camera and click Start")
        self.gesture_overlay.config(text="")
        self.fps_label.config(text="FPS: --")
    
    def process_video(self):
        """Enhanced video processing with improved finger switching"""
        fps_counter = 0
        fps_start_time = time.time()
        last_frame_time = time.time()
        
        while self.is_running:
            ret, frame = self.camera_manager.get_frame()
            if not ret or frame is None:
                time.sleep(0.005)
                continue
            
            # Frame rate control
            current_time = time.time()
            frame_delta = current_time - last_frame_time
            target_fps = 60
            target_frame_time = 1.0 / target_fps
            
            if frame_delta < target_frame_time:
                time.sleep(target_frame_time - frame_delta)
            
            last_frame_time = time.time()
            
            # Update settings
            self.cursor_controller.smoothing_factor = self.smoothing_var.get()
            
            # Process frame
            frame = cv2.flip(frame, 1)
            height, width, _ = frame.shape
            
            try:
                results = self.hand_tracker.find_hands(frame)
                landmarks = self.hand_tracker.get_landmarks(frame, results)
                
                if landmarks and len(landmarks) >= 21:
                    gesture = self.hand_tracker.detect_gestures(landmarks)
                    cursor_pos = self.hand_tracker.get_cursor_finger_position(landmarks)
                    
                    if cursor_pos['valid'] and cursor_pos['stability'] > 0.4:
                        sensitivity = self.sensitivity_var.get()
                        x, y = self.cursor_controller.map_coordinates(
                            cursor_pos['x'], cursor_pos['y'], width, height
                        )
                        self.cursor_controller.move_cursor(x, y)
                    
                    # Handle gestures
                    if gesture == "pinch":
                        is_pinch = self.hand_tracker.is_pinch_active(landmarks)
                        self.cursor_controller.handle_pinch_gesture(is_pinch)
                        self.gesture_overlay.config(text="🤏 Pinch (Click/Hold)")
                        self.status_labels["Gesture"].config(text="Pinch", foreground=self.colors['primary'])
                    
                    elif gesture == "point":
                        self.cursor_controller.handle_pinch_gesture(False)
                        self.gesture_overlay.config(text="👆 Point (Move Cursor)")
                        self.status_labels["Gesture"].config(text="Point", foreground=self.colors['primary'])
                    
                    elif gesture == "fist":
                        self.cursor_controller.handle_pinch_gesture(False)
                        self.cursor_controller.click()
                        self.gesture_overlay.config(text="✊ Fist (Click)")
                        self.status_labels["Gesture"].config(text="Fist", foreground=self.colors['primary'])
                    
                    elif gesture == "peace":
                        self.cursor_controller.handle_pinch_gesture(False)
                        self.cursor_controller.right_click()
                        self.gesture_overlay.config(text="✌️ Peace (Right Click)")
                        self.status_labels["Gesture"].config(text="Peace", foreground=self.colors['primary'])
                    
                    elif gesture == "open_hand":
                        self.cursor_controller.handle_pinch_gesture(False)
                        self.cursor_controller.scroll("up")
                        self.gesture_overlay.config(text="🖐️ Open Hand (Scroll)")
                        self.status_labels["Gesture"].config(text="Open Hand", foreground=self.colors['primary'])
                    
                    else:
                        self.cursor_controller.handle_pinch_gesture(False)
                        self.gesture_overlay.config(text=f"🎯 {gesture.replace('_', ' ').title()}")
                        self.status_labels["Gesture"].config(text=gesture.title(), foreground=self.colors['secondary'])
                
                else:
                    self.cursor_controller.handle_pinch_gesture(False)
                    self.gesture_overlay.config(text="🤚 Show your hand")
                    self.status_labels["Gesture"].config(text="No Hand", foreground="orange")
                    
            except Exception as e:
                print(f"Hand tracking error: {e}")
                self.gesture_overlay.config(text="❌ Tracking Error")
                self.cursor_controller.handle_pinch_gesture(False)
            
            # Update video display
            self.update_video_display(frame)
            
            # Calculate FPS
            fps_counter += 1
            if fps_counter % 30 == 0:
                current_time = time.time()
                fps = 30 / (current_time - fps_start_time)
                self.fps_label.config(text=f"FPS: {fps:.1f}")
                fps_start_time = current_time
            
            time.sleep(0.001)

    def update_video_display(self, frame):
        """Update video display with proper centering"""
        try:
            # Resize for display (maintain aspect ratio)
            display_width, display_height = 640, 480
            h, w = frame.shape[:2]
            aspect_ratio = w / h
            
            if aspect_ratio > display_width / display_height:
                new_width = display_width
                new_height = int(display_width / aspect_ratio)
            else:
                new_height = display_height
                new_width = int(display_height * aspect_ratio)
            
            display_frame = cv2.resize(frame, (new_width, new_height))
            
            # Convert to RGB
            rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_frame)
            photo = ImageTk.PhotoImage(pil_image)
            
            # Update display
            self.video_label.config(image=photo, text="", width=new_width, height=new_height)
            self.video_label.image = photo
            
        except Exception as e:
            print(f"Display error: {e}")
    
    def show_help(self):
        """Show help dialog with training game information"""
        help_text = """
Hand Cursor Control - Help

🎯 SETUP:
1. Choose Local Webcam or DroidCam
2. For DroidCam: Enter phone IP and test connection
3. Click 'Start Tracking'

🤚 GESTURES:
• Point (Index finger): Move cursor
• Pinch (Thumb + Index): Click (quick) / Hold+Drag (sustained)
• Fist: Alternative left click  
• Peace sign: Right click
• Open hand: Scroll up

⚙️ SETTINGS:
• Sensitivity: Control cursor speed
• Smoothing: Reduce jitter
• Invert Cursor: Toggle cursor direction

🎮 ADAPTIVE TRAINING GAME:
• Click 'Adaptive Training Game' to open
• Drag colored circles to matching drop zones
• Game adapts difficulty based on performance
• Provide feedback after each level
• BFS algorithm optimizes settings automatically

💡 TIPS:
• Ensure good lighting
• Keep hand clearly visible
• Adjust settings for comfort
• Use same WiFi for DroidCam
• Play training game to optimize settings

🔥 FIREWALL TROUBLESHOOTING:
If DroidCam connection fails:
• Temporarily disable Windows Firewall
• Add exception for Python.exe
• Check router firewall settings
• Ensure port 4747 is open

🤏 PINCH GESTURE USAGE:
• Quick pinch: Single click
• Hold pinch for 0.5+ seconds: Click and hold (drag mode)
• Release pinch: Release hold

For DroidCam setup, ensure both devices are on the same network.
        """
        messagebox.showinfo("Help - Hand Cursor Control", help_text)

    def run(self):
        """Run the application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Handle window closing with training game cleanup"""
        if self.is_running:
            self.stop_tracking()
        
        # Close training game if open
        self.close_training_game()
        
        self.root.destroy()
