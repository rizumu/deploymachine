from distutils.core import setup
from setuptools import setup, find_packages


README = read('README.rst')
VERSION = __import__("deploymachine").__version__

setup(
    name = "deploymachine",
    version = VERSION,
    url = "https://github.com/rizumu/deploymachine", #@@@readthedocs
    long_description = README,
    version = VERSION,
    license = "BSD",
    author = "Thomas Schreiber",
    author_email = "tom@insatsu.us",
    packages = find_packages(),
    install_requries = [
        #"openstack.compute",
        "fabric",
        "Jinja2",
        "kokki",
    ]
    classifiers= [
        "Development Status :: 3 - Alpha",
        "Framework :: FW Independent",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    zip_safe = False,
)
