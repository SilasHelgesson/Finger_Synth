from pathlib import Path
import cv2
import math
import numpy as np
import urllib.request
import os
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision
import yaml

BASE_DIR = Path(__file__).resolve().parents[2]  # src/hand_tracking/ -> src/ -> FINGER_SYNTH/

general_config_path = BASE_DIR / "config" / "general_config.yaml"
with open(general_config_path, "r") as file:
    general_config = yaml.safe_load(file)

def ensure_model():
    if not os.path.exists(general_config["model"]["path"]):
        print("Downloading hand landmarker model (~9 MB)…")
        urllib.request.urlretrieve(general_config["model"]["url"], general_config["model"]["path"])
        print("Done.")

def vec(a, b):
    return np.array([b.x - a.x, b.y - a.y, b.z - a.z])


def angle_between(v1, v2):
    cos_a = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-8)
    return math.degrees(math.acos(max(-1.0, min(1.0, cos_a))))


def finger_curl_pct(landmarks, joint_ids):
    angles = []
    for i in range(len(joint_ids) - 2):
        a = landmarks[joint_ids[i]]
        b = landmarks[joint_ids[i + 1]]
        c = landmarks[joint_ids[i + 2]]
        angles.append(angle_between(vec(b, a), vec(b, c)))
    avg = sum(angles) / len(angles)
    return max(0.0, min(100.0, (avg - general_config["curl"]["min"]) / (general_config["curl"]["max"] - general_config["curl"]["min"]) * 100.0))


def all_curls(landmarks):
    return {name: finger_curl_pct(landmarks, joints)
            for name, joints in general_config["finger_joints"].items()}


def smooth(prev, new_vals, alpha):
    if not prev:
        return dict(new_vals)
    return {k: alpha * new_vals[k] + (1 - alpha) * prev.get(k, new_vals[k])
            for k in new_vals}

def draw_skeleton(frame, lms, w, h):
    pts = [(int(lm.x * w), int(lm.y * h)) for lm in lms]
    for a, b in general_config["hand_connections"]:
        cv2.line(frame, pts[a], pts[b], (160, 160, 160), 1, cv2.LINE_AA)
    for i, pt in enumerate(pts):
        tip = i in {4, 8, 12, 16, 20}
        cv2.circle(frame, pt, 5 if tip else 3,
                   (0, 200, 255) if tip else (100, 100, 100), -1, cv2.LINE_AA)


def draw_hud(frame, hand_states, audio_config):
    y = 20
    for label, curls, vol in hand_states:
        hcol = general_config["hand_colours"].get(label, (200, 200, 200))
        cv2.putText(frame, f"{label}  vol:{vol*100:.0f}%",
                    (10, y), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, hcol, 1, cv2.LINE_AA)
        y += 20
        for finger, pct in curls.items():
            if finger == "Thumb":
                continue
            semitone = audio_config["note_semitones"].get(label, {}).get(finger)
            note     = audio_config["note_names"][semitone]
            on       = pct >= audio_config["extend_thresh"]
            col      = general_config["finger_colours"][finger] if on else (70, 70, 70)
            bar_w    = int(pct * 1.2)
            cv2.rectangle(frame, (10, y), (10 + bar_w, y + 12), col, -1)
            cv2.putText(frame, f"{finger[0]} {note} {'playing' if on else ''}",
                        (160, y + 11),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.38, col, 1, cv2.LINE_AA)
            y += 16
        y += 8

class HandTrackingHandler:
    def __init__(self):
        ensure_model()

        base_opts = mp_python.BaseOptions(model_asset_path=general_config["model"]["path"])
        options   = mp_vision.HandLandmarkerOptions(
            base_options=base_opts,
            running_mode=mp_vision.RunningMode.VIDEO,
            num_hands=2,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self.landmarker      = mp_vision.HandLandmarker.create_from_options(options)
        self.smoothed_curls  = {}
        self.smoothed_vols   = {}
        self.timestamp_ms    = 0
        self._last_landmarks = []

    def process_frame(self, frame, audio_config):
        h, w = frame.shape[:2]

        rgb      = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        self.timestamp_ms += 33
        result = self.landmarker.detect_for_video(mp_image, self.timestamp_ms)

        self._last_landmarks = result.hand_landmarks if result.hand_landmarks else []

        active_labels = set()
        hand_states   = []

        if result.hand_landmarks:
            for i, lms in enumerate(result.hand_landmarks):
                label = (result.handedness[i][0].display_name
                         if result.handedness else f"Hand{i}")
                active_labels.add(label)

                raw_curls = all_curls(lms)
                self.smoothed_curls[label] = smooth(
                    self.smoothed_curls.get(label), raw_curls, audio_config["smoothing"])

                thumb_pct = self.smoothed_curls[label].get("Thumb", 0.0)
                raw_vol   = max(0.0, min(1.0, thumb_pct / 100.0))
                vol       = (audio_config["volume_smooth"] * raw_vol
                             + (1 - audio_config["volume_smooth"]) * self.smoothed_vols.get(label, 0.0))
                self.smoothed_vols[label] = vol

                hand_states.append((label, self.smoothed_curls[label], vol))

        return hand_states, active_labels

    def draw(self, frame, lms_list, show_skeleton):
        """Draw skeleton overlays for all detected hands onto frame in-place."""
        if not show_skeleton or not lms_list:
            return
        h, w = frame.shape[:2]
        for lms in lms_list:
            draw_skeleton(frame, lms, w, h)

    def close(self):
        self.landmarker.close()