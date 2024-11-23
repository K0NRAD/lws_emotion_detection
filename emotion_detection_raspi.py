import cv2
import mediapipe as mp
from fer import FER
import time
import numpy as np
import RPi.GPIO as GPIO
from config import *

class EmotionDetector:
    def __init__(self):
        # GPIO Setup
        self.RELAY_HAPPY = RELAY_CONFIG['HAPPY_PIN']
        self.RELAY_NOT_HAPPY = RELAY_CONFIG['NOT_HAPPY_PIN']
        self.RELAY_DURATION = RELAY_CONFIG['RELAY_DURATION']
        self.setup_gpio()

        # Kamera Setup
        self.cap = cv2.VideoCapture(CAMERA_CONFIG['DEVICE'])
        if not self.cap.isOpened():
            raise ValueError("Failed to open camera")
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_CONFIG['WIDTH'])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_CONFIG['HEIGHT'])
        self.cap.set(cv2.CAP_PROP_FPS, CAMERA_CONFIG['FPS'])

        # Emotion Detection Setup
        self.emotion_detector = FER(mtcnn=True)
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_drawing = mp.solutions.drawing_utils
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=0,
            min_detection_confidence=0.5
        )

        # Adaptive Rate Setup
        self.target_fps = CAMERA_CONFIG['FPS']
        self.process_every_n_frames = DETECTION_CONFIG['PROCESS_EVERY_N_FRAMES']
        self.processing_times = []
        self.max_processing_times = 30
        self.frame_counter = 0
        self.fps = 0
        self.frames_since_update = 0
        self.last_fps_update = time.time()

        # Relais Status
        self.relay_timer = 0
        self.relay_active = False
        self.current_relay = None

    def setup_gpio(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.RELAY_HAPPY, GPIO.OUT)
        GPIO.setup(self.RELAY_NOT_HAPPY, GPIO.OUT)
        GPIO.output(self.RELAY_HAPPY, GPIO.HIGH if RELAY_CONFIG['ACTIVE_LOW'] else GPIO.LOW)
        GPIO.output(self.RELAY_NOT_HAPPY, GPIO.HIGH if RELAY_CONFIG['ACTIVE_LOW'] else GPIO.LOW)

    def update_adaptive_rate(self, processing_time):
        self.processing_times.append(processing_time)

        if len(self.processing_times) > self.max_processing_times:
            self.processing_times.pop(0)

        if len(self.processing_times) >= 5:
            avg_time = np.mean(self.processing_times)
            target_time = 1.0 / self.target_fps

            new_rate = max(1, int(avg_time / target_time))

            if new_rate != self.process_every_n_frames:
                self.process_every_n_frames = int(0.7 * self.process_every_n_frames + 0.3 * new_rate)

            current_time = time.time()
            self.frames_since_update += 1
            if current_time - self.last_fps_update >= 1.0:
                self.fps = self.frames_since_update / (current_time - self.last_fps_update)
                self.frames_since_update = 0
                self.last_fps_update = current_time

    def control_relay(self, is_happy):
        current_time = time.time()
        relay_active_level = GPIO.LOW if RELAY_CONFIG['ACTIVE_LOW'] else GPIO.HIGH
        relay_inactive_level = GPIO.HIGH if RELAY_CONFIG['ACTIVE_LOW'] else GPIO.LOW

        if (not self.relay_active) or (self.current_relay != is_happy):
            GPIO.output(self.RELAY_HAPPY, relay_inactive_level)
            GPIO.output(self.RELAY_NOT_HAPPY, relay_inactive_level)

            if is_happy:
                GPIO.output(self.RELAY_HAPPY, relay_active_level)
                if DEBUG_CONFIG['LOG_LEVEL'] == 'DEBUG':
                    print("Aktiviere Happy-Relais")
            else:
                GPIO.output(self.RELAY_NOT_HAPPY, relay_active_level)
                if DEBUG_CONFIG['LOG_LEVEL'] == 'DEBUG':
                    print("Aktiviere Not-Happy-Relais")

            self.relay_timer = current_time
            self.relay_active = True
            self.current_relay = is_happy

        # Deaktiviere Relais nach Ablauf der Zeit
        elif self.relay_active and (current_time - self.relay_timer >= self.RELAY_DURATION):
            GPIO.output(self.RELAY_HAPPY, relay_inactive_level)
            GPIO.output(self.RELAY_NOT_HAPPY, relay_inactive_level)
            self.relay_active = False
            if DEBUG_CONFIG['LOG_LEVEL'] == 'DEBUG':
                print("Deaktiviere Relais")

    def draw_debug_info(self, frame):
        if DEBUG_CONFIG['SHOW_FPS']:
            cv2.putText(
                frame,
                f"FPS: {self.fps:.1f} | Skip: {self.process_every_n_frames}",
                (10, frame.shape[0] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1
            )

    def run(self):
        print("Starte Emotion Detection... Drücke 'q' zum Beenden")
        try:
            while True:
                frame_start_time = time.time()
                success, frame = self.cap.read()
                if not success:
                    break

                if self.frame_counter % self.process_every_n_frames == 0:
                    # small_frame = cv2.resize(frame,
                    #                          (int(frame.shape[1] * DETECTION_CONFIG['DISPLAY_SCALE']),
                    #                           int(frame.shape[0] * DETECTION_CONFIG['DISPLAY_SCALE'])))

                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    # Gesichtserkennung
                    results = self.face_detection.process(rgb_frame)

                    if results.detections:
                        emotions = self.emotion_detector.detect_emotions(rgb_frame)
                        if emotions:
                            emotion_dict = emotions[0]['emotions']
                            is_happy = emotion_dict['happy'] > DETECTION_CONFIG['HAPPY_THRESHOLD']

                            # Relais steuern
                            self.control_relay(is_happy)

                            # Status anzeigen
                            emotion_text = "Happy" if is_happy else "Not Happy"
                            cv2.putText(
                                frame,
                                f"Emotion: {emotion_text}",
                                (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.7,
                                (0, 255, 0) if is_happy else (0, 0, 255),
                                2
                            )

                            if DEBUG_CONFIG['SHOW_DETECTION_BOXES']:
                                for detection in results.detections:
                                    self.mp_drawing.draw_detection(frame, detection)
                    else:
                        if self.relay_active:
                            GPIO.output(self.RELAY_HAPPY,
                                        GPIO.HIGH if RELAY_CONFIG['ACTIVE_LOW'] else GPIO.LOW)
                            GPIO.output(self.RELAY_NOT_HAPPY,
                                        GPIO.HIGH if RELAY_CONFIG['ACTIVE_LOW'] else GPIO.LOW)
                            self.relay_active = False

                    # Verarbeitungszeit messen und Rate anpassen
                    processing_time = time.time() - frame_start_time
                    self.update_adaptive_rate(processing_time)

                # Debug Informationen
                self.draw_debug_info(frame)

                # Relais-Timer überprüfen
                if self.relay_active:
                    self.control_relay(self.current_relay)

                self.frame_counter += 1

                # Frame anzeigen
                cv2.imshow('Emotion Detection', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        except KeyboardInterrupt:
            print("\nProgramm durch Benutzer beendet")
        except Exception as e:
            print(f"Fehler während der Ausführung: {str(e)}")
        finally:
            self.cleanup()

    def cleanup(self):
        print("Räume auf...")
        self.cap.release()
        cv2.destroyAllWindows()
        GPIO.cleanup()
        print(f"Programm beendet. Finale Stats: FPS: {self.fps:.1f}, " \
              f"Verarbeitung alle {self.process_every_n_frames} Frames")


if __name__ == "__main__":
    try:
        detector = EmotionDetector()
        detector.run()
    except Exception as e:
        print(f"Fehler beim Start der Emotion Detection: {str(e)}")
        GPIO.cleanup()