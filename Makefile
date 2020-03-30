setup:
	python3 -m venv .env/sparkifydb &&\
	source .env/sparkifydb/bin/activate

install:
	python3 -m pip install --upgrade pip &&\
		python3 -m pip install -r requirements.txt

create:
	python3 create_tables.py

process:
	python3 etl.py

etl: create process

test: 
	python3 create_tables.py && python3 -m pytest --nbval etl.ipynb

lint:
	pylint --disable=R,C sql_queries.py create_tables.py etl.py

format:
	python3 -m black *.py

all: setup install lint format test etl
