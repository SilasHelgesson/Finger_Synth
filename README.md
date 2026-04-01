# README

**English version below** 🇺🇸

---

## Deutsch 🇩🇪

### Projektbeschreibung

Dieses Projekt ist ein **Finger-basierter Synthesizer**, der mithilfe von **Computer Vision (MediaPipe)** Hand- und Fingerbewegungen in Echtzeit erkennt und in Musik umwandelt.

Jeder Finger ist einer bestimmten Note zugeordnet. Die **Krümmung (Curl)** eines Fingers bestimmt die Lautstärke des gespielten Tons, während der **Daumen die Gesamtlautstärke einer Hand kontrolliert**. Dadurch entsteht ein intuitives, berührungsloses Musikinstrument.

---

### Konfiguration

Die gesamte Logik für:
- Finger-zu-Noten-Zuordnung  
- Lautstärkesteuerung  
- Glättung und Schwellenwerte  
- Audio-Parameter  

befindet sich im Ordner:

```bash
config/
```

Dort können alle Parameter flexibel angepasst werden.

---

### Funktionsweise

1. Kamera erfasst die Hände  
2. MediaPipe erkennt 21 Hand-Landmarks  
3. Finger werden anhand ihrer Gelenke analysiert  
4. Die Krümmung eines Fingers bestimmt die Lautstärke eines Tons  
5. Der Daumen steuert die Gesamtlautstärke der jeweiligen Hand  
6. Eine Audio-Engine erzeugt den Klang in Echtzeit  

---

### Voraussetzungen

- Python 3.x  
- Webcam  
- Abhängigkeiten aus `requirements.txt`  

```bash
pip install -r requirements.txt
```

---

### Installation und Ausführung

1. Repository klonen:

```bash
git clone https://github.com/SilasHelgesson/Finger_Synth
cd Finger_Synth
```

2. Abhängigkeiten installieren:

```bash
pip install -r requirements.txt
```

3. Anwendung starten:

```bash
python src/apps/desktop.py
```

---

### Projektstruktur

```bash
Finger_Synth/
│── config/              # Konfigurationsdateien
│── src/
│   ├── apps/
│   │   └── desktop.py   # Haupteinstiegspunkt
│   ├── audio/           # Audio-Engine
│   └── hand_tracking/   # Handerkennung & Tracking
│
│── README.md
```

---

### Demo Video

[![Watch the video](https://img.youtube.com/vi/riYetWe_TzA/0.jpg)](https://www.youtube.com/watch?v=riYetWe_TzA)

---

## English 🇺🇸

### Project Description

This project is a **finger-controlled synthesizer** using **computer vision (MediaPipe)** to track hands and generate sound in real time.

Each finger is mapped to a musical note. The **finger curl controls the volume of the note**, while the **thumb controls the overall volume of each hand**.

---

### Configuration

All configuration related to:
- Finger-to-note mapping  
- Volume control  
- Smoothing and thresholds  
- Audio parameters  

is located in:

```bash
config/
```

All behavior can be adjusted there.

---

### How It Works

1. Camera captures the hands  
2. MediaPipe detects 21 hand landmarks  
3. Finger joints are analyzed  
4. Finger curl determines note volume  
5. Thumb controls overall hand volume  
6. Audio engine generates sound in real time  

---

### Prerequisites

- Python 3.x  
- Webcam  
- Dependencies listed in `requirements.txt`  

```bash
pip install -r requirements.txt
```

---

### Installation and Execution

1. Clone the repository:

```bash
git clone https://github.com/SilasHelgesson/Finger_Synth
cd Finger_Synth
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
python src/apps/desktop.py
```

---

### Project Structure

```bash
Finger_Synth/
│── config/
│── src/
│   ├── apps/
│   │   └── desktop.py
│   ├── audio/
│   └── hand_tracking/
│── README.md
```

---

### Video

[![Watch the video](https://img.youtube.com/vi/riYetWe_TzA/0.jpg)](https://www.youtube.com/watch?v=riYetWe_TzA)
