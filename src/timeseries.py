import random
import src.Types as Types


def generate(length=10, step=1, start=None, end=None, trend=None, value_type='int', minimum=0, maximum=10):
    print('length: ', str(length))
    print('step: ', str(step))
    print('start: ', str(start))
    print('end: ', str(end))
    print('trend: ', str(trend))
    print('value_type: ', str(value_type))
    print('minimum: ', str(minimum))
    print('maximum: ', str(maximum))
    print('tend(s):' + '\n' + str(list(Types.Trend)))
    print('value_type(s):' + '\n' + str(list(Types.ValueType)))