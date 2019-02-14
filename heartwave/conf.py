from pathlib import Path

MIN_BPM = 40
MAX_BPM = 180
CAM_ID = 0
STARTUP_TIME = 1.5
MAX_SAMPLES = 256
AV_BPM_PERIOD = 1.0
FACE_DETECT_PAUSE = 1.0
FACE_TRACKING_TIMEOUT = 5

# allow user settings to override the standard settings
path = Path.home() / '.heartwave.conf'
if path.is_file():
    with open(path) as f:
        code = f.read()
        exec(code)
