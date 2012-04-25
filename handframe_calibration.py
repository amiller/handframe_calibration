import numpy as np
import cv


def handframe_calibration(obj_points, finger_points, eye_point):
    """
    obj_points:
        Known locations of the targets that the user places his fingers over
        (world coordinates) shape=(Nx3), dtype=np.float32, N >= 3
    finger_points:
        3D (metric) points corresponding to the user's finger tips, relative
        to the camera's reference frame
        shape=(Nx3), dtype=np.float32, same N as obj_points
    eye_point:
        The 3D point of the user's eye, relative to the camera's frame
    """
    assert obj_points.shape[1] == finger_points.shape[1] == 3
    assert obj_points.shape[0] >= 4
    assert obj_points.shape[0] == finger_points.shape[0]

    KK = np.eye(3, dtype='f')

    # Correct for the eye position and divide the homogeneous coordinates
    img_points = finger_points - eye_point
    img_points = img_points[:,:2] / img_points[:,2:]

    # Use OpenCV's extrinsic calibration routine
    img_p = cv.fromarray(img_points)
    obj_p = cv.fromarray(obj_points)
    dc = cv.fromarray(np.zeros((4,1),'f'))
    rvec = cv.fromarray(np.zeros((3,1),'f'))
    rmat = cv.fromarray(np.zeros((3,3),'f'))
    tvec = cv.fromarray(np.zeros((3,1),'f'))
    cv.FindExtrinsicCameraParams2(obj_p, img_p, cv.fromarray(KK),
                                  dc, rvec, tvec)
    cv.Rodrigues2(rvec,rmat)
    RT = np.eye(4,dtype='f')
    RT[:3,:3] = rmat
    RT[:3,3] = np.array(tvec).flatten()

    # Try reprojecting the points
    reproj_p = cv.fromarray(img_points.copy())
    cv.ProjectPoints2(obj_p, rvec, tvec, cv.fromarray(KK), dc, reproj_p)
    reproj = np.array(reproj_p)
    within_epsilon = lambda a, b: np.all(np.abs(a-b) < 1e-3)
    #assert within_epsilon(reproj, img_points)

    # This is the place where we correct for opencv's different opinion
    # of how a camera matrix is oriented.
    #RT = np.dot(np.linalg.inv(RT), np.diag([1,-1,-1,1]))
    RT[:3,3] += eye_point
    RT = np.linalg.inv(RT)
    return RT
