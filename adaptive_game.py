import tkinter as tk
from tkinter import ttk
import random
import time
import math
import threading
from collections import deque
import numpy as np

class AdaptiveSettingsOptimizer:
    """BFS-based optimizer for cursor control settings"""
    
    def __init__(self):
        # BFS optimization parameters
        self.sensitivity_range = np.arange(0.3, 2.1, 0.1)
        self.smoothing_range = np.arange(0.1, 0.8, 0.05)
        self.acceleration_range = np.arange(1.0, 3.0, 0.1)
        
        # Current best settings
        self.best_settings = {'sensitivity': 1.0, 'smoothing': 0.3, 'acceleration': 1.5}
        self.best_score = 0.0
        
        # BFS queue and visited states
        self.search_queue = deque()
        self.visited_settings = set()
        self.optimization_history = []
        
    def bfs_optimize(self, current_score, user_feedback):
        """Use BFS to find optimal settings based on performance and feedback"""
        current_settings = self.best_settings.copy()
        
        # Add neighboring states to search queue
        neighbors = self.generate_neighbors(current_settings)
        
        for neighbor in neighbors:
            setting_key = self.settings_to_key(neighbor)
            if setting_key not in self.visited_settings:
                self.search_queue.append((neighbor, current_score))
                self.visited_settings.add(setting_key)
        
        # Process queue with user feedback weight
        feedback_weight = self.interpret_feedback(user_feedback)
        adjusted_score = current_score * feedback_weight
        
        if adjusted_score > self.best_score:
            self.best_score = adjusted_score
            self.best_settings = current_settings.copy()
            print(f"New best settings found: {self.best_settings} (Score: {adjusted_score:.2f})")
        
        return self.get_next_settings()
    
    def generate_neighbors(self, settings):
        """Generate neighboring settings for BFS exploration"""
        neighbors = []
        step_size = {'sensitivity': 0.1, 'smoothing': 0.05, 'acceleration': 0.1}
        
        for param in ['sensitivity', 'smoothing', 'acceleration']:
            # Increase parameter
            neighbor = settings.copy()
            neighbor[param] = min(neighbor[param] + step_size[param], 
                                self.get_max_value(param))
            neighbors.append(neighbor)
            
            # Decrease parameter
            neighbor = settings.copy()
            neighbor[param] = max(neighbor[param] - step_size[param], 
                                self.get_min_value(param))
            neighbors.append(neighbor)
        
        return neighbors
    
    def get_min_value(self, param):
        """Get minimum value for parameter"""
        param_mins = {'sensitivity': 0.3, 'smoothing': 0.1, 'acceleration': 1.0}
        return param_mins.get(param, 0.1)
    
    def get_max_value(self, param):
        """Get maximum value for parameter"""
        param_maxs = {'sensitivity': 2.0, 'smoothing': 0.8, 'acceleration': 3.0}
        return param_maxs.get(param, 2.0)
    
    def settings_to_key(self, settings):
        """Convert settings to hashable key"""
        return (round(settings['sensitivity'], 2), 
                round(settings['smoothing'], 2), 
                round(settings['acceleration'], 2))
    
    def interpret_feedback(self, feedback):
        """Convert user feedback to numerical weight"""
        feedback_map = {
            'much_faster': 1.5,
            'faster': 1.2,
            'perfect': 2.0,
            'slower': 0.8,
            'much_slower': 0.6,
            'sharper': 1.3,
            'smoother': 1.1
        }
        return feedback_map.get(feedback, 1.0)
    
    def get_next_settings(self):
        """Get next settings to try from BFS queue"""
        if self.search_queue:
            next_settings, _ = self.search_queue.popleft()
            return next_settings
        return self.best_settings

class TrainingGame:
    """Adaptive cursor training game with BFS optimization"""
    
    def __init__(self, parent_window, cursor_controller):
        self.parent_window = parent_window
        self.cursor_controller = cursor_controller
        self.optimizer = AdaptiveSettingsOptimizer()
        
        # Game state
        self.is_running = False
        self.current_level = 1
        self.score = 0
        self.total_attempts = 0
        self.successful_attempts = 0
        
        # Game objects
        self.targets = []
        self.grabbed_target = None
        self.drop_zones = []
        
        # Performance tracking
        self.start_time = 0
        self.completion_times = []
        self.accuracy_scores = []
        
        # UI components
        self.game_window = None
        self.canvas = None
        
        self.setup_game_ui()
        
    def setup_game_ui(self):
        """Setup the training game interface"""
        # Create game window
        self.game_window = tk.Toplevel(self.parent_window)
        self.game_window.title("🎮 Adaptive Cursor Training Game")
        self.game_window.geometry("850x650")
        self.game_window.configure(bg='#2c3e50')
        self.game_window.resizable(False, False)
        
        # Make window modal
        self.game_window.transient(self.parent_window)
        self.game_window.grab_set()
        
        # Header
        header_frame = tk.Frame(self.game_window, bg='#34495e', height=60)
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="🎯 Adaptive Cursor Training", 
                              font=('Arial', 16, 'bold'), fg='white', bg='#34495e')
        title_label.pack(pady=15)
        
        # Game canvas with proper parent reference
        canvas_frame = tk.Frame(self.game_window, bg='#2c3e50')
        canvas_frame.pack(pady=10)
        
        self.canvas = tk.Canvas(canvas_frame, width=800, height=400, 
                               bg='#34495e', highlightthickness=2, 
                               highlightbackground='#3498db')
        self.canvas.pack()
        
        # Control panel
        control_frame = tk.Frame(self.game_window, bg='#2c3e50')
        control_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Game info (left side)
        info_frame = tk.Frame(control_frame, bg='#2c3e50')
        info_frame.pack(side=tk.LEFT)
        
        self.level_label = tk.Label(info_frame, text="Level: 1", 
                                   font=('Arial', 12, 'bold'), fg='white', bg='#2c3e50')
        self.level_label.pack(anchor='w')
        
        self.score_label = tk.Label(info_frame, text="Score: 0", 
                                   font=('Arial', 12), fg='white', bg='#2c3e50')
        self.score_label.pack(anchor='w')
        
        self.accuracy_label = tk.Label(info_frame, text="Accuracy: 0%", 
                                      font=('Arial', 12), fg='white', bg='#2c3e50')
        self.accuracy_label.pack(anchor='w')
        
        # Control buttons (right side)
        button_frame = tk.Frame(control_frame, bg='#2c3e50')
        button_frame.pack(side=tk.RIGHT)
        
        self.start_btn = tk.Button(button_frame, text="🚀 Start Training", 
                                  command=self.start_game, font=('Arial', 10, 'bold'),
                                  bg='#27ae60', fg='white', padx=20, pady=5)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.reset_btn = tk.Button(button_frame, text="🔄 Reset", 
                                  command=self.reset_game, font=('Arial', 10),
                                  bg='#e74c3c', fg='white', padx=20, pady=5)
        self.reset_btn.pack(side=tk.LEFT, padx=5)
        
        self.close_btn = tk.Button(button_frame, text="❌ Close", 
                                  command=self.close, font=('Arial', 10),
                                  bg='#95a5a6', fg='white', padx=20, pady=5)
        self.close_btn.pack(side=tk.LEFT, padx=5)
        
        # Feedback panel
        feedback_frame = tk.LabelFrame(self.game_window, text="How did the cursor movement feel?", 
                                      font=('Arial', 11, 'bold'), fg='white', bg='#2c3e50',
                                      padx=10, pady=10)
        feedback_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.feedback_var = tk.StringVar()
        feedback_options = [
            ("🐌 Too slow, need much faster", "much_faster"),
            ("⏳ A bit slow", "faster"),
            ("✨ Perfect!", "perfect"),
            ("⚡ A bit fast", "slower"),
            ("🚀 Too fast, need slower", "much_slower"),
            ("🎯 Need sharper movement", "sharper"),
            ("🌊 Need smoother movement", "smoother")
        ]
        
        # Create feedback grid
        feedback_grid = tk.Frame(feedback_frame, bg='#2c3e50')
        feedback_grid.pack()
        
        for i, (text, value) in enumerate(feedback_options):
            rb = tk.Radiobutton(feedback_grid, text=text, variable=self.feedback_var,
                               value=value, command=self.apply_feedback,
                               font=('Arial', 10), fg='white', bg='#2c3e50',
                               selectcolor='#3498db', activebackground='#34495e')
            rb.grid(row=i//2, column=i%2, sticky='w', padx=15, pady=3)
        
        # Performance display
        perf_frame = tk.LabelFrame(self.game_window, text="Current Optimized Settings", 
                                  font=('Arial', 11, 'bold'), fg='white', bg='#2c3e50',
                                  padx=10, pady=10)
        perf_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        self.settings_label = tk.Label(perf_frame, 
                                      text="Sensitivity: 1.0 | Smoothing: 0.3 | Acceleration: 1.5",
                                      font=('Arial', 12), fg='#f39c12', bg='#2c3e50')
        self.settings_label.pack()
        
        # Instructions
        instructions = ("🎮 Instructions: Drag colored circles to matching drop zones\n"
                       "🎯 Complete levels to optimize your cursor settings automatically\n"
                       "📊 Provide feedback after each level for better optimization")
        
        instr_label = tk.Label(self.game_window, text=instructions,
                              font=('Arial', 9), fg='#bdc3c7', bg='#2c3e50',
                              justify=tk.CENTER)
        instr_label.pack(pady=(0, 10))
        
        # Bind mouse events to canvas
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        
        # Handle window closing
        self.game_window.protocol("WM_DELETE_WINDOW", self.close)
        
        # Show initial instructions
        self.show_initial_instructions()
        
    def show_initial_instructions(self):
        """Show initial game instructions"""
        self.canvas.create_text(400, 200, 
                               text="🎮 Welcome to Adaptive Cursor Training!\n\n"
                                    "Click 'Start Training' to begin your first level.\n\n"
                                    "The game will adapt to your performance and\n"
                                    "optimize cursor settings using AI algorithms.",
                               fill='white', font=('Arial', 14), justify=tk.CENTER)
        
    def start_game(self):
        """Start the training game"""
        self.is_running = True
        self.start_btn.config(state='disabled', text='🎯 Training...')
        self.start_time = time.time()
        
        self.generate_level()
        self.game_loop()
        
    def generate_level(self):
        """Generate targets and drop zones for current level"""
        self.canvas.delete("all")
        self.targets = []
        self.drop_zones = []
        
        # Progressive difficulty
        num_targets = min(2 + self.current_level, 6)
        target_size = max(35 - self.current_level * 3, 20)
        
        colors = ['#e74c3c', '#f39c12', '#2ecc71', '#9b59b6', '#1abc9c', '#e67e22']
        
        # Generate targets
        for i in range(num_targets):
            # Target position (top half)
            x = random.randint(target_size + 10, 800 - target_size - 10)
            y = random.randint(target_size + 10, 180)
            
            color = colors[i % len(colors)]
            target = self.canvas.create_oval(x - target_size//2, y - target_size//2,
                                           x + target_size//2, y + target_size//2,
                                           fill=color, outline='white', width=3,
                                           tags="target")
            self.targets.append({'id': target, 'color': color, 'size': target_size})
            
            # Create corresponding drop zone (bottom half)
            drop_x = random.randint(target_size + 10, 800 - target_size - 10)
            drop_y = random.randint(250, 380 - target_size)
            
            drop_zone = self.canvas.create_rectangle(drop_x - target_size//2, drop_y - target_size//2,
                                                   drop_x + target_size//2, drop_y + target_size//2,
                                                   fill='gray', outline=color, width=4,
                                                   stipple='gray50', tags="dropzone")
            self.drop_zones.append({'id': drop_zone, 'color': color, 'target_id': target})
        
        # Add level instructions
        self.canvas.create_text(400, 30, 
                               text=f"🎯 Level {self.current_level}: Drag {num_targets} colored circles to matching drop zones",
                               fill='white', font=('Arial', 14, 'bold'))
        
        # Separator line
        self.canvas.create_line(50, 220, 750, 220, fill='white', width=2, dash=(10, 5))
        
    def on_click(self, event):
        """Handle mouse click on canvas"""
        clicked_item = self.canvas.find_closest(event.x, event.y)[0]
        
        # Check if clicked on a target
        target_ids = [t['id'] for t in self.targets]
        if clicked_item in target_ids:
            self.grabbed_target = clicked_item
            # Highlight grabbed target
            self.canvas.itemconfig(clicked_item, outline='yellow', width=5)
            self.canvas.tag_raise(clicked_item)  # Bring to front
    
    def on_drag(self, event):
        """Handle dragging of targets"""
        if self.grabbed_target:
            # Get target size for proper centering
            target_size = 15  # Default size
            for target in self.targets:
                if target['id'] == self.grabbed_target:
                    target_size = target['size'] // 2
                    break
            
            # Update target position
            self.canvas.coords(self.grabbed_target, 
                             event.x - target_size, event.y - target_size,
                             event.x + target_size, event.y + target_size)
    
    def on_release(self, event):
        """Handle release of dragged target"""
        if self.grabbed_target:
            # Find what's under the mouse
            overlapping = self.canvas.find_overlapping(event.x-10, event.y-10, 
                                                     event.x+10, event.y+10)
            
            target_color = None
            for target in self.targets:
                if target['id'] == self.grabbed_target:
                    target_color = target['color']
                    break
            
            # Check for correct drop
            correct_drop = False
            for zone in self.drop_zones:
                if zone['id'] in overlapping and zone['color'] == target_color:
                    correct_drop = True
                    # Success animation
                    self.canvas.create_text(event.x, event.y - 30, text="✅ Correct!", 
                                          fill='#2ecc71', font=('Arial', 12, 'bold'),
                                          tags="temp")
                    self.canvas.after(1000, lambda: self.canvas.delete("temp"))
                    
                    # Remove target and zone
                    self.canvas.delete(self.grabbed_target)
                    self.canvas.delete(zone['id'])
                    self.targets = [t for t in self.targets if t['id'] != self.grabbed_target]
                    self.drop_zones = [z for z in self.drop_zones if z['id'] != zone['id']]
                    self.successful_attempts += 1
                    self.score += 10 * self.current_level
                    break
            
            if not correct_drop:
                # Error feedback
                self.canvas.create_text(event.x, event.y - 30, text="❌ Wrong zone!", 
                                      fill='#e74c3c', font=('Arial', 12, 'bold'),
                                      tags="temp")
                self.canvas.after(1000, lambda: self.canvas.delete("temp"))
                # Reset highlight
                self.canvas.itemconfig(self.grabbed_target, outline='white', width=3)
            
            self.grabbed_target = None
            self.total_attempts += 1
            
            # Check level completion
            if not self.targets:
                self.level_completed()
    
    def level_completed(self):
        """Handle level completion and settings optimization"""
        completion_time = time.time() - self.start_time
        accuracy = (self.successful_attempts / max(self.total_attempts, 1)) * 100
        
        self.completion_times.append(completion_time)
        self.accuracy_scores.append(accuracy)
        
        # Calculate performance score
        time_score = max(0, 100 - completion_time * 3)
        accuracy_score = accuracy
        performance_score = (time_score + accuracy_score) / 2
        
        # Show completion feedback
        self.show_level_feedback(completion_time, accuracy, performance_score)
        
        # Update level and UI
        self.current_level += 1
        self.update_display()
        
        # Enable start button for next level
        self.start_btn.config(state='normal', text='🚀 Next Level')
        self.is_running = False
        
    def show_level_feedback(self, time_taken, accuracy, score):
        """Show level completion feedback"""
        # Clear canvas
        self.canvas.delete("all")
        
        # Celebration message
        messages = ["🎉 Excellent!", "⭐ Great job!", "🚀 Amazing!", "💪 Well done!", "🎯 Perfect!"]
        celebration = random.choice(messages)
        
        feedback_text = f"{celebration}\n\n" \
                       f"Level {self.current_level} Completed!\n\n" \
                       f"⏱️ Time: {time_taken:.1f} seconds\n" \
                       f"🎯 Accuracy: {accuracy:.1f}%\n" \
                       f"📊 Performance Score: {score:.1f}\n\n" \
                       f"How did the cursor movement feel?\n" \
                       f"Select feedback below to optimize settings!"
        
        self.canvas.create_text(400, 200, text=feedback_text, fill='white',
                               font=('Arial', 14), justify=tk.CENTER)
    
    def apply_feedback(self):
        """Apply user feedback to optimize settings using BFS"""
        if not self.feedback_var.get():
            return
        
        # Calculate current performance score
        recent_scores = self.accuracy_scores[-3:] if len(self.accuracy_scores) >= 3 else self.accuracy_scores
        avg_accuracy = np.mean(recent_scores) if recent_scores else 50
        
        recent_times = self.completion_times[-3:] if len(self.completion_times) >= 3 else self.completion_times
        avg_time = np.mean(recent_times) if recent_times else 10
        
        performance_score = avg_accuracy * (50 / max(avg_time, 1))
        
        # Get optimized settings using BFS
        new_settings = self.optimizer.bfs_optimize(performance_score, self.feedback_var.get())
        
        # Apply new settings to cursor controller
        if hasattr(self.cursor_controller, 'set_adaptive_settings'):
            self.cursor_controller.set_adaptive_settings(
                new_settings['sensitivity'],
                new_settings['smoothing'], 
                new_settings['acceleration']
            )
        
        # Update display
        self.settings_label.config(
            text=f"Sensitivity: {new_settings['sensitivity']:.1f} | "
                 f"Smoothing: {new_settings['smoothing']:.2f} | "
                 f"Acceleration: {new_settings['acceleration']:.1f}"
        )
        
        # Show optimization feedback
        optimization_text = f"🤖 AI Optimization Applied!\n\n" \
                           f"New Settings:\n" \
                           f"• Sensitivity: {new_settings['sensitivity']:.1f}\n" \
                           f"• Smoothing: {new_settings['smoothing']:.2f}\n" \
                           f"• Acceleration: {new_settings['acceleration']:.1f}\n\n" \
                           f"Ready for next level?"
        
        self.canvas.delete("all")
        self.canvas.create_text(400, 200, text=optimization_text, fill='#f39c12',
                               font=('Arial', 12), justify=tk.CENTER)
        
        # Clear feedback selection
        self.feedback_var.set("")
        
        print(f"Settings optimized based on feedback: {self.feedback_var.get()}")
    
    def game_loop(self):
        """Main game loop"""
        if self.is_running:
            self.update_display()
            self.game_window.after(100, self.game_loop)
    
    def update_display(self):
        """Update game display"""
        self.level_label.config(text=f"Level: {self.current_level}")
        self.score_label.config(text=f"Score: {self.score}")
        
        if self.total_attempts > 0:
            accuracy = (self.successful_attempts / self.total_attempts) * 100
            self.accuracy_label.config(text=f"Accuracy: {accuracy:.1f}%")
    
    def reset_game(self):
        """Reset the game to initial state"""
        self.is_running = False
        self.current_level = 1
        self.score = 0
        self.total_attempts = 0
        self.successful_attempts = 0
        self.completion_times = []
        self.accuracy_scores = []
        
        self.canvas.delete("all")
        self.start_btn.config(state='normal', text='🚀 Start Training')
        self.feedback_var.set("")
        
        # Reset optimizer
        self.optimizer = AdaptiveSettingsOptimizer()
        self.settings_label.config(text="Sensitivity: 1.0 | Smoothing: 0.3 | Acceleration: 1.5")
        
        # Show initial instructions
        self.show_initial_instructions()
        
        print("Training game reset")
        
    def close(self):
        """Close the game window"""
        self.is_running = False
        if self.game_window:
            self.game_window.destroy()
        print("Training game closed")

# Test function to run the game standalone
if __name__ == "__main__":
    class MockCursorController:
        def set_adaptive_settings(self, sensitivity, smoothing, acceleration):
            print(f"Mock settings: S={sensitivity}, Sm={smoothing}, A={acceleration}")
    
    root = tk.Tk()
    root.withdraw()  # Hide main window
    
    mock_controller = MockCursorController()
    game = TrainingGame(root, mock_controller)
    
    root.mainloop()
