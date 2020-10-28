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

# How the missing data will be introduced to dataset
DEFAULT_MISSING_METHOD = 'REMOVE'


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
        value_type = Types.ValueType[_value_type]
        return value_type
    except KeyError:
        raise Exception('Invalid value type specified! Allowed types include ' +
                        str(list(map(lambda en: en.name, list(Types.ValueType)))) + '.')


def _setup_missing(_missing):
    if _missing is None:
        return 0.0
    elif 0 <= _missing < 1:
        return _missing
    raise Exception('Invalid value of missing data specified. The parameter has to be a float between 0 and 1.')


def _setup_missing_method(_missing_method):
    if _missing_method is None:
        return Types.MissingMethod[DEFAULT_MISSING_METHOD]
    try:
        missing_method = Types.MissingMethod[_missing_method]
        return missing_method
    except KeyError:
        raise Exception('Invalid missing method specified! Allowed types include ' +
                        str(list(map(lambda en: en.name, list(Types.MissingMethod)))) + '.')


def _get_random_trend():
    return random.choice(list(Types.Trend))


def _get_random_float(_min, _max):
    return _min + random.random() * (_max - _min)


def _get_random_int(_min, _max):
    return random.randint(_min, _max)


def _generate_random_data(_timeseries, _get_random, _min, _max):
    timeseries = []
    for point in _timeseries:
        timeseries.append((point, _get_random(_min, _max)))
    return timeseries


def _generate_steady_data(_timeseries, _get_random, _min, _max):
    timeseries = []
    for point in _timeseries:
        timeseries.append((point, (_max - _min)/2))
    return timeseries


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
    if _trend == Types.Trend.RANDOM:
        return _generate_random_data(_timeseries, random_function, _min, _max)
    if _trend == Types.Trend.STEADY:
        return _generate_steady_random_data(_timeseries, random_function, _step, _min, _max)
    if _trend == Types.Trend.LINEAR_INCREASING:
        return _generate_linear_random_data(_timeseries, random_function, _step, _min, _max)
    if _trend == Types.Trend.LINEAR_DECREASING:
        return _generate_linear_random_data(_timeseries, random_function, _step, _min, _max, True)
    if _trend == Types.Trend.QUADRATIC_INCREASING:
        return _generate_quadratic_random_data(_timeseries, random_function, _step, _min, _max)
    if _trend == Types.Trend.QUADRATIC_DECREASING:
        return _generate_quadratic_random_data(_timeseries, random_function, _step, _min, _max, True)
    if _trend == Types.Trend.LOGARITHMIC_INCREASING:
        return _generate_logarithmic_random_data(_timeseries, random_function, _step, _min, _max)
    if _trend == Types.Trend.LOGARITHMIC_DECREASING:
        return _generate_logarithmic_random_data(_timeseries, random_function, _step, _min, _max, True)
    else:
        raise Exception('Invalid trend type supplied!')


def _get_n_random_indices(_max, _n):
    count_to_remove = round(_max * _n)
    indices = []

    if count_to_remove >= _max:
        count_to_remove = _max - 1

    while count_to_remove > 0:
        index = _get_random_int(0, _max - 1)
        if index not in indices:
            indices.append(index)
            count_to_remove -= 1

    return indices


def _set_elements_to_none_at_indices(_timeseries, _indices):
    timeseries = []
    for index in _indices:
        _timeseries[index] = None
    for element in _timeseries:
        if element is not None:
            timeseries.append(element)
    return timeseries


def _set_element_values_to_none_at_indices(_timeseries, _indices):
    for index in _indices:
        timestamp, value = _timeseries[index]
        _timeseries[index] = (timestamp, None)
    return _timeseries


def _introduce_missing_values(_timeseries, _missing, _missing_method):
    if _missing == 0:
        return _timeseries

    indices = _get_n_random_indices(len(_timeseries), _missing)
    if _missing_method == Types.MissingMethod.REMOVE:
        return _set_elements_to_none_at_indices(_timeseries, indices)
    if _missing_method == Types.MissingMethod.SET_NONE:
        return _set_element_values_to_none_at_indices(_timeseries, indices)


def _generate(_step, _start, _end, _trend, _value_type, _min, _max, _missing, _missing_method):
    timeseries = []
    current_timestamp = _start
    while current_timestamp <= _end:
        timeseries.append(current_timestamp)
        current_timestamp = current_timestamp.add(seconds=_step)

    timeseries = _map_random_data_to_timeseries(timeseries, _step, _trend, _value_type, _min, _max)
    timeseries = _introduce_missing_values(timeseries, _missing, _missing_method)

    return timeseries


def generate(_step=None, _start=None, _end=None, _trend=None, _value_type=None, _min=None, _max=None, _missing=None,
             _missing_method=None):
    print('_step: ', str(_step))
    print('_start: ', str(_start))
    print('_end: ', str(_end))
    print('_trend: ', str(_trend))
    print('_value_type: ', str(_value_type))
    print('_min: ', str(_min))
    print('_max: ', str(_max))
    print('_missing: ', str(_missing))
    print('_missing_method: ', str(_missing_method))
    print('trend(s):' + '\n' + str(list(Types.Trend)))
    print('value_type(s):' + '\n' + str(list(Types.ValueType)))
    print('missing_method(s):' + '\n' + str(list(Types.MissingMethod)))

    start, end = _setup_dates(_start, _end)
    step = _setup_step(_step, start, end)
    minimum, maximum = _setup_min_max(_min, _max)
    trend = _setup_trend(_trend)
    value_type = _setup_value_type(_value_type)
    missing = _setup_missing(_missing)
    missing_method = _setup_missing_method(_missing_method)

    print('Start date: ' + str(start))
    print('End date: ' + str(end))
    print('Step: ' + str(step))
    print('Value type: ' + str(value_type))
    print('Trend: ' + str(trend))
    print('Minimum: ' + str(minimum))
    print('Maximum: ' + str(maximum))
    print('Missing: ', str(missing))
    print('Missing method: ', str(missing_method))

    timeseries = _generate(
        step, start, end, trend, _value_type, minimum, maximum, missing, missing_method
    )

    print('TIMESERIES: ' + str(timeseries))
