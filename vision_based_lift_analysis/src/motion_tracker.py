'''
    motion_tracker.py provides vertical motion tracking
    for rep phase detection in lift analysis
'''

class Motion_tracker:
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
