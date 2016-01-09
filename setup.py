from setuptools import setup
setup(
    author="Johannes Brodwall",
    author_email="jhannes@gmail.com",
    version="0.2",
    description="Growl notifications for pytest results.",
    name="pytest-growl",
    install_requires=['gntp>=1.0.2'],
    package_data={'':['*.png']},
    keywords="pytest, pytest-, growl, py.test",
    packages=['pytest_growl'],
    entry_points={'pytest11': ['pytest_growl = pytest_growl.pytest_growl', ]},)
