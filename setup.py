import os
import sys
import codecs
from setuptools import setup

if sys.version_info < (3, 6, 0):
    raise RuntimeError('Python 3.6 or higher is required')

here = os.path.abspath(os.path.dirname(__file__))
with codecs.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='heartwave',
    version='0.9.2',
    description='Heart rate measurement from webcam or video',
    long_description=long_description,
    packages=['heartwave'],
    url='https://github.com/erdewit/heartwave',
    author='Ewald R. de Wit',
    author_email='ewald.de.wit@gmail.com',
    license='BSD',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='PPG photoplethysmogram heart rate webcam',
    entry_points={
        'console_scripts': [
            'heartwave=heartwave.app:main',
        ]
    },
    package_data={'heartwave': ['data/*.xml']},
    install_requires=[
        'PyQt5', 'PyQtChart', 'numpy', 'scipy',
        'opencv-contrib-python'],
)
