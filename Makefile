all: macli

macli: macli.py
	pyinstaller -F macli.py

clean:
	rm -fR build dist *pyc *spec 
