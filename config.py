CAMERA_CONFIG = {
    'DEVICE': 0,                # Kamera Device ID
    'FPS': 15,                  # Frames per Second
}

RELAY_CONFIG = {
    'HAPPY_PIN': 17,            # GPIO Pin für "Happy" Relais
    'NOT_HAPPY_PIN': 18,        # GPIO Pin für "Not Happy" Relais
    'ACTIVE_LOW': True,         # True wenn Relais low-aktiv sind
    'RELAY_DURATION': 4.0       # Aktvierungsdauer (Sekunden)
}

EMOTION_DETECTION_CONFIG = {
    'MAX_FACES': 1,             # Anzahl der Gesichter die erkannt werden
    'IS_HAPPY': 0.05,           # Is Happy Threshold
    'IS_NOT_HAPPY': 0.01        # Is Not Happy Threshold    
}

DEBUG_CONFIG = {
    'LOG_LEVEL': 'DEBUG',         # Debug Level: DEBUG, INFO, WARNING, ERROR
    'SHOW_DETECTION_BOXES': True, # Erkennungsboxen anzeigen
    'SHOW_FACE_MESHES': False     # Face Mesh anzeigen
}
