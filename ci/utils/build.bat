@echo off
python setup.py bdist_wheel
pip install --upgrade --no-index --find-links=dist pynwrfc
pytest -vv


