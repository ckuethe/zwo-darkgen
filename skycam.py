#!/usr/bin/env python3

import os
import sys
import time
import zwoasi as asi
from multiprocessing import Process


# Initialize camera
def initialize(_library='asi.so'):

    asi.init(_library)

    num_cameras = asi.get_num_cameras()
    if num_cameras == 0:
        raise NameError('No cameras found')
    if num_cameras > 1:
        raise NameError('Only one camera is allowed')

    cameras_found = asi.list_cameras()

    global camera, camera_info
    camera = asi.Camera(0)
    camera_info = camera.get_camera_property()

    camera.set_control_value(asi.ASI_BANDWIDTHOVERLOAD, camera.get_controls()['BandWidth']['MinValue'])

    camera.stop_video_capture()
    camera.stop_exposure()


# Configure camera settings
# _drange must be either 8 or 16
# _oolor is a boolean
def configure(_gain=150, _exposure=30000, _wb_b=99, \
              _wb_r=75, _gamma=60, _brightness=50, _flip=0, \
              _drange=8, _color=False):

    global camera
    camera.set_control_value(asi.ASI_GAIN, _gain)
    camera.set_control_value(asi.ASI_EXPOSURE, _exposure)
    camera.set_control_value(asi.ASI_WB_B, _wb_b)
    camera.set_control_value(asi.ASI_WB_R, _wb_r)
    camera.set_control_value(asi.ASI_GAMMA, _gamma)
    camera.set_control_value(asi.ASI_BRIGHTNESS, _brightness)
    camera.set_control_value(asi.ASI_FLIP, _flip)

    global drange, color
    color = _color
    drange = _drange


# Capture a single frame and save it to a file
def capture(_path='./', _file=None, _extenstion='.jpg'):

    if _file is None:
        _file = time.strftime('%Y-%m-%d-%H-%M-%S-%Z')

    filename = _path + _file + _extenstion

    global drange, color

    if color is True:
        camera.set_image_type(asi.ASI_IMG_RGB24)
    else:
        if drange is 8:
            camera.set_image_type(asi.ASI_IMG_RAW8)
        elif drange is 16:
            camera.set_image_type(asi.ASI_IMG_RAW16)

    camera.capture(filename=filename)


# Recording process function
# Use timelapse function to start reording
def record(_directory, _delay):

    while True:
        filename = str(time.time()).replace('.', '_')
        capture(_path=_directory, _file=filename, _extenstion=_extension)
        time.sleep(_delay / 1000)


# Run a background proess for creating a timelapse
# Uses a RAM disk by default
# _delay is time in milliseconds between expositions
def timelapse(_action='start', _directory='/mnt/skycam', _delay=1000, _extenstion='.jpg'):

    if _action == 'start':
        start()
    elif _action == 'stop':
        stop()

    # Start the timelapse
    # Starts a timelapse in the bakground
    def start():

        if not os.path.exists(_directory):
            raise NameError('Timelapse diretory does not exsist')

        global recorder
        recorder = Process(target=record, args=(_directory,))
        recorder.start()

    # Stops the timelapse
    def stop():

        recorder.join()
