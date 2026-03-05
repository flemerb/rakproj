install:
    pip install -r requirements.txt

test:
    pytest tests/ -v

lint:
    flake8 src/ services/
    black --check src/ services/

build:
    docker-compose build

up:
    docker-compose up -d

down:
    docker-compose down

train:
    curl -X POST http://localhost:8080/api/v1/admin/retrain \
      -H "Authorization: Bearer $(TOKEN)"

logs:
    docker-compose logs -f
