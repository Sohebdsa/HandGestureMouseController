#!/usr/bin/env python3
"""
Hand Cursor Control Application with DroidCam Support

This application uses hand gestures to control the mouse cursor.
It supports both local webcams and phone cameras via DroidCam.

Features:
- Local webcam support
- DroidCam (phone camera) support
- Real-time gesture recognition
- GUI with camera selection and testing

Author: Your Name
Date: July 2025
"""

import sys
import os
from hand_tracker import HandTracker
from cursor_controller import CursorController
from gui_controller import GUIController

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_modules = ['cv2', 'mediapipe', 'pyautogui', 'tkinter', 'PIL', 'requests']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print("Missing required modules:")
        for module in missing_modules:
            print(f"  - {module}")
        print("\nPlease install missing modules using:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def print_droidcam_setup_guide():
    """Print DroidCam setup instructions"""
    print("\nDroidCam Setup Guide:")
    print("=" * 50)
    print("1. Download DroidCam app from Google Play Store")
    print("2. Install DroidCam on your Android phone")
    print("3. Connect both phone and PC to the same WiFi network")
    print("4. Open DroidCam app on your phone")
    print("5. Note the IP address displayed (e.g., 192.168.1.100)")
    print("6. In the application, select 'DroidCam (Phone)' option")
    print("7. Enter the IP address and click 'Test Connection'")
    print("8. Once connected, click 'Start Tracking'")
    print("\nTroubleshooting:")
    print("- Ensure both devices are on the same network")
    print("- Check firewall settings if connection fails")
    print("- Try restarting the DroidCam app")

def main():
    """Main application entry point"""
    print("Hand Cursor Control Application with DroidCam Support")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Print setup guide
    print_droidcam_setup_guide()
    
    try:
        # Initialize components
        print("\nInitializing hand tracker...")
        hand_tracker = HandTracker()
        
        print("Initializing cursor controller...")
        cursor_controller = CursorController()
        
        print("Starting GUI...")
        gui = GUIController(hand_tracker, cursor_controller)
        
        # Run the application
        gui.run()
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        print("Application closed")

if __name__ == "__main__":
    main()
