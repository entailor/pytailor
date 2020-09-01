from enum import Enum


class State(Enum):
    PRE = -3
    ARCHIVED = -2
    FAILED = -1
    STOPPED = 0
    WAITING = 1
    READY = 2
    RESERVED = 3
    RUNNING = 4
    COMPLETED = 5
