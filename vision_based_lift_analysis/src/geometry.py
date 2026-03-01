'''
    Geometry.py is used for joint angle calculation in
    this vision based lift analysis system.
'''
import numpy as np

def calculate_angle(point_a, vertex_point, point_c):
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
    # convert input coordinates to numpy arrays
    first_point = np.array(point_a)
    joint_vertex = np.array(vertex_point)
    third_point = np.array(point_c)

    # create vectors from the vertex to the other two points
    vector_1 = first_point - joint_vertex
    vector_2 = third_point - joint_vertex

    # compute the cosine of the angle using the dot product formula:
    # cos(theta) = (v1 . v2) / (||v1|| * ||v2||)
    cosine_angle = np.dot(vector_1, vector_2) / (
        np.linalg.norm(vector_1)
        * np.linalg.norm(vector_2)
        + 1e-7)

    # clip to prevent floating point precision errors
    cosine_angle = np.clip(cosine_angle, -1.0, 1.0)

    # convert from radians to degrees
    angle_degrees = np.degrees(np.arccos(cosine_angle))

    return angle_degrees
