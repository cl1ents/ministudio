from Helpers import clamp01, lerp
from easing_functions import *

currentSpeed = 1800
maxFov = 120
minFov = 70
maxSpeed = 1500

fov = lerp(minFov, maxFov, clamp01(currentSpeed / maxSpeed), QuinticEaseIn)

print(fov)