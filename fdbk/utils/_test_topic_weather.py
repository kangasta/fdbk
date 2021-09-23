from random import uniform


FIELDS = ['temperature', 'humidity', 'pressure']


UNITS = [
    dict(field='temperature', unit='celsius'),
    dict(field='humidity', unit='percent'),
    dict(field='pressure', unit='hectopascal'),
]


def _get_ti_params(method='average'):
    return dict(method=method, name='Statistics')


DATA_TOOLS = [
    dict(
        field='temperature',
        method='table_item',
        parameters=_get_ti_params()),
    dict(
        field='temperature',
        method='table_item',
        parameters=_get_ti_params('min')),
    dict(
        field='temperature',
        method='table_item',
        parameters=_get_ti_params('max')),
    dict(field='humidity', method='table_item', parameters=_get_ti_params()),
    dict(field='pressure', method='table_item', parameters=_get_ti_params()),
    dict(field='temperature', method='line'),
    dict(field='humidity', method='line'),
    dict(field='pressure', method='line'),
]


TEMPLATE_DICT = dict(
    name='test_topic_weather',
    description='Random weather measurement data for testing.',
    type_str='template',
    fields=FIELDS,
    units=UNITS,
    data_tools=DATA_TOOLS,
)


class TestTopicWeather:
    def __init__(self, name=None, description=None):
        self._name = name
        self._description = description

    @property
    def template(self):
        return TEMPLATE_DICT

    @property
    def topic(self):
        return dict(
            name=self._name,
            template='test_topic_weather',
            type_str='topic',
        )

    @property
    def data(self):
        return dict(
            temperature=uniform(-20, 30),
            humidity=uniform(0, 100),
            pressure=uniform(980, 1030)
        )
