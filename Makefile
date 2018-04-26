venv:
	virtualenv -p python3.6 venv
	make pip

pip:
	venv/bin/pip install -r requirements.txt

