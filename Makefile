test:
	coverage run --omit=venv/** -m pytest && coverage html

run:
	sanic --debug --reload --access-logs --worker 2 ironsigma.checkbook.app

clean:
	rm -r htmlcov/ .coverage .pytest_cache
	find . -name '*.pyc' -o -name __pycache__ -exec rm -r "{}" +
