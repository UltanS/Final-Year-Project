"""
main.py

Runs the vision based lift analysis application with a simple GUI

The GUI allows the user to:
- select the lift type
- select the visible body side
- choose a video file

The analysis pipeline then:
- loads the selected video
- runs MediaPipe pose estimation
- tracks vertical motion
- detects repetition phases
- checks if it is a valid lift
- visualises the lift analysis
"""

# pylint: disable=no-member, too-many-locals, too-many-branches, too-many-statements
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

import cv2
import mediapipe as mp

from motion_tracker import MotionTracker
from rep_state_machine import RepStateMachine
from lift_rules_module import (
    bench_parameters,
    squat_parameters,
    deadlift_parameters
)
from geometry import calculate_angle

def draw_judgement(frame, result, reasons):
    """
    Draws GOOD LIFT or BAD LIFT feedback on the frame.

    Parameters
    ----------
    frame : numpy.ndarray
        Current video frame.
    result : str
        Either "good" or "bad".
    reasons : list[str]
        List of failure reasons if the lift is bad.
    """


    frame_height, frame_width, _ = frame.shape

    if result == "good":
        cv2.putText(
            frame,
            "GOOD LIFT",
            (frame_width // 4, 120),
            cv2.FONT_HERSHEY_SIMPLEX,
            2,
            (0, 255, 0),
            5
        )
    elif result == "bad":
        cv2.putText(
            frame,
            "BAD LIFT",
            (frame_width // 3, 120),
            cv2.FONT_HERSHEY_SIMPLEX,
            2,
            (0, 0, 255),
            5
        )

        text_y = 180
        for reason in reasons:
            cv2.putText(
                frame,
                reason,
                (50, text_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                3
            )
            text_y += 40

def run_lift_analysis(video_path, lift_type, lift_side):
    """
    Runs the lift analysis pipeline on the selected video.

    Parameters
    ----------
    video_path : str
        Path to the selected video file
    lift_type : str
        Type of lift being analysed: bench, squat, or deadlift
    lift_side : str
        Visible body side in the video: left or right
    """

    # mediapipe setup
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles

    pose = mp_pose.Pose(model_complexity=2, smooth_landmarks=True)

    # landmark index selecttion
    if lift_side == "left":
        shoulder_index = 11
        elbow_index = 13
        wrist_index = 15
        hip_index = 23
        knee_index = 25
        ankle_index = 27
    else:
        shoulder_index = 12
        elbow_index = 14
        wrist_index = 16
        hip_index = 24
        knee_index = 26
        ankle_index = 28

    # lift specific parameters
    if lift_type == "bench":
        lift_parameters = bench_parameters()
    elif lift_type == "squat":
        lift_parameters = squat_parameters()
    elif lift_type == "deadlift":
        lift_parameters = deadlift_parameters()
    else:
        raise ValueError("Lift type must be 'bench', 'squat', or 'deadlift'")

    # initialise analysis components
    motion_tracker = MotionTracker()
    rep_state_machine = RepStateMachine(lift_parameters)

    rep_count = 0

    # video setup
    video_capture = cv2.VideoCapture(video_path)

    if not video_capture.isOpened():
        messagebox.showerror("Video Error", "Could not open the selected video")
        return

    frames_per_second = video_capture.get(cv2.CAP_PROP_FPS)
    frame_delay = int(1000 / frames_per_second) if frames_per_second > 0 else 1

    # main analysis loop
    while True:
        frame_available, frame = video_capture.read()

        if not frame_available:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pose_results = pose.process(rgb_frame)

        if not pose_results.pose_landmarks:
            cv2.imshow("Lift Detection", frame)
            if cv2.waitKey(frame_delay) & 0xFF == 27:
                break
            continue

        frame_height, frame_width, _ = frame.shape
        landmarks = pose_results.pose_landmarks.landmark

        #extract body landmark coordinates
        shoulder = (
            landmarks[shoulder_index].x * frame_width,
            landmarks[shoulder_index].y * frame_height
        )
        elbow = (
            landmarks[elbow_index].x * frame_width,
            landmarks[elbow_index].y * frame_height
        )
        wrist = (
            landmarks[wrist_index].x * frame_width,
            landmarks[wrist_index].y * frame_height
        )
        hip = (
            landmarks[hip_index].x * frame_width,
            landmarks[hip_index].y * frame_height
        )
        knee = (
            landmarks[knee_index].x * frame_width,
            landmarks[knee_index].y * frame_height
        )
        ankle = (
            landmarks[ankle_index].x * frame_width,
            landmarks[ankle_index].y * frame_height
        )

        # select tracking landmark and check for lockout
        if lift_type == "bench":
            tracked_vertical_position = int(wrist[1])
            elbow_angle = calculate_angle(shoulder, elbow, wrist)
            lockout_valid = elbow_angle >= lift_parameters["lockout_angle"]
            primary_tracking_point = wrist
        else:
            tracked_vertical_position = int(hip[1])

            hip_angle = calculate_angle(shoulder, hip, knee)
            knee_angle = calculate_angle(hip, knee, ankle)

            lockout_valid = (
                hip_angle >= lift_parameters["lockout_hip_angle"]
                and knee_angle >= lift_parameters["lockout_knee_angle"]
            )
            primary_tracking_point = hip

        # update analysis state
        smoothed_vertical_position, vertical_velocity = motion_tracker.update(
            tracked_vertical_position
        )

        rep_event = rep_state_machine.update(
            smoothed_vertical_position,
            vertical_velocity,
            lockout_valid
        )

        if rep_event == "rep_complete":
            rep_count += 1
            print(f"Rep {rep_count} complete")
            rep_state_machine.reset()

        # draw visual overlay
        mp_drawing.draw_landmarks(
            frame,
            pose_results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=(
                mp_drawing_styles.get_default_pose_landmarks_style()
            ),
            connection_drawing_spec=mp_drawing.DrawingSpec(
                thickness=2,
                circle_radius=2
            )
        )

        tracked_joint_points = [shoulder, elbow, wrist, hip, knee, ankle]
        for joint_point in tracked_joint_points:
            cv2.circle(
                frame,
                (int(joint_point[0]), int(joint_point[1])),
                6,
                (0, 255, 255),
                -1
            )

        cv2.circle(
            frame,
            (int(primary_tracking_point[0]), int(primary_tracking_point[1])),
            10,
            (0, 0, 255),
            -1
        )

        cv2.putText(
            frame,
            f"Lift: {lift_type}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            f"Reps: {rep_count}",
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )

        cv2.imshow("Lift Detection", frame)

        if cv2.waitKey(frame_delay) & 0xFF == 27:
            break

    video_capture.release()
    cv2.destroyAllWindows()


class LiftAnalysisGUI:
    """
    Simple graphical interface for selecting lift type,
    visible side, and input video
    """

    def __init__(self, root_window):
        self.root_window = root_window
        self.root_window.title("Vision-Based Lift Analysis")
        self.root_window.geometry("520x300")
        self.root_window.resizable(False, False)

        self.selected_video_path = ""

        self.lift_type_var = tk.StringVar(value="bench")
        self.lift_side_var = tk.StringVar(value="left")

        self.build_interface()

    def build_interface(self):
        """
        Builds the GUI layout.
        """

        title_label = tk.Label(
            self.root_window,
            text="Vision-Based Lift Analysis",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=15)

        lift_type_label = tk.Label(self.root_window, text="Select Lift Type:")
        lift_type_label.pack()

        lift_type_dropdown = ttk.Combobox(
            self.root_window,
            textvariable=self.lift_type_var,
            values=["bench", "squat", "deadlift"],
            state="readonly",
            width=20
        )
        lift_type_dropdown.pack(pady=5)

        lift_side_label = tk.Label(
            self.root_window,
            text="Select Visible Body Side:"
        )
        lift_side_label.pack()

        lift_side_dropdown = ttk.Combobox(
            self.root_window,
            textvariable=self.lift_side_var,
            values=["left", "right"],
            state="readonly",
            width=20
        )
        lift_side_dropdown.pack(pady=5)

        choose_file_button = tk.Button(
            self.root_window,
            text="Choose Video File",
            command=self.choose_video_file,
            width=20
        )
        choose_file_button.pack(pady=15)

        self.file_label = tk.Label(
            self.root_window,
            text="No file selected",
            wraplength=450,
            justify="center"
        )
        self.file_label.pack(pady=5)

        start_button = tk.Button(
            self.root_window,
            text="Start Analysis",
            command=self.start_analysis,
            width=20,
            bg="lightgreen"
        )
        start_button.pack(pady=20)

    def choose_video_file(self):
        """
        Opens a file picker for selecting a video file
        """

        selected_file = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mov *.mkv"),
                ("All files", "*.*")
            ]
        )

        if selected_file:
            self.selected_video_path = selected_file
            self.file_label.config(text=selected_file)

    def start_analysis(self):
        """
        Validates user input and launches the lift analysis
        """

        if not self.selected_video_path:
            messagebox.showerror(
                "Missing Video",
                "Please choose a video file before starting analysis."
            )
            return

        selected_lift_type = self.lift_type_var.get()
        selected_lift_side = self.lift_side_var.get()

        self.root_window.destroy()

        run_lift_analysis(
            self.selected_video_path,
            selected_lift_type,
            selected_lift_side
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = LiftAnalysisGUI(root)
    root.mainloop()
