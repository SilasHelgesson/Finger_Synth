from pathlib import Path
import cv2
import sys

SRC_DIR = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(SRC_DIR / "audio"))
sys.path.insert(0, str(SRC_DIR / "hand_tracking"))

from audio_handler         import AudioEngine, audio_config
from hand_tracking_handler import HandTrackingHandler, draw_hud, general_config

def main():
    engine  = AudioEngine()
    tracker = HandTrackingHandler()
    print("Audio engine started.")
    print("Extend fingers to play notes. Thumb = volume.")
    print("Left = C3 D3 E3 G3 | Right = C4 D4 E4 G4")
    print("Q: quit  L: toggle skeleton")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Cannot open webcam.")

    cv2.namedWindow("Finger Synth", cv2.WINDOW_NORMAL)
    cv2.moveWindow("Finger Synth", 0, 50)

    show_skeleton = True

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        frame = cv2.flip(frame, 1)
        h, w  = frame.shape[:2]

        hand_states, active_labels = tracker.process_frame(frame, audio_config)

        tracker.draw(frame, tracker._last_landmarks, show_skeleton)

        for label, curls, vol in hand_states:
            for finger, pct in curls.items():
                if finger == "Thumb":
                    continue
                engine.set_note(label, finger, pct >= audio_config["extend_thresh"], vol)

        for label in list(tracker.smoothed_curls.keys()):
            if label not in active_labels:
                for finger in general_config["finger_joints"]:
                    if finger != "Thumb":
                        engine.set_note(label, finger, False, 0.0)

        draw_hud(frame, hand_states, audio_config)

        cv2.putText(frame, "Q: quit  |  L: skeleton",
                    (10, h - 12), cv2.FONT_HERSHEY_SIMPLEX,
                    0.4, (140, 140, 140), 1, cv2.LINE_AA)

        cv2.imshow("Finger Synth", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        elif key == ord("l"):
            show_skeleton = not show_skeleton

    engine.stop()
    tracker.close()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()