from enum import IntEnum


class FieldState(IntEnum):
    EMPTY = 0
    MISS = 1
    UNDAMAGED = 2
    DAMAGED = 3
    DESTROYED = 4