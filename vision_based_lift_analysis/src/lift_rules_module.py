"""
lift_rules_module.py

Defines lift-specific parameters for movement detection
and judging rules in lift analysis

Each lift returns a dictionary containing:
- motion thresholds
- lockout conditions
- judging rule thresholds
"""

def bench_parameters():
    """
    Parameters for bench press detection and judging
    """

    return {
        # Motion thresholds
        "velocity_ascend": -2,
        "velocity_descend": 2,
        "velocity_still": 1,
        "minimum_descent": 15,
        "top_tolerance": 20,

        # Judging rules
        "minimum_pause_frames": 3,   # must pause on chest
        "lockout_angle": 145,        # elbow angle for lockout

        # Rule flags (optional toggles)
        "require_pause": True,
        "check_downward_motion": True
    }

def squat_parameters():
    """
    Parameters for squat detection and judging
    """

    return {
        # Motion thresholds
        "velocity_ascend": -2,
        "velocity_descend": 2,
        "velocity_still": 1,
        "minimum_descent": 20,
        "top_tolerance": 25,

        # Judging rules
        "lockout_hip_angle": 165,
        "lockout_knee_angle": 165,

        # Depth rule (basic version)
        "require_depth": True,

        # Rule flags
        "check_downward_motion": True
    }

def deadlift_parameters():
    """
    Parameters for deadlift detection
    """

    return {
        "velocity_ascend": -2,
        "velocity_descend": 2,
        "velocity_still": 1,
        "minimum_descent": 10,
        "top_tolerance": 30,
        "lockout_hip_angle": 170,
        "lockout_knee_angle": 170
    }
