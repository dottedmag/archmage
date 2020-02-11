set -ex

pip install pytest pychm
python setup.py build
python setup.py develop
python -m pytest
