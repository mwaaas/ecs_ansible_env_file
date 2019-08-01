test_python3:
	docker-compose build --build-arg PYTHON_VERSION=3.6.7 app
	docker-compose run app python -m unittest test_ecs_env.py
test_python2:
	docker-compose build --build-arg PYTHON_VERSION=2.7.15 app
	docker-compose run app python -m unittest test_ecs_env

deploy:
	rm -r -f dist
	docker-compose run --no-deps -e PYPI_PASSWORD=$(PYPI_PASSWORD) -e PYPI_USER=$(PYPI_USER) -e VERSION=$(CIRCLE_TAG) app bash -c 'printf "[distutils]\nindex-servers = pypi \n[pypi]\nusername:$(PYPI_USER)\npassword:$(PYPI_PASSWORD)\n" > ~/.pypirc && python setup.py sdist && twine upload dist/*'