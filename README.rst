EzProf
======

Easy and intuitive Python profiling API, for example:

.. code-block:: python

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


Basically it measures time spent between ``start()`` and ``stop()`` using
the Python-builtin function ``time.time()``.

Profiling APIs
**************

There are 3 ways to use this profiler:

1. ``ezprof.start()`` and ``ezprof.stop()`` are the most fundemental APIs:
   It will measure the time difference between ``start`` and ``stop``.
   Then save the result according to the given name. e.g.:

.. code-block:: python

    import ezprof
    import time

    def do_something_A():
        time.sleep(0.01)

    def do_something_B():
        time.sleep(0.1)

    ezprof.start('A')
    do_something_A()
    ezprof.stop('A')

    ezprof.start('B')
    do_something_B()
    ezprof.stop('B')

    ezprof.show()


.. code-block:: none

      min   |   avg   |   max   |  num  |  total  |    name
     0.100s |  0.100s |  0.100s |    1x |  0.100s | B
    10.10ms | 10.10ms | 10.10ms |    1x | 10.10ms | A


2. ``with ezprof.scope()``, this one makes our code cleaner and readable.
   Basically, it will automatically invoke ``stop`` when the indented block exited.
   For more details about the ``with`` syntax in Python, see `this tutorial <https://www.pythonforbeginners.com/files/with-statement-in-python>`_.

.. code-block:: python

    import ezprof
    import time

    def do_something_A():
        time.sleep(0.01)

    def do_something_B():
        time.sleep(0.1)

    with ezprof.scope('A'):
        do_something_A()
    # automatically invoke stop('A')

    with ezprof.scope('B'):
        do_something_B()
    # automatically invoke stop('B')

    ezprof.show()


.. code-block:: none

      min   |   avg   |   max   |  num  |  total  |    name
     0.100s |  0.100s |  0.100s |    1x |  0.100s | B
    10.10ms | 10.10ms | 10.10ms |    1x | 10.10ms | A


3. ``@ezprof.timed``, this one is very intuitive when profiling functions.
   It will measure the time spent in the function, i.e. ``start`` when entering the function, ``stop`` when leaving the function, and the record name is the function name.

.. code-block:: python

    import ezprof
    import time

    @ezprof.timed
    def do_something_A():
        time.sleep(0.01)

    @ezprof.timed
    def do_something_B():
        time.sleep(0.1)

    do_something_A()
    do_something_B()

    ezprof.print()


.. code-block:: none

      min   |   avg   |   max   |  num  |  total  |    name
     0.100s |  0.100s |  0.100s |    1x |  0.100s | do_something_B
    10.10ms | 10.10ms | 10.10ms |    1x | 10.10ms | do_something_A


.. warning::

    When combining ``@ezprof.timed`` with other decorators, then
    ``@ezprof.timed`` should be put **above** it to get desired output, e.g.:

    .. code-block:: python

        def my_decorator(foo):
            def wrapped():
                do_something()
                return foo()

        @ezprof.timed
        @my_decorator
        def substep():
            ...


Recording multiple entries
**************************

When a same **name** is used for multiple times, then they will be merged into one, e.g.:

.. code-block:: python

    import ezprof
    import time

    def do_something_A():
        time.sleep(0.01)

    def do_something_B():
        time.sleep(0.1)

    ezprof.start('A')
    do_something_A()
    ezprof.stop('A')

    ezprof.start('A')
    do_something_B()
    ezprof.stop('A')

    ezprof.start('B')
    do_something_B()
    ezprof.stop('B')

    ezprof.show()

will obtain:

.. code-block:: none

      min   |   avg   |   max   |  num  |  total  |    name
    10.10ms | 55.12ms |  0.100s |    2x |  0.110s | A
     0.100s |  0.100s |  0.100s |    1x |  0.100s | B


- ``min`` is the minimum time in records.
- ``avg`` is the average time of records.
- ``max`` is the maximum time in records.
- ``num`` is the number of record entries.
- ``total`` is the total costed time of records.


Profiler options
****************

Due to Taichi's JIT mechanism, a kernel will be **compiled** on its first invocation.
So the first record will be extremely long compared to the following records since it
**involves both compile time and execution time**, e.g.:

.. code-block:: none

       min   |   avg   |   max   |  num  |  total  |    name
      2.37ms |  3.79ms |  1.615s | 1900x |  7.204s | substep

.. code-block:: none

       min   |   avg   |   max   |  num  |  total  |    name
      2.37ms |  2.95ms | 12.70ms | 1895x |  5.592s | substep


As you see, this make our result inaccurate, especially the ``max`` column.

To avoid this, you may specify a ``warmup`` option to ``ti.profiler``, e.g.:

.. code-block:: python

    @ezprof.timed(warmup=5)
    @ti.kernel
    def substep():
        ...


Set ``warmup=5`` for example, will **discard** the first 5 record entries.
I.e. discard the kernel compile time and possible TLB and cache misses on start up.


.. warning::

    ``ezprof`` **only works in Python-scope** for Taichi users, e.g.::

        @ti.func
        def substep():
            ezprof.start('hello')  # won't work as you expected...
            ...
            ezprof.stop('hello')

        @ezprof.timed  # won't work as you expected...
        @ti.func
        def hello():
            ...

        @ezprof.timed  # Kernels are OK!
        @ti.kernel
        def hello():
            ...

    To do profiling **inside Taichi-scope**, please see the ``KernelProfiler``
    provided by Taichi itself.

(TODO: clarify the relationship between ``ezprof`` and ``taichi#1493``)
