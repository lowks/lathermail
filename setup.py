import os
from setuptools import setup, find_packages

install_requires = [
    "Flask==0.10.1",
    "Flask-RESTful==0.2.12",
    "Flask-PyMongo==0.3.0",
    "pymongo==2.7.1",
    "python-dateutil==2.2",
    "SQLAlchemy==1.0.9",
    "Flask-SQLAlchemy==2.1",
]


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="lathermail",
    url="https://github.com/reclosedev/lathermail/",
    version="0.1.3",
    author="Roman Haritonov",
    author_email="reclosedev@gmail.com",
    license="MIT",
    packages=find_packages("."),
    install_requires=install_requires,
    entry_points={
        'console_scripts':
            [
                'lathermail = lathermail.run_all:main',
            ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Server",
    ],
)
