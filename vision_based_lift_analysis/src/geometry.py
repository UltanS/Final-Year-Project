import numpy as np
'''
    Function: calculate_angle(point_a, vertex_point, point_c
    Description:
        This function calculates the angle formed at the vertex
        point between two connected line segments:
        point_a -> vertex_point -> point_c

        This is used to measure joint angles such as:
            Elbow angle - shoulder -> elbow -> wrist
            Knee angle - hip -> knee -> ankle
            Hip angle - shoulder -> hip -> knee

        Parameters
        point_a: tuple(float, float)
            First point of the line
        vertex_point: tuple(float, float)
            Central point of the line where the angle is measured
        point_c: tuple(float, float)
            Third point of the line

        Returns a float, the angle at the vertex point
'''
def calculate_angle(point_a, vertex_point, point_c):
    # convert input coordinates to numpy arrays
    first_point = np.array(point_a)
    joint_vertex = np.array(vertex_point)
    third_point = np.array(point_c)
    
    return angle_degrees
