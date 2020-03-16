declare -a PYTHONS=("369" "375" "380")

for PYTHON_VERSION in "${PYTHONS[@]}"
do
    rm -rf tests/__pycache__
    rm -rf tests/stfc-mrfc/__pycache__
    echo py$PYTHON_VERSION
    pyenv activate py$PYTHON_VERSION
    python setup.py bdist_wheel
    pip install --upgrade --force --find-links=dist pynwrfc
    [[ $1 != skip ]] && pytest -vv
done
python setup.py sdist


