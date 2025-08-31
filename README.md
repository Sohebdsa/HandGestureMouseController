# Hand Cursor Control with DroidCam Support

A Python application that enables full mouse cursor control using hand gestures, with support for both local webcams and phone cameras via DroidCam. Perfect for accessibility, presentations, or hands-free computing.

![Python](https://img.shields.io/badge/Python-3.7%2B-blue) ![OpenCV](https://img.shields.io/badge/OpenCV-4.8.1-green) ![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.7-yellow) ![License](https://img.shields.io/badge/License-MIT-red)

## 🎯 Features

- **Real-time Hand Tracking**: Uses MediaPipe for accurate hand detection and gesture recognition
- **Multiple Camera Support**: Works with local webcams and DroidCam (phone camera)
- **Intuitive Gestures**: Natural hand movements for cursor control
- **Professional GUI**: Clean, responsive interface with real-time feedback
- **Adaptive Training Game**: Built-in game to optimize cursor sensitivity and smoothing
- **Customizable Settings**: Adjustable sensitivity, smoothing, and gesture assignments
- **Accessibility Focused**: Designed for users who prefer hands-free interaction

## 🤚 Gesture Controls

| Gesture | Action | Description |
|---------|--------|-------------|
| 👆 **Point** | Move Cursor | Point with index finger to move cursor |
| 🤏 **Pinch** | Click / Hold | Quick pinch = click, Hold pinch = drag mode |
| ✊ **Fist** | Left Click | Alternative left click gesture |
| ✌️ **Peace** | Right Click | Two-finger gesture for right-click |
| 🖐️ **Open Hand** | Scroll Up | Open hand gesture for scrolling |

## 🚀 Installation & Setup

### Prerequisites
- **Python**: 3.7 or higher
- **Camera**: Local webcam or DroidCam-compatible phone

### Windows Installation
1. Download Python from [python.org](https://python.org), run installer and check "Add Python to PATH"
2. Open Command Prompt and verify: `python --version`
3. Clone repository: `git clone https://github.com/yourusername/hand-cursor-control.git`
4. Navigate to folder: `cd hand-cursor-control`
5. Create virtual environment: `python -m venv hand_cursor_env`
6. Activate environment: `hand_cursor_env\Scripts\activate`
7. Install dependencies: `pip install -r requirements.txt`
8. Run application: `python main.py`

### macOS Installation
1. Install Python via Homebrew: `brew install python` or download from python.org
2. Clone repository: `git clone https://github.com/yourusername/hand-cursor-control.git`
3. Navigate to folder: `cd hand-cursor-control`
4. Create virtual environment: `python -m venv hand_cursor_env`
5. Activate environment: `source hand_cursor_env/bin/activate`
6. Install dependencies: `pip install -r requirements.txt`
7. Run application: `python main.py`

### Linux Installation (Ubuntu/Debian)
1. Install Python: `sudo apt update && sudo apt install python3 python3-pip`
2. Clone repository: `git clone https://github.com/yourusername/hand-cursor-control.git`
3. Navigate to folder: `cd hand-cursor-control`
4. Create virtual environment: `python3 -m venv hand_cursor_env`
5. Activate environment: `source hand_cursor_env/bin/activate`
6. Install dependencies: `pip install -r requirements.txt`
7. Run application: `python main.py`

### Required Dependencies (requirements.txt)
opencv-python==4.8.1.78
mediapipe==0.10.7
pyautogui==0.9.54
numpy==1.24.3
pillow==10.0.1
requests==2.31.0

## 📱 DroidCam Setup

To use your phone as a camera: Download DroidCam from Google Play Store or App Store, ensure phone and computer are on same WiFi network, note IP address shown in DroidCam app, select "DroidCam (Phone)" in application and enter IP address, test connection before starting tracking. For Windows users, download DroidCam drivers from [dev47apps.com](https://www.dev47apps.com/).

## 🎮 Usage & Configuration

Run `python main.py`, select camera source (local webcam or DroidCam), adjust sensitivity and smoothing settings, click "Start Tracking" to begin hand cursor control, use gestures to control mouse cursor. Access "Adaptive Training Game" to optimize settings through drag-and-drop exercises that automatically adjust difficulty and find optimal sensitivity values using BFS algorithm.

### Gesture Customization
Edit `gesture_settings.json` to customize actions:

## 📁 Project Structure
hand_cursor_control/
├── main.py # Application entry point
├── hand_tracker.py # Hand detection and gesture recognition
├── cursor_controller.py # Mouse cursor control logic
├── gui_controller.py # Main GUI interface
├── gesture_manager.py # Gesture configuration management
├── camera_manager.py # Camera handling (local and DroidCam)
├── adaptive_game.py # Training game module
├── gesture_settings.json # Gesture configuration file
├── requirements.txt # Python dependencies
├── LICENSE # MIT License file
└── README.md # This file


## 🛠️ Advanced Features & Customization

**Development Setup**: Clone repository, create virtual environment, install with `pip install -e ".[dev]"`, run tests with `pytest`, format code with `black .`

**Linux System Service**: Create `/etc/systemd/system/hand-cursor-control.service` with proper User, WorkingDirectory, Environment PATH, and ExecStart configurations, then enable with `sudo systemctl daemon-reload && sudo systemctl enable hand-cursor-control`

**Adding New Gestures**: Modify `hand_tracker.py` for detection, update `gesture_manager.py` with action types, add assignments in `gesture_settings.json`, update gesture guide in `gui_controller.py`

**UI Customization**: Modify color schemes and layouts in `gui_controller.py`, adjust styling in GUI setup methods, add new controls as needed

## 🤝 Contributing & Support

**Contributing**: Fork repository, create feature branch (`git checkout -b feature/AmazingFeature`), commit changes (`git commit -m 'Add AmazingFeature'`), push to branch (`git push origin feature/AmazingFeature`), open Pull Request

**Getting Help**: Check troubleshooting section, review existing GitHub Issues, create new issue with OS details, Python version (`python --version`), full error message, and reproduction steps

**Roadmap**: Multiple hand tracking, voice commands integration, machine learning for personalized gestures, mobile app companion, eye tracking support

## 📄 License & Acknowledgments

Licensed under MIT License. Built with **MediaPipe** for hand tracking, **OpenCV** for computer vision, **PyAutoGUI** for cursor control, **DroidCam** for mobile camera integration.

## 🎯 Quick Start Summary

1. Install Python 3.7+
2. Clone: `git clone https://github.com/yourusername/hand-cursor-control.git`
3. Setup: `cd hand-cursor-control && python -m venv hand_cursor_env`
4. Activate: `hand_cursor_env\Scripts\activate` (Windows) or `source hand_cursor_env/bin/activate` (macOS/Linux)
5. Install: `pip install -r requirements.txt`
6. Run: `python main.py`
7. Configure camera source and start tracking
8. Use hand gestures to control cursor

**Made by sohebdsa with ❤️ for accessibility and hands-free computing** - Give a ⭐️ if this project helped you! Happy hand controlling! 🤚✨

