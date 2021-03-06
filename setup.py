from distutils.core import setup

setup(
    author='Stefan "eFrane" Graupner',
    author_email='stefan.graupner@oparl.org',
    description = 'Validator for OParl data',
    install_requires=[
        'beautifultable',
        'PyGObject',
        'redis',
        'requests',
        'tqdm'
    ],
    license=open('LICENSE').read(),
    long_description=open('README.md').read(),
    name = 'oparl_validator',
    packages=['oparl_validator', 'oparl_validator.core', 'oparl_validator.extra'],
    url='https://github.com/OParl/validator',
    version= 'master'
)