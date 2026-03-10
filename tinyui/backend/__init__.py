"""
TinyPedal backend adapter layer.

All tinypedal imports used by tinyui are centralized here.
If tinypedal changes, only this package needs updating.
"""

# Re-export all adapter modules
from .constants import *
from .controls import *
from .data import *
from .formatter import *
from .misc import *
from .regex import *
from .settings import *
from .validator import *
