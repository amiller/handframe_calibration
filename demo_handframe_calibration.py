from wxpy3d import PointWindow
from wxpy3d.opengl_state import opengl_state
from OpenGL.GL import *
from OpenGL.GLUT import *
import handframe_calibration; reload(handframe_calibration)
from handframe_calibration import handframe_calibration

if not 'window' in globals():
    window = PointWindow(title="Hand-framing Calibration", size=(500,500))
    glutInit()

#w, h = (0.2160, 0.2794)
w,h = (1.0, 1.0)
obj_points = np.array([[-w/2, h/2, 0], [w/2, h/2, 0],
                       [-w/2, 0,   0], [w/2, 0,   0],
                       [-w/2, 0, h/2], [w/2, 0, h/2]], 'f')

def make_camera():
    magnitude = lambda x: np.sqrt((x*x).sum())
    normalize = lambda x: x / magnitude(x)

    RT = np.eye(4, dtype='f')
    RT[:3,2] = normalize((np.random.rand(3)*2-1)*.2 + [0,0,-2])
    RT[:3,0] = normalize(np.cross((np.random.rand(3)*2-1), RT[:3,2]))
    RT[:3,1] = normalize(np.cross(RT[:3,2], RT[:3,0]))
    RT[:3,3] = (np.random.rand(3)*2-1)*.2 + [0,.5,-.5]
    return RT

def random_alpha(a,b):
    alpha = 0.5 #np.random.rand()
    return (alpha) * a + (1-alpha) * b

eye = (np.random.rand(3).astype('f')*2-1)*.2 + [0,0.5,1]
camera = make_camera()
def once():
    global eye, camera, finger_points, target_points, camera_est
    global finger_img, eye_img
    target_points = obj_points[(0,1,4,5),:]
    #target_points = obj_points[:,:]
    eye = (np.random.rand(3).astype('f')*2-1)*.2 + [0,0.8,1]
    camera = make_camera()
    finger_points = np.array([random_alpha(eye, p) 
                              for p in target_points], 'f')

    # Build finger points from the camera's point of view
    img = np.vstack((finger_points, [eye]))
    img = np.hstack((img, np.ones_like(img[:,:1])))
    img = np.dot(np.linalg.inv(camera), img.transpose()).transpose()
    img = img[:,:3] / img[:,3:]
    eye_img = img[-1,:]
    finger_img = img[:-1,:]
    finger_img += np.random.normal(scale=0.003, size=finger_img.shape)

    camera_est = handframe_calibration(target_points, finger_img, eye_img)
once()

@window.eventx
def EVT_KEY_DOWN(evt):
    c = evt.GetKeyCode()
    if c == ord('R'):
        once()
        window.Refresh()

def render_frustum(RT):
    assert RT.shape == (4,4)
    assert RT.dtype == np.float32
    with opengl_state():
        glMultMatrixf(RT.transpose())
        glScale(0.2, 0.2, 0.2)

        # Draw a little box, that's all
        glBegin(GL_LINES)
        glColor(1,0,0); glVertex(0,0,0); glVertex(1,0,0)
        glColor(0,1,0); glVertex(0,0,0); glVertex(0,1,0)
        glColor(0,0,1); glVertex(0,0,0); glVertex(0,0,1)
        glColor(1,1,1); glVertex(0,0,0); glVertex(0,0,-1)
        glEnd()

@window.event
def post_draw():
    glClearColor(0,0,0,1)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Draw a frame
    glBegin(GL_LINES)
    glColor(1,1,1)
    for i in (0,1, 2,3, 4,5,  0,2, 2,4,  1,3, 3,5):
        glVertex(*obj_points[i])
    glEnd()

    # Draw the target points and imaged finger points
    for p in target_points:
        with opengl_state():
            glTranslate(*p)
            glColor(1,0,1)
            glutSolidSphere(.01, 10, 10)
        glBegin(GL_LINES)
        glVertex(*eye); glVertex(*p)
        glEnd()

    for p in finger_img:
        with opengl_state():
            glMultMatrixf(camera.transpose())
            glTranslate(*p)
            glColor(0,1,1)
            glutSolidSphere(.01, 10, 10)

    # Draw the eye
    with opengl_state():
        glMultMatrixf(camera.transpose())
        glTranslate(*eye_img)
        glColor(1,1,0)
        glutSolidSphere(.02, 10, 10)


    # Draw coordinate axes
    with opengl_state():
        glScale(.05,.05,.05)
        glBegin(GL_LINES)
        glColor(1,0,0); glVertex(0,0,0); glVertex(1,0,0)
        glColor(0,1,0); glVertex(0,0,0); glVertex(0,1,0)
        glColor(0,0,1); glVertex(0,0,0); glVertex(0,0,1)
        glEnd()

    # Draw coordinate axes for the camera
    with opengl_state():
        glMultMatrixf(camera.transpose())
        glScale(0.2, 0.2, 0.2)
        glBegin(GL_LINES)
        glColor(1,0,0); glVertex(0,0,0); glVertex(1,0,0)
        glColor(0,1,0); glVertex(0,0,0); glVertex(0,1,0)
        glColor(0,0,1); glVertex(0,0,0); glVertex(0,0,1)
        glColor(1,1,1); glVertex(0,0,0); glVertex(0,0,-1)
        glEnd()

    # Draw coordinate axes for the camera
    with opengl_state():
        glMultMatrixf(camera_est.transpose())
        glScale(0.2, 0.2, 0.2)
        glLineWidth(2)
        glBegin(GL_LINES)
        glColor(1,0,0); glVertex(0,0,0); glVertex(1,0,0)
        glColor(0,1,0); glVertex(0,0,0); glVertex(0,1,0)
        glColor(0,0,1); glVertex(0,0,0); glVertex(0,0,1)
        glColor(1,1,1); glVertex(0,0,0); glVertex(0,0,-1)
        glEnd()


window.Refresh()
