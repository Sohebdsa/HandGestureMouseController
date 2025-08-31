import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

class GestureManager:
    """Manages custom gesture assignments and actions"""
    
    def __init__(self, cursor_controller):
        self.cursor_controller = cursor_controller
        self.settings_file = "gesture_settings.json"
        
        # Default gesture assignments
        self.default_actions = {
            "point": {"action": "cursor_move", "params": {}},
            "pinch": {"action": "click_hold", "params": {}},
            "fist": {"action": "left_click", "params": {}},
            "peace": {"action": "right_click", "params": {}},
            "open_hand": {"action": "scroll_up", "params": {}}
        }
        
        # Available actions
        self.available_actions = {
            "cursor_move": "Move Cursor",
            "left_click": "Left Click",
            "right_click": "Right Click",
            "double_click": "Double Click",
            "click_hold": "Click and Hold",
            "scroll_up": "Scroll Up",
            "scroll_down": "Scroll Down",
            "key_press": "Press Key",
            "key_combo": "Key Combination",
            "no_action": "No Action"
        }
        
        # Current gesture assignments
        self.gesture_actions = self.load_settings()
        
    def load_settings(self):
        """Load gesture settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            return self.default_actions.copy()
        except Exception as e:
            print(f"Error loading settings: {e}")
            return self.default_actions.copy()
    
    def save_settings(self):
        """Save gesture settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.gesture_actions, f, indent=2)
            print("Gesture settings saved")
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def execute_gesture_action(self, gesture, landmarks=None):
        """Execute the assigned action for a gesture"""
        if gesture not in self.gesture_actions:
            return
        
        action_config = self.gesture_actions[gesture]
        action = action_config["action"]
        params = action_config.get("params", {})
        
        try:
            if action == "cursor_move":
                # This is handled by the main tracking loop
                pass
            elif action == "left_click":
                self.cursor_controller.click()
            elif action == "right_click":
                self.cursor_controller.right_click()
            elif action == "double_click":
                self.cursor_controller.double_click()
            elif action == "click_hold":
                # This is handled by pinch gesture logic
                pass
            elif action == "scroll_up":
                self.cursor_controller.scroll("up")
            elif action == "scroll_down":
                self.cursor_controller.scroll("down")
            elif action == "key_press":
                key = params.get("key", "space")
                self.cursor_controller.key_press(key)
            elif action == "key_combo":
                keys = params.get("keys", ["ctrl", "c"])
                self.cursor_controller.key_combination(*keys)
            elif action == "no_action":
                pass
        except Exception as e:
            print(f"Error executing action {action}: {e}")
    
    def open_assignment_window(self, parent):
        """Open gesture assignment window"""
        self.assignment_window = tk.Toplevel(parent)
        self.assignment_window.title("Gesture Assignment Settings")
        self.assignment_window.geometry("600x500")
        self.assignment_window.resizable(False, False)
        
        # Make window modal
        self.assignment_window.transient(parent)
        self.assignment_window.grab_set()
        
        self.setup_assignment_ui()
    
    def setup_assignment_ui(self):
        """Setup the assignment UI"""
        # Header
        header_frame = tk.Frame(self.assignment_window, bg='#2c3e50', height=60)
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="🎭 Gesture Action Assignment", 
                              font=('Arial', 16, 'bold'), fg='white', bg='#2c3e50')
        title_label.pack(pady=15)
        
        # Main content
        content_frame = tk.Frame(self.assignment_window)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Gesture assignment grid
        gestures = ["point", "pinch", "fist", "peace", "open_hand"]
        gesture_emojis = {"point": "👆", "pinch": "🤏", "fist": "✊", "peace": "✌️", "open_hand": "🖐️"}
        
        self.action_vars = {}
        self.param_entries = {}
        
        for i, gesture in enumerate(gestures):
            # Gesture label
            gesture_frame = tk.Frame(content_frame)
            gesture_frame.grid(row=i, column=0, columnspan=3, sticky='w', pady=10)
            
            emoji_label = tk.Label(gesture_frame, text=gesture_emojis[gesture], 
                                  font=('Arial', 20))
            emoji_label.pack(side=tk.LEFT, padx=(0, 10))
            
            gesture_label = tk.Label(gesture_frame, text=f"{gesture.title()} Gesture:", 
                                   font=('Arial', 12, 'bold'))
            gesture_label.pack(side=tk.LEFT)
            
            # Action selection
            action_frame = tk.Frame(content_frame)
            action_frame.grid(row=i, column=1, sticky='w', padx=20, pady=5)
            
            self.action_vars[gesture] = tk.StringVar()
            current_action = self.gesture_actions.get(gesture, {}).get("action", "no_action")
            self.action_vars[gesture].set(current_action)
            
            action_combo = ttk.Combobox(action_frame, textvariable=self.action_vars[gesture],
                                       values=list(self.available_actions.keys()),
                                       state="readonly", width=15)
            action_combo.pack()
            action_combo.bind('<<ComboboxSelected>>', 
                             lambda e, g=gesture: self.on_action_change(g))
            
            # Parameters entry
            param_frame = tk.Frame(content_frame)
            param_frame.grid(row=i, column=2, sticky='w', padx=20, pady=5)
            
            self.param_entries[gesture] = tk.Entry(param_frame, width=20)
            self.param_entries[gesture].pack()
            
            # Load current parameters
            current_params = self.gesture_actions.get(gesture, {}).get("params", {})
            if "key" in current_params:
                self.param_entries[gesture].insert(0, current_params["key"])
            elif "keys" in current_params:
                self.param_entries[gesture].insert(0, ",".join(current_params["keys"]))
        
        # Buttons
        button_frame = tk.Frame(self.assignment_window)
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        save_btn = tk.Button(button_frame, text="💾 Save Settings", 
                            command=self.save_assignments, font=('Arial', 10, 'bold'),
                            bg='#27ae60', fg='white', padx=20, pady=5)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        reset_btn = tk.Button(button_frame, text="🔄 Reset to Default", 
                             command=self.reset_to_default, font=('Arial', 10),
                             bg='#e74c3c', fg='white', padx=20, pady=5)
        reset_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(button_frame, text="❌ Cancel", 
                              command=self.assignment_window.destroy, font=('Arial', 10),
                              bg='#95a5a6', fg='white', padx=20, pady=5)
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        # Instructions
        instr_text = ("Instructions:\n"
                     "• Select action for each gesture\n"
                     "• For 'Press Key': enter key name (e.g., 'space', 'enter')\n"
                     "• For 'Key Combination': enter keys separated by commas (e.g., 'ctrl,c')")
        
        instr_label = tk.Label(self.assignment_window, text=instr_text,
                              font=('Arial', 9), justify=tk.LEFT, fg='gray')
        instr_label.pack(pady=(0, 10))
    
    def on_action_change(self, gesture):
        """Handle action selection change"""
        action = self.action_vars[gesture].get()
        param_entry = self.param_entries[gesture]
        
        # Clear and configure parameter entry based on action
        param_entry.delete(0, tk.END)
        
        if action == "key_press":
            param_entry.config(state='normal')
            param_entry.insert(0, "space")
        elif action == "key_combo":
            param_entry.config(state='normal')
            param_entry.insert(0, "ctrl,c")
        else:
            param_entry.config(state='disabled')
    
    def save_assignments(self):
        """Save gesture assignments"""
        for gesture in self.action_vars:
            action = self.action_vars[gesture].get()
            param_text = self.param_entries[gesture].get()
            
            params = {}
            if action == "key_press" and param_text:
                params["key"] = param_text
            elif action == "key_combo" and param_text:
                params["keys"] = [k.strip() for k in param_text.split(",")]
            
            self.gesture_actions[gesture] = {
                "action": action,
                "params": params
            }
        
        self.save_settings()
        messagebox.showinfo("Settings Saved", "Gesture assignments have been saved!")
        self.assignment_window.destroy()
    
    def reset_to_default(self):
        """Reset to default gesture assignments"""
        if messagebox.askyesno("Reset Settings", "Reset all gestures to default assignments?"):
            self.gesture_actions = self.default_actions.copy()
            self.save_settings()
            messagebox.showinfo("Reset Complete", "Gesture assignments reset to default!")
            self.assignment_window.destroy()
