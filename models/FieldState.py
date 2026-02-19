from enum import Enum

class FieldState(Enum):
    EMPTY = 0
    MISS = 1
    UNDAMAGED = 2
    DAMAGED = 3
    DESTROYED = 4