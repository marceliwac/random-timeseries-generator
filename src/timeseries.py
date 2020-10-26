import random
import pendulum
import src.Types as Types

# Amount of time that the data will span if start and/or end date won't be supplied.
DEFAULT_DATE_SPAN_IN_DAYS = 7

# Step of each timeseries entry in seconds.
DEFAULT_STEP_IN_SECONDS = 3600

# Trend which data will follow over time.
DEFAULT_TREND = 'STEADY'

# Value type that will be used.
DEFAULT_VALUE_TYPE = 'INT'

# Minimum value for the data range.
DEFAULT_MIN_VALUE = 0

# Maximum value for the data range.
DEFAULT_MAX_VALUE = 7


def _setup_dates(_start, _end):
    if _start is None and _end is None:
        end = pendulum.now()
        start = end.subtract(days=DEFAULT_DATE_SPAN_IN_DAYS)
    elif _start is not None:
        start = pendulum.parse(_start)
        end = start.add(days=DEFAULT_DATE_SPAN_IN_DAYS)
    elif _end is not None:
        end = pendulum.parse(_end)
        start = end - end.subtract(days=DEFAULT_DATE_SPAN_IN_DAYS)
    else:
        start = pendulum.parse(_start)
        end = pendulum.parse(_end)

    return start, end


def _setup_step(_step, _start, _end):
    if _step is not None:
        total_duration = _start.diff(_end).in_seconds()
        if total_duration < _step:
            return total_duration
        return _step
    return DEFAULT_STEP_IN_SECONDS


def _setup_min_max(_min, _max):
    if _min is None and _max is None:
        return DEFAULT_MIN_VALUE, DEFAULT_MAX_VALUE
    elif _min is None:
        if _max > 0:
            return 0, _max
        return _max - (DEFAULT_MAX_VALUE - DEFAULT_MIN_VALUE), _max
    elif _max is None:
        return _min, _min + (DEFAULT_MAX_VALUE - DEFAULT_MIN_VALUE)

    if _min >= _max:
        raise AttributeError('Invalid minimum and maximum values specified. Minimum cannot be greater or equal to '
                             'maximum.')
    return _min, _max


def _get_random_trend():
    return random.choice(list(Types.Trend))


def _get_random_float(_min, _max):
    return _min + random.random() * (_max - _min)


def _get_random_int(_min, _max):
    return random.randint(_min, _max)


def _generate(_step, _start, _end, _trend, _value_type, _min, _max):
    timeseries = []
    current_timestamp = _start
    while current_timestamp <= _end:
        timeseries.append((current_timestamp, _get_random_int(_min, _max)))
        current_timestamp = current_timestamp.add(seconds=_step)

    return timeseries


def generate(_step=None, _start=None, _end=None, _trend=None, _value_type=None, _min=None, _max=None):
    print('step: ', str(_step))
    print('start: ', str(_start))
    print('end: ', str(_end))
    print('trend: ', str(_trend))
    print('value_type: ', str(_value_type))
    print('_min: ', str(_min))
    print('_max: ', str(_max))
    print('tend(s):' + '\n' + str(list(Types.Trend)))
    print('value_type(s):' + '\n' + str(list(Types.ValueType)))

    start, end = _setup_dates(_start, _end)
    step = _setup_step(_step, start, end)
    minimum, maximum = _setup_min_max(_min, _max)
    print('Start date:', start)
    print('End date:', end)
    print('Step:', step)
    print('Minimum:', minimum)
    print('Maximum:', maximum)

    timeseries = _generate(
        step, start, end, _trend, _value_type, minimum, maximum
    )

    print(timeseries)
