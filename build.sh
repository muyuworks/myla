cd js
./build.sh
cd ..

python -m build
python -m twine upload --repository pypi dist/*$1*.whl
