declare -a PYTHONS=("2715" "369" "374" "380")

rm -rf tests/__pycache__
rm -rf tests/stfc-mrfc/__pycache__

for PYTHON_VERSION in "${PYTHONS[@]}"
do

    echo py$PYTHON_VERSION
    pyenv activate py$PYTHON_VERSION
    python setup.py bdist_wheel
    pip install --upgrade --no-index --find-links=dist pyrfc
    pytest -vv

done


