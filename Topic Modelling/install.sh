# sh install.sh
pip install --upgrade pip
pip install pip-tools --upgrade
pip-compile requirements.in -v --upgrade
pip install jupyter jupytext black pytest-cov pre-commit pylint isort pip-audit
pip install -e .
pip install git+https://github.com/rwalk/gsdmm.git # gsdmm module
pytest --cov=.
pip-audit -r requirements.txt