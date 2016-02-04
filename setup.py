from distutils.core import setup

setup(  name='pygooglesms',
        version='1.0.1',
        description='Python bindings for Google Voice SMS',
        author='Reilly Steele',
        author_email='steelereily@gmail.com',
        url='https://github.com/Maome/pygooglesms',
        py_modules=['pygooglesms'],
        license='MIT',
        long_description='This module can be installed or used as an included '
                'file to give your application access to Google Voice\'s SMS '
                'sending functionality',
        install_requires=['beautifulsoup4>=1.2', 'requests>=2.0'],
        )

