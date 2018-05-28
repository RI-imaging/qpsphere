from os.path import dirname, realpath, exists
from distutils.command.build import build
from setuptools import setup, find_packages
import sys


author = u"Paul Müller"
authors = [author]
description = 'library for analyzing spherical objects in phase imaging'
name = 'qpsphere'
year = "2017"

sys.path.insert(0, realpath(dirname(__file__))+"/"+name)
from _version import version


class BuildIncludeBinaries(build):
    """Put binary files in resource directory for wheel builds"""
    def run(self):
        import qpsphere
        qpsphere.util.download_binaries(package_dir=True)
        # run the original build command
        super(BuildIncludeBinaries, self).run()


setup(
    name=name,
    author=author,
    author_email='dev@craban.de',
    url='https://github.com/RI-imaging/qpsphere',
    version=version,
    packages=find_packages(),
    package_dir={name: name},
    # Note: package data are not included in the source distribution
    # (manually excluded in MANIFEST.in)
    package_data={"qpsphere": ['resources/*']},
    cmdclass={"build": BuildIncludeBinaries},
    license="MIT",
    description=description,
    long_description=open('README.rst').read() if exists('README.rst') else '',
    install_requires=["appdirs",
                      "lmfit",
                      "matplotlib",
                      "nrefocus>=0.1.5",
                      "numpy>=1.9.0",
                      "scikit-image>=0.11.0",
                      "scipy>=0.18.0",
                      "qpimage",
                      ],
    setup_requires=['pytest-runner'],
    tests_require=["pytest"],
    python_requires='>=3.5, <4',
    keywords=["digital holographic microscopy",
              "optics",
              "quantitative phase imaging",
              "refractive index",
              "scattering",
              ],
    classifiers= [
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Science/Research'
                 ],
    platforms=['ALL'],
    )
