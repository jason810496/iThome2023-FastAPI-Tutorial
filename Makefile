dev:
	docker compose --file docker-compose-dev.yml up --build -d
prod:
	docker compose --file docker-compose-prod.yml up -d
	
primary-replica: primary-replica-reset primary-replica-setup primary-replica-test

primary-replica-reset:
	./primary-replica/reset.sh
primary-replica-setup:
	./primary-replica/setup.sh
primary-replica-test:
	./primary-replica/test.sh
down:
	docker compose down

.PHONY: dev prod primary-replica down