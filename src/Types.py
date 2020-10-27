import enum


class Trend(enum.Enum):
    RANDOM = 0
    STEADY = 1
    LINEAR_INCREASING = 2
    LINEAR_DECREASING = 3
    QUADRATIC_INCREASING = 4
    QUADRATIC_DECREASING = 5
    LOGARITHMIC_INCREASING = 6
    LOGARITHMIC_DECREASING = 7


class ValueType(enum.Enum):
    INT = 0
    FLOAT = 1
