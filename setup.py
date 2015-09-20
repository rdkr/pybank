from setuptools import setup

setup(
    name='pybank',
    version='0.2',
    py_modules=['pybank'],
    install_requires=[
        'pyyaml',
        'appdirs',
        'requests',
        'beautifulsoup4',
        'tabulate',
        'click'
    ],
    entry_points='''
        [console_scripts]
        pybank=pybank:cli
    '''
)