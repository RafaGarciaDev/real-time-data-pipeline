# 🚀 Pipeline de Dados em Tempo Real

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Kafka](https://img.shields.io/badge/Apache%20Kafka-3.0-black.svg)
![Docker](https://img.shields.io/badge/Docker-Compose-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

Um pipeline de dados em tempo real completo para processamento e análise de streaming de dados, utilizando Apache Kafka, Python, PostgreSQL e visualização em tempo real.

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Arquitetura](#arquitetura)
- [Tecnologias](#tecnologias)
- [Funcionalidades](#funcionalidades)
- [Instalação](#instalação)
- [Uso](#uso)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Monitoramento](#monitoramento)
- [Contribuindo](#contribuindo)
- [Licença](#licença)

## 🎯 Visão Geral

Este projeto demonstra a implementação de um pipeline de dados em tempo real que:

- Gera dados simulados de eventos de e-commerce
- Processa streams de dados usando Apache Kafka
- Armazena dados processados em PostgreSQL
- Visualiza métricas em tempo real via dashboard web
- Monitora a saúde do pipeline

## 🏗️ Arquitetura

```
┌─────────────────┐
│  Data Producer  │ → Gera eventos simulados
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Apache Kafka   │ → Message Broker
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Data Consumer  │ → Processa eventos
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   PostgreSQL    │ → Armazena dados
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Dashboard     │ → Visualiza métricas
└─────────────────┘
```

## 🛠️ Tecnologias

- **Apache Kafka**: Message broker para streaming de dados
- **Python 3.9+**: Linguagem principal
- **PostgreSQL**: Banco de dados relacional
- **Docker & Docker Compose**: Containerização
- **Flask**: Framework web para dashboard
- **Plotly**: Visualização de dados
- **Kafka-Python**: Cliente Kafka para Python

## ✨ Funcionalidades

- ✅ Geração de dados simulados de e-commerce em tempo real
- ✅ Processamento de streams com Apache Kafka
- ✅ Transformação e enriquecimento de dados
- ✅ Persistência em banco de dados relacional
- ✅ Dashboard web interativo com métricas em tempo real
- ✅ Monitoramento de health do pipeline
- ✅ Logs estruturados
- ✅ Tratamento de erros e retry logic
- ✅ Containerização completa com Docker

## 🚀 Instalação

### Pré-requisitos

- Docker e Docker Compose instalados
- Python 3.9+ (para desenvolvimento local)
- 4GB de RAM disponível

### Passos

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/real-time-data-pipeline.git
cd real-time-data-pipeline
```

2. Inicie os serviços com Docker Compose:
```bash
docker-compose up -d
```

3. Aguarde todos os serviços iniciarem (cerca de 30 segundos):
```bash
docker-compose ps
```

4. Acesse o dashboard:
```
http://localhost:5000
```

## 💻 Uso

### Iniciar o Pipeline

```bash
# Iniciar todos os serviços
docker-compose up -d

# Verificar logs
docker-compose logs -f

# Verificar logs de um serviço específico
docker-compose logs -f producer
docker-compose logs -f consumer
```

### Parar o Pipeline

```bash
docker-compose down
```

### Limpar dados e recomeçar

```bash
docker-compose down -v
docker-compose up -d
```

### Desenvolvimento Local

```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Executar producer
python src/producer.py

# Executar consumer
python src/consumer.py

# Executar dashboard
python src/dashboard.py
```

## 📁 Estrutura do Projeto

```
real-time-data-pipeline/
│
├── src/
│   ├── producer.py          # Gerador de dados
│   ├── consumer.py          # Consumidor Kafka
│   ├── dashboard.py         # Dashboard web
│   ├── config.py            # Configurações
│   └── utils.py             # Funções auxiliares
│
├── docker/
│   ├── Dockerfile.producer
│   ├── Dockerfile.consumer
│   └── Dockerfile.dashboard
│
├── sql/
│   └── init.sql             # Schema do banco
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── dashboard.js
│
├── templates/
│   └── index.html           # Template do dashboard
│
├── tests/
│   ├── test_producer.py
│   ├── test_consumer.py
│   └── test_integration.py
│
├── docker-compose.yml       # Orquestração de containers
├── requirements.txt         # Dependências Python
├── .env.example            # Exemplo de variáveis de ambiente
├── .gitignore
├── LICENSE
└── README.md
```

## 📊 Monitoramento

### Métricas Disponíveis

O dashboard exibe as seguintes métricas em tempo real:

- **Total de Eventos**: Número total de eventos processados
- **Eventos por Segundo**: Taxa de throughput
- **Receita Total**: Valor total de transações
- **Produtos Mais Vendidos**: Top 10 produtos
- **Distribuição por Categoria**: Vendas por categoria
- **Timeline de Eventos**: Gráfico temporal

### Health Checks

Verificar saúde dos serviços:

```bash
# Kafka
curl http://localhost:9092

# PostgreSQL
docker-compose exec postgres psql -U admin -d pipeline_db -c "SELECT 1;"

# Dashboard
curl http://localhost:5000/health
```

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Executar com cobertura
pytest --cov=src tests/

# Executar testes específicos
pytest tests/test_producer.py
```

## 🔧 Configuração

Copie o arquivo `.env.example` para `.env` e ajuste as variáveis:

```env
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC=ecommerce-events
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=pipeline_db
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin123
```

## 📈 Melhorias Futuras

- [ ] Implementar Apache Flink para processamento complexo
- [ ] Adicionar Redis para cache
- [ ] Implementar alertas via email/Slack
- [ ] Adicionar autenticação ao dashboard
- [ ] Implementar CDC (Change Data Capture)
- [ ] Adicionar testes de carga
- [ ] Implementar CI/CD com GitHub Actions
- [ ] Adicionar Grafana para métricas avançadas

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👤 Autor

Seu Nome
- GitHub: [@seu-usuario](https://github.com/seu-usuario)
- LinkedIn: [seu-perfil](https://linkedin.com/in/seu-perfil)

## 🙏 Agradecimentos

- Apache Kafka Community
- Docker Community
- Comunidade Python

---

⭐ Se este projeto foi útil, considere dar uma estrela!
