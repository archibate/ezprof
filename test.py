import ezprof
import time


@ezprof.timed
def func():
    time.sleep(0.0233)

func()

with ezprof.scope('hello'):
    time.sleep(0.2)

ezprof.start('world')
for i in range(450):
    pass
ezprof.stop('world')

ezprof.show()
