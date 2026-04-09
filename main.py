
import cv2
import mediapipe as mp
import time
import threading
import tkinter as tk
from PIL import Image, ImageTk
from scipy.spatial.distance import euclidean
import pygame

# ---------------- CONFIG ----------------

class Config:
    CAMERA_INDEX = 0

    DROWSY_TIME = 2.0
    YAWN_TIME = 2.0
    HEAD_TIME = 2.0

    UI_REFRESH_MS = 20
    ALARM_SOUND = "warning (1).mp3"

    BG = "#0d1117"
    PANEL = "#161b22"
    ACCENT = "#58a6ff"
    OK = "#3fb950"
    DANGER = "#f85149"

# ---------------- STATE ----------------

class State:
    def __init__(self):
        self.lock = threading.Lock()
        self.running = False
        self.frame = None

        self.eye_state = "OPEN"
        self.yawn_count = 0
        self.drowsy_count = 0
        self.head_down_count = 0

        self.logs = []
        self.status = "Initializing..."

# ---------------- ALARM ----------------

class Alarm:
    def __init__(self, path):
        pygame.mixer.init()
        self.sound = pygame.mixer.Sound(path)
        self.playing = False

    def play(self):
        if not self.playing:
            self.sound.play(loops=-1)
            self.playing = True

    def stop(self):
        if self.playing:
            self.sound.stop()
            self.playing = False

# ---------------- DETECTOR ----------------

class Detector(threading.Thread):
    def __init__(self, state, cfg, alarm):
        super().__init__(daemon=True)
        self.state = state
        self.cfg = cfg
        self.alarm = alarm

        self.cap = cv2.VideoCapture(cfg.CAMERA_INDEX)
        self.face = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)

        # timers
        self.eye_start = None
        self.yawn_start = None
        self.head_start = None

        # flags (prevent duplicate count)
        self.drowsy_flag = False
        self.yawn_flag = False
        self.head_flag = False

        # calibration
        self.calibrating = True
        self.start_time = time.time()
        self.calib_time = 5

        self.ear_samples = []
        self.mar_samples = []	
        self.nose_samples = []

        self.EAR_T = 0.23
        self.MAR_T = 0.07
        self.HEAD_BASE = 0.5

    def EAR(self, lm, idx, w, h):
        pts = [(int(lm[i].x*w), int(lm[i].y*h)) for i in idx]
        A = euclidean(pts[1], pts[5])
        B = euclidean(pts[2], pts[4])
        C = euclidean(pts[0], pts[3])
        return (A+B)/(2.0*C)

    def log(self, text):
        now = time.strftime("%H:%M:%S")
        with self.state.lock:
            self.state.logs.append(f"[{now}] {text}")

    def run(self):
        while self.state.running:
            ret, frame = self.cap.read()
            if not ret:
                continue

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = self.face.process(rgb)

            status = "No Face"
            eye_state = "UNKNOWN"

            if res.multi_face_landmarks:

                if len(res.multi_face_landmarks) > 1:
                    status = "MULTIPLE FACES"
                    self.alarm.play()
                    self.log("Multiple faces detected!")
                else:
                    lm = res.multi_face_landmarks[0].landmark
                    h, w = frame.shape[:2]

                    left_eye = [33,160,158,133,153,144]
                    right_eye = [362,385,387,263,373,380]

                    ear = (self.EAR(lm,left_eye,w,h) +
                           self.EAR(lm,right_eye,w,h))/2

                    mar = abs(lm[13].y - lm[14].y)
                    nose = lm[1].y

                    # CALIBRATION
                    if self.calibrating:
                        self.ear_samples.append(ear)
                        self.mar_samples.append(mar)
                        self.nose_samples.append(nose)

                        remain = int(self.calib_time - (time.time()-self.start_time))
                        cv2.putText(frame,f"Calibrating {remain}s",(30,50),
                                    cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,255),2)

                        if time.time()-self.start_time > self.calib_time:
                            self.EAR_T = sum(self.ear_samples)/len(self.ear_samples)*0.75
                            self.MAR_T = sum(self.mar_samples)/len(self.mar_samples)*1.5
                            self.HEAD_BASE = sum(self.nose_samples)/len(self.nose_samples)
                            self.calibrating = False
                            self.log("Calibration Done")

                        status = "Calibrating..."
                    else:
                        status = "Normal"

                        # -------- EYE --------
                        if ear < self.EAR_T:
                            eye_state = "CLOSED"
                            if self.eye_start is None:
                                self.eye_start = time.time()
                        else:
                            eye_state = "OPEN"
                            self.eye_start = None
                            self.drowsy_flag = False

                        # -------- DROWSY --------
                        if self.eye_start and time.time()-self.eye_start > self.cfg.DROWSY_TIME:
                            status = "DROWSY"
                            if not self.drowsy_flag:
                                self.state.drowsy_count += 1
                                self.log("Drowsy detected")
                                self.drowsy_flag = True

                        # -------- YAWN -------- (FIXED)
                        if mar > self.MAR_T:
                            if self.yawn_start is None:
                                self.yawn_start = time.time()
                        else:
                            self.yawn_start = None
                            self.yawn_flag = False

                        if self.yawn_start and time.time()-self.yawn_start > self.cfg.YAWN_TIME:
                            status = "YAWNING"
                            if not self.yawn_flag:
                                self.state.yawn_count += 1
                                self.log("Yawning detected")
                                self.yawn_flag = True

                        # -------- HEAD DOWN (STRICT FIX) --------
                        if nose > self.HEAD_BASE + 0.10 and eye_state == "CLOSED":
                            if self.head_start is None:
                                self.head_start = time.time()
                        else:
                            self.head_start = None
                            self.head_flag = False

                        if self.head_start and time.time()-self.head_start > self.cfg.HEAD_TIME:
                            status = "HEAD DOWN"
                            if not self.head_flag:
                                self.state.head_down_count += 1
                                self.log("Head Down detected")
                                self.head_flag = True

                        # -------- ALARM --------
                        if status != "Normal":
                            self.alarm.play()
                        else:
                            self.alarm.stop()

            else:
                self.alarm.stop()

            with self.state.lock:
                self.state.frame = frame
                self.state.status = status
                self.state.eye_state = eye_state

        self.cap.release()

# ---------------- GUI (OLD STYLE) ----------------

class App:
    def __init__(self):
        self.cfg = Config()
        self.state = State()
        self.alarm = Alarm(self.cfg.ALARM_SOUND)

        self.root = tk.Tk()
        self.root.title("Driver Monitoring Dashboard")
        self.root.geometry("1200x700")
        self.root.resizable(False, False)
        self.root.configure(bg=self.cfg.BG)

        main = tk.Frame(self.root, bg=self.cfg.BG)
        main.pack(fill="both", expand=True)

        # LEFT CAMERA
        self.left = tk.Frame(main, width=800, height=600, bg=self.cfg.BG)
        self.left.pack(side="left")
        self.left.pack_propagate(False)

        self.video = tk.Label(self.left, bg="black")
        self.video.pack(fill="both", expand=True)

        # RIGHT PANEL
        self.right = tk.Frame(main, width=350, bg=self.cfg.PANEL)
        self.right.pack(side="right", fill="y")

        tk.Label(self.right, text="Driver Monitor",
                 font=("Arial",18,"bold"),
                 fg=self.cfg.ACCENT, bg=self.cfg.PANEL).pack(pady=20)

        self.eye = tk.Label(self.right, fg="white", bg=self.cfg.PANEL)
        self.eye.pack(pady=5)

        self.yawn = tk.Label(self.right, fg="white", bg=self.cfg.PANEL)
        self.yawn.pack(pady=5)

        self.drowsy = tk.Label(self.right, fg="white", bg=self.cfg.PANEL)
        self.drowsy.pack(pady=5)

        self.head = tk.Label(self.right, fg="white", bg=self.cfg.PANEL)
        self.head.pack(pady=5)

        self.status = tk.Label(self.right, font=("Arial",16,"bold"),
                               bg=self.cfg.PANEL)
        self.status.pack(pady=20)

        tk.Button(self.right,text="Start",bg=self.cfg.ACCENT,
                  command=self.start).pack(pady=5)

        tk.Button(self.right,text="Stop",bg="#444",
                  command=self.stop).pack(pady=5)

        tk.Button(self.right,text="Exit",bg=self.cfg.DANGER,
                  command=self.exit).pack(pady=5)

        # LOG BOX
        self.log_box = tk.Text(self.right, height=10, bg="black", fg="lime")
        self.log_box.pack(pady=10)

        self.detector = None
        self.update_ui()
        self.root.mainloop()

    def start(self):
        if not self.state.running:
            self.state.running = True
            self.detector = Detector(self.state,self.cfg,self.alarm)
            self.detector.start()

    def stop(self):
        self.state.running = False
        self.alarm.stop()

    def exit(self):
        self.stop()
        self.root.destroy()

    def update_ui(self):
        with self.state.lock:
            frame = self.state.frame
            status = self.state.status
            eye = self.state.eye_state
            y = self.state.yawn_count
            d = self.state.drowsy_count
            h = self.state.head_down_count
            logs = self.state.logs[-5:]

        if frame is not None:
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(img)
            img = img.resize((800,600))
            img = ImageTk.PhotoImage(img)
            self.video.imgtk = img
            self.video.config(image=img)

        self.eye.config(text=f"Eye: {eye}")
        self.yawn.config(text=f"Yawn: {y}")
        self.drowsy.config(text=f"Drowsy: {d}")
        self.head.config(text=f"Head Down: {h}")
        self.status.config(text=f"Status: {status}",
                           fg=self.cfg.OK if status=="Normal" else self.cfg.DANGER)

        # LOG UPDATE
        self.log_box.delete(1.0, tk.END)
        for log in logs:
            self.log_box.insert(tk.END, log + "\n")

        self.root.after(self.cfg.UI_REFRESH_MS, self.update_ui)

if __name__ == "__main__":
    App()