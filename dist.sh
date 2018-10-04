#!/bin/bash
rm -Rf dist/*
python3 setup.py sdist bdist_wheel
python3 -m twine upload dist/*
rm -Rf dist build heartwave.egg-info

