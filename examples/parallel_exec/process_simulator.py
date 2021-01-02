from random import randrange, uniform
from sys import stderr
from time import sleep

exit_code = randrange(0, 3)

print('Starting the process')
sleep(uniform(0.25, 2.5))

if exit_code:
    print(f'Error scenario {exit_code}', file=stderr)

sleep(uniform(0.25, 2.5))

print('Process completed')
exit(exit_code)
