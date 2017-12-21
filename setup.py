from distutils.core import setup

setup(
    author='Stefan "eFrane" Graupner',
    author_email='stefan.graupner@oparl.org',
    description = 'Validator for OParl data',
    install_requires=[
        'beautifultable',
        'redis',
        'requests',
        'tqdm'
    ],
    license=open('LICENSE').read(),
    long_description=open('README.md').read(),
    name = 'oparl-validator',
    packages=['core', 'extra'],
    url='https://github.com/OParl/validator',
    version= 'master'
)