#!/bin/bash
python3 setup.py sdist bdist_wheel
twine upload dist/*
rm -Rf build
rm -Rf dist
