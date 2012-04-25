Find the extrinsic calibration (camera pose) of a kinect, using a "hand framing" 
gesture. The user should close one eye and hold out their thumbs and forefingers
so that they line up with (cover up) four points with known world coordinates,
(e.g., the four corners of a TV screen). The 3D positions of the four finger tips
and the user's eye (i.e., the user's nose) are found, relative to the camera.
From these five points (four rays), the camera pose can be estimated.

So far this code just provides the geometry, finding the nose and finger tips in 
a kinect depth image is assumed to be handled externally.

<img src="http://i.imgur.com/66kbN.png"/>

Legend:
-  Yellow: User's eye
-  Cyan: User's finger tips
-  Purple: Target points with known coordinates
-  Thin coordinate axes: actual camera pose
-  Thick coordinate axes: estimated camera pose

Requirements:

- github.com/amiller/wxpy3d
- OpenCV 2.1+ or so

Usage:

    $ ipython --pylab=wx
    In [1]: run -i demo_handframe_calibration.py

    # Press 'R' to re-randomize the eye and camera positions
    # Use the mouse to control the 