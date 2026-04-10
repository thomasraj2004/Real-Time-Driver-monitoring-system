# Real-Time-Driver-monitoring-system
Real-Time Driver monitoring system

## 📌 Project Overview

The **Driver Monitoring System** is a real-time computer vision application designed to detect driver fatigue and inattentiveness. It uses a webcam to monitor facial features and identify dangerous behaviors such as:

* 😴 Drowsiness (eye closure)
* 😮 Yawning
* 🧠 Head down posture
* 👥 Multiple face detection (distraction)

This system helps in improving road safety by alerting the driver with an alarm.

---

## 🎯 Objectives

* Detect driver fatigue in real-time
* Alert driver using sound alarm
* Reduce road accidents caused by drowsiness
* Provide a simple GUI dashboard for monitoring

---

## 🛠️ Technologies Used

| Technology   | Purpose                          |
| ------------ | -------------------------------- |
| Python       | Core programming language        |
| OpenCV       | Video capture & image processing |
| MediaPipe    | Face landmark detection          |
| Tkinter      | GUI interface                    |
| Pygame       | Alarm sound                      |
| SciPy        | Distance calculation             |
| PIL (Pillow) | Image display                    |

---

## ⚙️ Features

* ✅ Real-time face detection
* ✅ Eye Aspect Ratio (EAR) for drowsiness detection
* ✅ Mouth Aspect Ratio (MAR) for yawning detection
* ✅ Head position tracking
* ✅ Automatic calibration (first 5 seconds)
* ✅ Alarm system
* ✅ Live dashboard with logs

---

## 🧠 How It Works

1. Webcam captures video frames
2. MediaPipe detects facial landmarks
3. System calculates:

   * **EAR (Eye Aspect Ratio)** → detects eye closure
   * **MAR (Mouth Aspect Ratio)** → detects yawning
   * **Nose position** → detects head movement
4. If thresholds are exceeded:

   * Status changes (Drowsy / Yawning / Head Down)
   * Alarm is triggered
5. GUI displays live data

---

## 📂 Project Structure

```
Driver-Monitoring-System/
│
├── main.py                # Main application code
├── warning (1).mp3       # Alarm sound file
├── README.md              # Project documentation
```

---

## 🧪 Installation & Setup

### Step 1: Install Python

Download and install Python (>=3.8)

👉 https://www.python.org/downloads/

---

### Step 2: Install Required Libraries

Open terminal / command prompt and run:

```bash
pip install opencv-python mediapipe pillow scipy pygame
```

---

### Step 3: Add Alarm Sound

Make sure your project folder contains:

```
warning (1).mp3
```

Or update this line in code:

```python
ALARM_SOUND = "your_sound.mp3"
```

---

### Step 4: Run the Project

```bash
python main.py
```

---

## ▶️ Usage

1. Click **Start**
2. Sit in front of camera
3. System will **calibrate for 5 seconds**
4. After calibration:

   * Normal → No alert
   * Drowsy/Yawning → Alarm triggers
5. Click **Stop** to end detection

---

## 📊 Output

* Live webcam feed
* Driver status display
* Event counters:

  * Yawn count
  * Drowsy count
  * Head down count
* Logs of events

---

## ⚠️ Limitations

* Works best with good lighting
* Single person detection preferred
* Accuracy depends on camera quality
* Not suitable for extreme angles

---

## 🚀 Future Improvements

* Mobile app integration
* Cloud data storage
* AI model improvements
* Night vision support
* Driver identity recognition

---

## 👨‍💻 Author

THOMAS RAJ S

---

## 📜 License

This project is for educational purposes.

---------------------------------------------------------------------------------


## 🚀 How to Run the Project (Step-by-Step Guide)

Follow these steps to set up and run the Driver Monitoring System on your computer.

---

### 🧩 Prerequisites

Make sure you have the following installed:

* Python (version 3.8 or higher)
* Webcam (built-in or external)
* Internet connection (for installing libraries)

---

### 🔧 Step 1: Clone the Repository

Open your terminal or command prompt and run:

```bash
cd Driver-Monitoring-System
```

---

### 📦 Step 2: Create Virtual Environment (Recommended)

```bash
python -m venv venv
```

#### Activate it:

**Windows:**

```bash
venv\Scripts\activate
```

**Mac/Linux:**

```bash
source venv/bin/activate
```

---

### 📥 Step 3: Install Dependencies

Install all required Python libraries:

```bash
pip install opencv-python mediapipe pillow scipy pygame

---

### 🔊 Step 4: Add Alarm Sound File

Ensure the following file is present in your project folder:

```bash
warning (1).mp3
```

If not, you can:

* Add your own `.mp3` file
* Or update this line in the code:

```python
ALARM_SOUND = "your_sound.mp3"
```

---

### ▶️ Step 5: Run the Application

```bash
python main.py
```

---

### 🖥️ Step 6: Use the Application

1. Click **Start**
2. Sit in front of the camera
3. Wait for **5 seconds calibration**
4. System will start detecting:

   * Eye closure → Drowsiness
   * Yawning → Alert
   * Head down → Warning

---

### ⏹️ Step 7: Stop the Application

* Click **Stop** button to end detection
* Click **Exit** to close the application

---

## 🛠️ Troubleshooting

### ❌ Camera not opening

* Check if another app is using the camera
* Try changing camera index:

```python
CAMERA_INDEX = 1
```

---

### ❌ Module not found error

Run:

```bash
pip install <module_name>
```

---

### ❌ No sound playing

* Check `.mp3` file path
* Ensure system volume is not muted

---

### ❌ Low detection accuracy

* Use good lighting
* Sit facing the camera
* Avoid multiple faces in frame

---

## ✅ You're Ready!

Now your Driver Monitoring System should run successfully 🎉


