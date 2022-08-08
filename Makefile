.PHONY: clean install

PYTHON_FILES=$(wildcard jsom/*/*.py)

clean:
	-rm -rf jsom.egg-info build dist

dist: $(PYTHON_FILES)
	if [ -z $$(pip list | grep -e "^build\s") ]; then pip install build; fi
	python -m build

install: dist
	pip install dist/*.whl

uninstall:
	pip uninstall jsom
