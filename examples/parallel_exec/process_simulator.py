from random import randrange, uniform
from sys import stderr
from time import sleep

exit_code = randrange(0, 3)
long_error = (
    'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras sed '
    'ullamcorper tortor. Vestibulum convallis nibh nec eros aliquet sodales. '
    'Maecenas pellentesque interdum turpis quis mattis. Ut semper aliquet '
    'erat, ac fringilla mauris iaculis iaculis. Phasellus sed felis purus. '
    'Aenean porta nunc ligula, vitae egestas ligula rhoncus at. Orci varius '
    'natoque penatibus et magnis dis parturient montes, nascetur ridiculus '
    'mus. Sed lobortis finibus aliquet.'
)

print('Starting the process')
sleep(uniform(0.25, 2.5))

if exit_code == 1:
    print('Short error (1): SimulatedError', file=stderr)
elif exit_code == 2:
    print(f'Long error (2):\n{long_error}', file=stderr)

sleep(uniform(0.25, 2.5))

print('Process completed')
exit(exit_code)
