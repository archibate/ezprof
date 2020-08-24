project_name = 'ezprof'
version = '0.0.1'
description = 'Easy and intuitive Python profiling API'
with open('README.rst', 'r') as f:
    long_description = f.read()
long_description = '''
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
'''
classifiers = [
    'Intended Audience :: Developers',
    'Operating System :: OS Independent',
]
python_requires = '>=3.6'
install_requires = [
    'colorama',
]

import setuptools

setuptools.setup(
    name=project_name,
    version=version,
    author='彭于斌',
    author_email='1931127624@qq.com',
    description=description,
    long_description=long_description,
    classifiers=classifiers,
    python_requires=python_requires,
    install_requires=install_requires,
    packages=setuptools.find_packages(),
)
