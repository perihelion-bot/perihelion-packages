from enum import StrEnum, auto

class SolveMode(StrEnum):
    RANDOM = auto()
    MAX = auto()
    MIN = auto()


class OperationEnum(StrEnum):
    ADD = '+'
    SUBTRACT = '-'
    MULTIPLY = '*'
    DIVIDE = '/'
    POW = '^'

class FormatEnum(StrEnum):
    LIST = 'l'
    SUM = 's'
    GREATER = '>'
    LESS = '<'
    EQUALS = '=='
    TOP = "top"
    BOTTOM = "bottom"

class FormatType(StrEnum):
    FORMAT_DEFAULT = auto()
    FORMAT_SUM = auto()
    FORMAT_LIST = auto()
    FORMAT_LIST_SPLIT = auto()

class ThresholdType(StrEnum):
    GREATER = auto()
    LESS = auto()
    MAX = auto()
    MIN = auto()
    EQUALS = auto()
    TOP = auto()
    BOTTOM = auto()
