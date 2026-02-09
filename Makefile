.PHONY: help build up down logs clean test install dev stop restart status

help: ## Mostra ajuda
	@echo "Pipeline de Dados em Tempo Real - Comandos Disponíveis"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Constrói todas as imagens Docker
	docker-compose build

up: ## Inicia todos os serviços
	docker-compose up -d
	@echo "Aguardando serviços iniciarem..."
	@sleep 10
	@echo "Dashboard disponível em: http://localhost:5000"

down: ## Para todos os serviços
	docker-compose down

stop: ## Para todos os serviços (sem remover containers)
	docker-compose stop

restart: ## Reinicia todos os serviços
	docker-compose restart

logs: ## Mostra logs de todos os serviços
	docker-compose logs -f

logs-producer: ## Mostra logs do producer
	docker-compose logs -f producer

logs-consumer: ## Mostra logs do consumer
	docker-compose logs -f consumer

logs-dashboard: ## Mostra logs do dashboard
	docker-compose logs -f dashboard

status: ## Mostra status dos serviços
	docker-compose ps

clean: ## Remove containers, volumes e imagens
	docker-compose down -v
	docker system prune -f

clean-all: ## Remove tudo incluindo imagens
	docker-compose down -v --rmi all
	docker system prune -af

install: ## Instala dependências Python localmente
	pip install -r requirements.txt

dev: ## Inicia apenas infraestrutura (para desenvolvimento local)
	docker-compose up -d zookeeper kafka postgres
	@echo "Infraestrutura iniciada. Execute os scripts Python localmente."

test: ## Executa testes
	pytest tests/ -v --cov=src --cov-report=term-missing

test-coverage: ## Executa testes com relatório de cobertura HTML
	pytest tests/ -v --cov=src --cov-report=html
	@echo "Relatório gerado em htmlcov/index.html"

db-shell: ## Acessa shell do PostgreSQL
	docker-compose exec postgres psql -U admin -d pipeline_db

db-backup: ## Faz backup do banco de dados
	docker-compose exec postgres pg_dump -U admin pipeline_db > backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "Backup criado: backup_$$(date +%Y%m%d_%H%M%S).sql"

db-restore: ## Restaura backup do banco (uso: make db-restore FILE=backup.sql)
	@if [ -z "$(FILE)" ]; then \
		echo "Erro: especifique o arquivo com FILE=backup.sql"; \
		exit 1; \
	fi
	docker-compose exec -T postgres psql -U admin pipeline_db < $(FILE)
	@echo "Backup restaurado"

kafka-topics: ## Lista tópicos Kafka
	docker-compose exec kafka kafka-topics --bootstrap-server localhost:9092 --list

kafka-describe: ## Descreve tópico (uso: make kafka-describe TOPIC=ecommerce-events)
	docker-compose exec kafka kafka-topics --bootstrap-server localhost:9092 --describe --topic $(TOPIC)

kafka-consumer-groups: ## Lista grupos de consumidores
	docker-compose exec kafka kafka-consumer-groups --bootstrap-server localhost:9092 --list

kafka-lag: ## Mostra lag dos consumers
	docker-compose exec kafka kafka-consumer-groups --bootstrap-server localhost:9092 --group ecommerce-consumer-group --describe

scale-producer: ## Escala producers (uso: make scale-producer N=3)
	docker-compose up -d --scale producer=$(N)
	@echo "Producers escalados para $(N) instâncias"

scale-consumer: ## Escala consumers (uso: make scale-consumer N=3)
	docker-compose up -d --scale consumer=$(N)
	@echo "Consumers escalados para $(N) instâncias"

monitoring: ## Mostra uso de recursos dos containers
	docker stats

health: ## Verifica saúde do dashboard
	@curl -s http://localhost:5000/health | python -m json.tool

quick-start: build up ## Build e start rápido
	@echo "Pipeline iniciado com sucesso!"
	@echo "Dashboard: http://localhost:5000"

demo: ## Demonstração completa do pipeline
	@echo "Iniciando demonstração..."
	@make up
	@echo "\n Aguardando dados serem gerados (30s)..."
	@sleep 30
	@echo "\nAbrindo dashboard..."
	@open http://localhost:5000 || xdg-open http://localhost:5000 || echo "Abra: http://localhost:5000"
	@echo "\nDemonstração pronta! Pressione Ctrl+C para parar e execute 'make down'"
