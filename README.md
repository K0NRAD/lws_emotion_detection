
# Raspberry Pi Emotion Detection mit Relais-Steuerung

Ein Python-basiertes System zur Emotionserkennung in Echtzeit mit automatischer Relais-Steuerung. Das System erkennt Gesichtsausdrücke und steuert basierend auf der erkannten Emotion (lächelnd/nicht lächelnd) zwei separate Relais an.

## 🎯 Features

- Echtzeit-Gesichtserkennung
- Emotionserkennung (Fokus auf Lächeln)
- Adaptive Framerate für optimale Performance
- Dual-Relais-Steuerung (je 2 Sekunden Aktivierung)
- Performance-Optimierung für Raspberry Pi 3+
- Konfigurierbares Debug-Interface
- Automatischer Systemstart als Service

## 🔧 Hardware-Anforderungen

- Raspberry Pi 3+ (oder besser)
- USB-Webcam
- 2x Relais-Module (5V)
- Jumper-Kabel
- Optional: Gehäuse

## 📋 Pin-Belegung

| Component      | GPIO Pin | Beschreibung        |
|---------------|----------|---------------------|
| Happy Relay   | GPIO 17  | Aktiv bei Lächeln   |
| Not Happy Relay| GPIO 18  | Aktiv bei nicht Lächeln |

## 🛠 Installation

1. **Repository klonen:**
```bash
git clone https://github.com/username/raspberry-emotion-detection.git
cd raspberry-emotion-detection
```

2. **Automatische Installation ausführen:**
```bash
chmod +x install_requirements.sh
./install_requirements.sh
```

3. **Service aktivieren:**
```bash
sudo systemctl start emotion-detection.service
sudo systemctl enable emotion-detection.service
```

## ⚙️ Konfiguration

Die Konfiguration erfolgt über die `config.py`:

```python
# Beispiel-Konfiguration
RELAY_CONFIG = {
    'HAPPY_PIN': 17,
    'NOT_HAPPY_PIN': 18,
    'ACTIVE_LOW': True,
    'RELAY_DURATION': 2.0
}

CAMERA_CONFIG = {
    'WIDTH': 320,
    'HEIGHT': 240,
    'FPS': 10,
    'DEVICE': 0
}
```

## 🚀 Verwendung

### Manuelle Ausführung:
```bash
source emotion_env/bin/activate
python3 emotion_detector.py
```

### Service-Verwaltung:
```bash
# Status prüfen
sudo systemctl status emotion-detection.service

# Logs anzeigen
sudo journalctl -u emotion-detection.service -f

# Service neustarten
sudo systemctl restart emotion-detection.service
```

## 📊 Performance

Das System verwendet eine adaptive Framerate-Anpassung:
- Automatische Anpassung der Verarbeitungsrate
- Optimierung für Raspberry Pi 3+
- Typische Performance: 5-10 FPS bei Emotionserkennung

## 🔍 Debug-Modus

Der Debug-Modus kann in der `config.py` aktiviert werden:
```python
DEBUG_CONFIG = {
    'SHOW_FPS': True,
    'SHOW_DETECTION_BOXES': True,
    'LOG_LEVEL': 'DEBUG'
}
```

## 📦 Projektstruktur

```
emotion_detection/
├── emotion_detector.py    # Hauptprogramm
├── config.py             # Konfigurationsdatei
├── install_requirements.sh # Installations-Script
├── requirements.txt      # Python-Abhängigkeiten
└── emotion_env/         # Virtuelle Umgebung
```

## 🔄 Updates

Updates können über Git eingespielt werden:
```bash
git pull
sudo systemctl restart emotion-detection.service
```

## 📝 Logging

Logs werden über systemd verwaltet:
```bash
# Alle Logs anzeigen
sudo journalctl -u emotion-detection.service

# Letzte 100 Zeilen
sudo journalctl -u emotion-detection.service -n 100

# Logs folgen
sudo journalctl -u emotion-detection.service -f
```

## 🔒 Sicherheit

- GPIO-Pins sind durch Pull-down-Widerstände geschützt
- Service läuft mit eingeschränkten Rechten
- Automatische Relais-Deaktivierung nach Timeout

## 📈 Performance-Optimierung

Das System verwendet mehrere Optimierungstechniken:
1. Adaptive Framerate-Anpassung
2. Bildverkleinerung für Analyse
3. Frame-Skipping bei hoher Last
4. Caching von Erkennungsergebnissen

## 📄 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert - siehe [LICENSE](LICENSE) Datei.

## 🙏 Danksagungen

- OpenCV Team
- MediaPipe Team
- FER (Facial Expression Recognition) Entwickler
- Raspberry Pi Foundation

## 📧 Kontakt

Bei Fragen oder Problemen:
- Issue auf GitHub erstellen
- E-Mail: hauke.konrad.coding@gmail.com
