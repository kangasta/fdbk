'''Data analysis tools

Functions to ease the simple data analysis done by the DBConnection.

'''

from ._chart_funcs import *
from ._utils import *
from ._value_funcs import *

functions = {**VALUE_FUNCS, **CHART_FUNCS}  # pylint: disable=invalid-name
