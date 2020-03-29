'''Data analysis tools

Functions to ease the simple data analysis done by the DBConnection.

'''

from ._value_funcs import *
from ._chart_funcs import *

functions = {**VALUE_FUNCS, **CHART_FUNCS}  # pylint: disable=invalid-name
