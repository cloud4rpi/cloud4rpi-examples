.PHONY: style lint test

style:
	pep8 --show-source --show-pep8 .

lint:
	pylint --rcfile=.pylintrc --reports=n common/*.py raspberrypi/*.py test/*.py

test:
	python -m unittest discover test

ci: style lint test
