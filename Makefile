all: macli

macli: macli.py venv
	venv/bin/pyinstaller -F macli.py

venv: venv/bin/activate

venv/bin/activate: requirements.txt
	test -d venv || virtualenv venv
	venv/bin/pip3 install -Ur requirements.txt
	touch venv/bin/activate

clean:
	rm -fR build dist *pyc *spec 
