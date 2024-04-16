from enum import Enum


class Status(str, Enum):
    IN_PROCESS = 'in-process'
    DONE = 'done'
    ERROR = 'error'
