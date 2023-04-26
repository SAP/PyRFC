# clean test build folder
rm -rf build tests/tmp/*
# build the sdist and package
python -m build --no-isolation  --sdist --wheel --outdir tests/tmp
# unzip sdist
tar -xvf tests/tmp/*.tar.gz -C tests/tmp
# unzip package
unzip tests/tmp/*.whl -d tests/tmp