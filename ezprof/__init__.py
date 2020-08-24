import time
import functools
from colorama import Fore, Back, Style



def _m(sec):
    if sec > 9.9:
        return f'{Fore.LIGHTRED_EX}{sec:6.1f}{Fore.RESET}s'
    elif sec > 0.099:
        return f'{Fore.LIGHTRED_EX}{sec:6.3f}{Fore.RESET}s'
    else:
        ms = sec * 1000
        if ms > 0.099:
            return f'{Fore.LIGHTMAGENTA_EX}{ms:5.2f}{Fore.RESET}ms'
        else:
            ns = ms * 1000
            return f'{Fore.BLUE}{ns:5.2f}{Fore.RESET}ns'


def _c(cnt):
    return f'{Fore.MAGENTA}{cnt:4d}{Fore.RESET}x'


def _n(name):
    return f'{Fore.MAGENTA}{name}{Fore.RESET}'




class Record:
    def __init__(self, profiler, name):
        self.record = profiler.records[name]
        self.options = profiler.options[name]
        self.rec = self.record

        warmup = self.options.get('warmup', 0)
        self.rec = self.rec[warmup:]

    @property
    def min(self):
        return min(self.rec)

    @property
    def max(self):
        return max(self.rec)

    @property
    def total(self):
        return sum(self.rec)

    @property
    def avg(self):
        return sum(self.rec) / len(self.rec)

    @property
    def count(self):
        return len(self.rec)


class Profiler:
    def __init__(self, timer=time.time):
        self.timer = timer
        self.records = {}
        self.started = {}
        self.options = {}

    def start(self, name, **options):
        self.options[name] = self.options.get(name, options)
        self.started[name] = self.timer()

    def stop(self, name):
        t = self.timer()
        diff = t - self.started[name]
        del self.started[name]
        self.last_started = None
        if name not in self.records:
            self.records[name] = []
        self.records[name].append(diff)

    class TimedScope:
        def __init__(self, profiler, name, **options):
            self.profiler = profiler
            self.name = name
            self.options = options

        def __enter__(self):
            self.profiler.start(self.name, **self.options)

        def __exit__(self, *args):
            self.profiler.stop(self.name)

    def scope(self, name, **options):
        return self.TimedScope(self, name, **options)

    def show(self, name=None):
        print('  min   |   avg   |   max   |  num  |  total  |    name')
        if name is not None:
            names = [name]
        else:

            def keyfunc(name):
                rec = Record(self, name)
                return -rec.total

            names = sorted(self.records.keys(), key=keyfunc)
        for name in names:
            rec = Record(self, name)
            print(
                f'{_m(rec.min)} | {_m(rec.avg)} | {_m(rec.max)} | {_c(rec.count)} '
                f'| {_m(rec.total)} | {_n(name)}')

    def timed(self, name=None, **options):
        if callable(name):
            foo = name
            name = None
        else:
            foo = None

        def decorator(foo):
            if decorator.name is None:
                name = foo.__name__
            else:
                name = decorator.name

            @functools.wraps(foo)
            def wrapped(*args, **kwargs):
                self.start(name, **decorator.options)
                ret = foo(*args, **kwargs)
                self.stop(name)
                return ret

            return wrapped

        decorator.name = name
        decorator.options = options

        return decorator(foo) if foo is not None else decorator

    __call__ = timed


profiler = Profiler()

scope = profiler.scope
show = profiler.show
start = profiler.start
stop = profiler.stop
timed = profiler.timed
