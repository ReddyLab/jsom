.PHONY: clean install

PYTHON_FILES=$(wildcard jsom/*/*.py)

clean:
	-rm -rf jsom.egg-info build dist

dist: $(PYTHON_FILES)
	X=$$(pip list | grep -e "^build\s"); if [ $$(expr "$$X" : '.*') = 0 ]; then pip install build; fi
	python -m build

install: dist
	pip install dist/*.whl

uninstall:
	pip uninstall jsom
