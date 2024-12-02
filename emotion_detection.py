import time
import os
import random

import numpy as np
import pygame

import RPi.GPIO as GPIO
import cv2

from cvzone.FaceMeshModule import FaceMeshDetector
from screeninfo import get_monitors

from config import *


class EmotionDetector:
    def __init__(self):

        # GPIO Setup
        self.RELAY_HAPPY = RELAY_CONFIG['HAPPY_PIN']
        self.RELAY_NOT_HAPPY = RELAY_CONFIG['NOT_HAPPY_PIN']
        self.RELAY_DURATION = RELAY_CONFIG['RELAY_DURATION']
        self.setup_gpio()

        # Display Setup
        self.screen_width = get_monitors()[0].width
        self.screen_height = get_monitors()[0].height
        cv2.namedWindow("emotions", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("emotions", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        # Camera Setup
        self.cap = cv2.VideoCapture(CAMERA_CONFIG['DEVICE'])
        if not self.cap.isOpened():
            raise ValueError("Failed to open camera")
        self.cap.set(cv2.CAP_PROP_FPS, CAMERA_CONFIG['FPS'])

        # Emotion Detection Setup
        self.detector = FaceMeshDetector(maxFaces=EMOTION_DETECTION_CONFIG['MAX_FACES'])
        self.LEFT_MOUTH_LANDMARK = 61
        self.RIGHT_MOUTH_LANDMARK = 291
        self.TOP_LIP_LANDMARK = 13
        self.BOTTOM_LIP_LANDMARK = 14
        self.FOREHEAD_LANDMARK = 10
        self.CHIN_LANDMARK = 152

        # Relais Status
        self.relay_timer = 0
        self.relay_active = False
        self.current_relay = None

        self.balloons = []
        for img_balloon_file in os.listdir("resources/balloon_popping_game/"):
            if img_balloon_file.startswith("balloon_"):
                image_balloon = pygame.image.load(f'resources/balloon_popping_game/{img_balloon_file}').convert_alpha()
                rect_balloon = image_balloon.get_rect()
                rect_balloon.x, rect_balloon.y = random.randint(80, 1200), 720 - random.randint(0, 150)
                speed = random.randint(5, 15)
                self.balloons.append({
                    'image': image_balloon,
                    'rect': rect_balloon,
                    'speed': speed,
                    'popped': False
                })


    def setup_gpio(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.RELAY_HAPPY, GPIO.OUT)
        GPIO.setup(self.RELAY_NOT_HAPPY, GPIO.OUT)
        GPIO.output(self.RELAY_HAPPY, GPIO.HIGH if RELAY_CONFIG['ACTIVE_LOW'] else GPIO.LOW)
        GPIO.output(self.RELAY_NOT_HAPPY, GPIO.HIGH if RELAY_CONFIG['ACTIVE_LOW'] else GPIO.LOW)

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
                    print("Activate Happy-Relais")
            else:
                GPIO.output(self.RELAY_NOT_HAPPY, relay_active_level)
                if DEBUG_CONFIG['LOG_LEVEL'] == 'DEBUG':
                    print("Activate Not-Happy-Relais")

            self.relay_timer = current_time
            self.relay_active = True
            self.current_relay = is_happy

        elif self.relay_active and (current_time - self.relay_timer >= self.RELAY_DURATION):
            GPIO.output(self.RELAY_HAPPY, relay_inactive_level)
            GPIO.output(self.RELAY_NOT_HAPPY, relay_inactive_level)
            self.relay_active = False
            if DEBUG_CONFIG['LOG_LEVEL'] == 'DEBUG':
                print("Deactivate Relais")

    def draw_halo(self, frame, face):
        print("----")    

    def run(self):
        print("Starte Emotion Detection... Drücke 'q' zum Beenden")
        try:
            while True:
                success, frame = self.cap.read()
                if not success:
                    break

                frame, faces = self.detector.findFaceMesh(frame, draw=DEBUG_CONFIG['SHOW_FACE_MESHES'])

                if faces:
                    for face in faces:
                        leftMouth = face[self.LEFT_MOUTH_LANDMARK]
                        rightMouth = face[self.RIGHT_MOUTH_LANDMARK]

                        topLip = face[self.TOP_LIP_LANDMARK]
                        bottomLip = face[self.BOTTOM_LIP_LANDMARK]

                        mouthOpenRatio = (bottomLip[1] - topLip[1]) / (rightMouth[0] - leftMouth[0])

                        is_happy = None
                        if mouthOpenRatio > EMOTION_DETECTION_CONFIG['IS_HAPPY']:
                            is_happy = True
                            self.control_relay(is_happy)
                            self.draw_halo(face, frame)	
                        if mouthOpenRatio < EMOTION_DETECTION_CONFIG['IS_NOT_HAPPY']:
                            is_happy = False
                            self.control_relay(is_happy)

                        if is_happy != None:
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
                            # Finde minimale/maximale x,y Koordinaten
                            x_coords = [p[0] for p in face]
                            y_coords = [p[1] for p in face]
                            
                            x_min, x_max = min(x_coords), max(x_coords)
                            y_min, y_max = min(y_coords), max(y_coords)
                            
                            # Rechteck zeichnen
                            cv2.rectangle(frame, (int(x_min-10), int(y_min-10)), 
                                                (int(x_max+10), int(y_max+10)), 
                                                (0,255,0), 2)


                else:
                    if self.relay_active:
                        GPIO.output(self.RELAY_HAPPY,
                                    GPIO.HIGH if RELAY_CONFIG['ACTIVE_LOW'] else GPIO.LOW)
                        GPIO.output(self.RELAY_NOT_HAPPY,
                                    GPIO.HIGH if RELAY_CONFIG['ACTIVE_LOW'] else GPIO.LOW)
                        self.relay_active = False

                # Relais-Timer überprüfen
                if self.relay_active:
                    self.control_relay(self.current_relay)

                frame = cv2.resize(frame, (self.screen_width, self.screen_height))
                cv2.imshow('emotions', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        except KeyboardInterrupt:
            print("\nProgramm durch Benutzer beendet")
        except Exception as e:
            print(f"Fehler während der Ausführung: {str(e)}")
        finally:
            self.cleanup()

    def cleanup(self):
        print("Cleanup...")
        self.cap.release()
        cv2.destroyAllWindows()
        GPIO.cleanup()
        print(f"Exit programm.")


if __name__ == "__main__":
    try:
        detector = EmotionDetector()
        detector.run()
    except Exception as e:
        print(f"Failed to start Emotion Detection: {str(e)}")
        GPIO.cleanup()
