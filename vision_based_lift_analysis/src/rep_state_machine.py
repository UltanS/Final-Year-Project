"""
rep_state_machine.py

Implements a rep state machine for lift analysis

This class tracks the phases of a rep:
- searching for the lockout position
- descent
- pause / bottom position
- ascent
- rep completion
"""

# pylint: disable=too-few-public-methods, too-many-branches
class RepStateMachine:
    """
    Tracks repetition phases using vertical motion and lockout conditions

    The state machine can be reused for different lifts by using
    lift-specific threshold parameters
    """

    def __init__(self, state_parameters):
        """
        Parameters
        ----------
        state_parameters : dict
            Dictionary containing movement thresholds such as:
            - velocity_descend
            - velocity_ascend
            - velocity_still
            - minimum_descent
            - top_tolerance
        """
        self.state_parameters = state_parameters

        # Declare attributes so pylint knows they belong to the class
        self.current_state = None
        self.top_position_y = None
        self.bottom_position_y = None
        self.pause_frame_count = 0
        self.repetition_started = False
        self.rep_flags = set()

        self.reset()

    def reset(self):
        """
        Resets the state machine for the next repetition
        """

        # Current repetition phase
        self.current_state = "search_lockout"

        # Highest position reached at the top of the movement
        self.top_position_y = None

        # Lowest position reached during descent
        self.bottom_position_y = None

        # Number of frames spent in the pause / bottom state
        self.pause_frame_count = 0

        # Indicates whether enough descent occurred to count as a real rep
        self.repetition_started = False

        # Stores rule-related events detected during the rep
        self.rep_flags = set()

    def update(self, current_position_y, vertical_velocity, lockout_valid):
        """
        Updates the state machine using the current frame data.

        Parameters
        ----------
        current_position_y : int or float
            Current tracked vertical position
        vertical_velocity : int or float
            Change in vertical position between frames
        lockout_valid : bool
            Whether the current frame satisfies the lift lockout condition

        Returns
        -------
        str or None
            Returns "rep_complete" when a repetition has been completed
            Otherwise returns None
        """

        parameters = self.state_parameters

        # State 1: search for the top lockout position
        if self.current_state == "search_lockout":

            if lockout_valid:
                if self.top_position_y is None:
                    self.top_position_y = current_position_y
                else:
                    self.top_position_y = min(
                        self.top_position_y,
                        current_position_y
                    )

            # Transition into descent when lockout is valid
            # and the tracked point begins to move downward
            if (
                lockout_valid
                and vertical_velocity > parameters["velocity_descend"]
            ):
                self.current_state = "descent"
                self.bottom_position_y = current_position_y

        # State 2: descent phase
        elif self.current_state == "descent":

            self.bottom_position_y = max(
                self.bottom_position_y,
                current_position_y
            )

            # Mark the repetition as started only if meaningful
            # downward motion has occurred
            if (
                self.bottom_position_y - self.top_position_y
                >= parameters["minimum_descent"]
            ):
                self.repetition_started = True

            # If movement becomes nearly still, treat this as the
            # bottom / pause position
            if abs(vertical_velocity) <= parameters["velocity_still"]:
                self.current_state = "pause"
                self.pause_frame_count = 1

            # If upward motion begins, transition into ascent
            if vertical_velocity < parameters["velocity_ascend"]:
                self.current_state = "ascent"

        # State 3: pause / bottom position
        elif self.current_state == "pause":

            self.pause_frame_count += 1

            if vertical_velocity < parameters["velocity_ascend"]:
                self.current_state = "ascent"

        # State 4: ascent phase
        elif self.current_state == "ascent":

            # Detect downward movement during ascent
            if vertical_velocity > parameters["velocity_descend"]:
                self.rep_flags.add("downward_on_ascent")

            # Repetition is complete when:
            # - a real rep had started
            # - lockout is valid again
            # - the tracked point has returned close to the top position
            if (
                self.repetition_started
                and lockout_valid
                and current_position_y
                <= self.top_position_y + parameters["top_tolerance"]
            ):
                return "rep_complete"

        return None
