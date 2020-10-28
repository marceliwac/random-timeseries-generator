import random
import math
import sys
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
        raise Exception('Invalid minimum and maximum values specified. Minimum cannot be greater or equal to '
                        'maximum.')
    return _min, _max


def _setup_trend(_trend):
    if _trend is None:
        return Types.Trend[DEFAULT_TREND]
    try:
        trend = Types.Trend[_trend]
        return trend
    except KeyError:
        raise Exception('Invalid trend specified! Allowed types include ' +
                        str(list(map(lambda en: en.name, list(Types.Trend)))) + '.')


def _setup_value_type(_value_type):
    if _value_type is None:
        return Types.ValueType[DEFAULT_VALUE_TYPE]
    try:
        trend = Types.ValueType[_value_type]
        return trend
    except KeyError:
        raise Exception('Invalid value type specified! Allowed types include ' +
                        str(list(map(lambda en: en.name, list(Types.ValueType)))) + '.')


def _get_random_trend():
    return random.choice(list(Types.Trend))


def _get_random_float(_min, _max):
    return _min + random.random() * (_max - _min)


def _get_random_int(_min, _max):
    return random.randint(_min, _max)


def _generate_random_data(_timeseries, _get_random, _min, _max):
    return list(map(lambda timestamp: (timestamp, _get_random(_min, _max)), _timeseries))


def _generate_steady_data(_timeseries, _get_random, _min, _max):
    return list(map(lambda timestamp: (timestamp, (_max - _min)/2), _timeseries))


def _generate_linear_random_data(_timeseries, _get_random, _step, _min, _max, _is_decreasing=False):
    step_count = len(_timeseries)

    def transformation_function(timestamp):
        step_no = timestamp.diff(_timeseries[0]).in_seconds() / _step
        step_value = step_no / step_count
        if _is_decreasing:
            return _min + ((1 - step_value) * (_max - _min))
        else:
            return _min + (step_value * (_max - _min))

    return list(map(transformation_function, _timeseries))


def _generate_quadratic_random_data(_timeseries, _get_random, _step, _min, _max, _is_decreasing=False):
    step_count = len(_timeseries)

    def transformation_function(timestamp):
        step_no = timestamp.diff(_timeseries[0]).in_seconds() / _step
        step_value = step_no / step_count
        if _is_decreasing:
            return _min + ((1 - pow(step_value, 2)) * (_max - _min))
        else:
            return _min + (pow(step_value, 2) * (_max - _min))

    return list(map(transformation_function, _timeseries))


def _generate_logarithmic_random_data(_timeseries, _get_random, _step, _min, _max, _is_decreasing=False):
    step_count = len(_timeseries)

    def transformation_function(timestamp):
        step_no = timestamp.diff(_timeseries[0]).in_seconds() / _step
        step_value = step_no / step_count

        # Interpolate for step_value : [1; e] (e is 2.72...)
        step_value = 1 + ((math.e - 1) * step_value)

        if _is_decreasing:
            return _min + ((1 - math.log(step_value)) * (_max - _min))
        else:
            return _min + (math.log(step_value) * (_max - _min))

    return list(map(transformation_function, _timeseries))


def _map_random_data_to_timeseries(_timeseries, _step, _trend, _value_type, _min, _max):
    random_function = _get_random_int if _value_type == Types.ValueType['INT'] else _get_random_float
    print('Trend is: ' + str(_trend))
    if _trend == Types.Trend['RANDOM']:
        return _generate_random_data(_timeseries, random_function, _min, _max)
    if _trend == Types.Trend['STEADY']:
        return _generate_steady_random_data(_timeseries, random_function, _step, _min, _max)
    if _trend == Types.Trend['LINEAR_INCREASING']:
        return _generate_linear_random_data(_timeseries, random_function, _step, _min, _max)
    if _trend == Types.Trend['LINEAR_DECREASING']:
        return _generate_linear_random_data(_timeseries, random_function, _step, _min, _max, True)
    if _trend == Types.Trend['QUADRATIC_INCREASING']:
        return _generate_quadratic_random_data(_timeseries, random_function, _step, _min, _max)
    if _trend == Types.Trend['QUADRATIC_DECREASING']:
        return _generate_quadratic_random_data(_timeseries, random_function, _step, _min, _max, True)
    if _trend == Types.Trend['LOGARITHMIC_INCREASING']:
        return _generate_logarithmic_random_data(_timeseries, random_function, _step, _min, _max)
    if _trend == Types.Trend['LOGARITHMIC_DECREASING']:
        return _generate_logarithmic_random_data(_timeseries, random_function, _step, _min, _max, True)
    else:
        raise Exception('Invalid trend type supplied!')


def _generate(_step, _start, _end, _trend, _value_type, _min, _max):
    timeseries = []
    current_timestamp = _start
    while current_timestamp <= _end:
        timeseries.append(current_timestamp)
        current_timestamp = current_timestamp.add(seconds=_step)

    timeseries = _map_random_data_to_timeseries(timeseries, _step, _trend, _value_type, _min, _max)

    return timeseries


def generate(_step=None, _start=None, _end=None, _trend=None, _value_type=None, _min=None, _max=None):
    print('_step: ', str(_step))
    print('_start: ', str(_start))
    print('_end: ', str(_end))
    print('_trend: ', str(_trend))
    print('_value_type: ', str(_value_type))
    print('_min: ', str(_min))
    print('_max: ', str(_max))
    print('tend(s):' + '\n' + str(list(Types.Trend)))
    print('value_type(s):' + '\n' + str(list(Types.ValueType)))

    start, end = _setup_dates(_start, _end)
    step = _setup_step(_step, start, end)
    minimum, maximum = _setup_min_max(_min, _max)
    trend = _setup_trend(_trend)
    print('Start date:', start)
    print('End date:', end)
    print('Step:', step)
    print('Minimum:', minimum)
    print('Maximum:', maximum)

    timeseries = _generate(
        step, start, end, trend, _value_type, minimum, maximum
    )

    print(timeseries)
