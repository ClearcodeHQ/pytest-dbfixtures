from setuptools import setup

setup(
    name='pytest-dbfixtures',
    version='0.0.1',
    description='dbfixtures plugin for py.test.',
    author='Clearcode - The A Room',
    author_email='thearoom@clearcode.cc',
    url='https://github.com/clearcode/pytest-dbfixtures',
    packages=['pytest_dbfixtures'],
    install_requires=[
        'pytest',
        'summon_process',
        'pyaml',
        'pymlconf',
    ],
    include_package_data=True,
    entry_points={
        'pytest11': [
            'pytest_dbfixtures = pytest_dbfixtures.pytest_dbfixtures'
        ]},
    keywords='py.test pytest redis mongo',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
        'Topic :: Utilities',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7']
)
