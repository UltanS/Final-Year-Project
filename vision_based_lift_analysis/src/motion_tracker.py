'''
    motion_tracker.py provides vertical motion tracking
    for rep phase detection in lift analysis
'''
# pylint: disable=too-few-public-methods
class MotionTracker:
    '''
        class: Motion_tracker
        description:
            tracks vertical movement of a landmark and computes:
                smoothed vertical position
                frame to frame vertical velocity
            this is used to detect:
                descent phase
                ascent phase
                pause detection
    '''
    def __init__(self, smoothing_factor=0.8):
        '''
            parameters:
                smoothing factor:
                the higher the value results in a smoother but slower
                response
        '''

        # smoothing weight
        self.smoothing_weight = smoothing_factor

        # previous vertical position
        self.previous_position_y = None

        # current smoothed vertical position
        self.current_smoothed_y = None

    def update(self, current_raw_y):
        '''
            updates the smoothed vertical position and calculates velocity

            parameters:
                current_raw_y : int or float
                    current raw vertical coordinate from pose detection
                    
            returns
                tuple (smoothed_position_y, vertical_velocity)
                    smoothed_position_y : int
                        filtered vertical coordinate
                    vertical_velocity : int
                        change in vertical position between frames
                        positive = moving downward
                        negative = moving upward
        '''

        # apply smoothing
        # smoothed = alpha * previous_smoothed + (1 - alpha) * current_raw
        if self.current_smoothed_y is None:
            self.current_smoothed_y = current_raw_y
        else:
            self.current_smoothed_y = int(
                self.smoothing_weight * self.current_smoothed_y
                + (1 - self.smoothing_weight) * current_raw_y)

        # compute vertical velocity
        if self.previous_position_y is None:
            vertical_velocity = 0
        else:
            vertical_velocity = (
                self.current_smoothed_y - self.previous_position_y
            )

        # store current position for next frame comparison
        self.previous_position_y = self.current_smoothed_y

        return self.current_smoothed_y, vertical_velocity
