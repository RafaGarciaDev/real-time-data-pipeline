# 🏗️ Arquitetura do Sistema

## Visão Geral

Este documento descreve a arquitetura técnica do Pipeline de Dados em Tempo Real, detalhando cada componente, suas responsabilidades e como eles interagem.

## Componentes Principais

### 1. Apache Kafka

**Responsabilidade**: Message Broker e Log de Eventos

**Tecnologia**: 
- Kafka 3.5.0
- Zookeeper para coordenação

**Configurações**:
- 1 broker
- Replicação: 1 (single node)
- Partições: Configurável por tópico
- Retention: 7 dias

**Fluxo de Dados**:
```
Producer → Kafka Topic → Consumer(s)
```

### 2. Data Producer

**Responsabilidade**: Gerar eventos simulados de e-commerce

**Tecnologia**: 
- Python 3.9
- kafka-python
- Faker para dados sintéticos

**Tipos de Eventos Gerados**:
1. `page_view` - Visualização de página
2. `add_to_cart` - Adição ao carrinho
3. `remove_from_cart` - Remoção do carrinho
4. `purchase` - Compra realizada
5. `search` - Busca de produtos

**Configurações**:
- Taxa padrão: 2 eventos/segundo
- Sessões de usuário: Mantidas em memória
- Retry logic: 5 tentativas com backoff exponencial

**Estrutura de Evento**:
```json
{
  "event_id": "uuid",
  "event_type": "purchase",
  "timestamp": "2024-01-01T00:00:00",
  "user_id": "USER001",
  "session_id": "uuid",
  "product": {
    "id": "PROD001",
    "name": "Product Name",
    "category": "Electronics",
    "price": 999.99
  },
  "quantity": 1,
  "total_amount": 999.99,
  "payment_method": "credit_card"
}
```

### 3. Data Consumer

**Responsabilidade**: Processar eventos e persistir em banco de dados

**Tecnologia**:
- Python 3.9
- kafka-python
- psycopg2 (PostgreSQL driver)

**Processamento**:
1. Consome mensagens do Kafka
2. Valida estrutura do evento
3. Extrai e normaliza dados
4. Persiste em PostgreSQL
5. Commit de offset

**Otimizações**:
- Batch processing (100 eventos por lote)
- Connection pooling (até 10 conexões)
- Auto-commit de offsets
- Timeout configurável

### 4. PostgreSQL

**Responsabilidade**: Armazenamento persistente de dados

**Tecnologia**: PostgreSQL 15

**Schema**:

```sql
events
├── id (SERIAL)
├── event_id (VARCHAR, UNIQUE)
├── event_type (VARCHAR)
├── timestamp (TIMESTAMP)
├── user_id (VARCHAR)
└── session_id (VARCHAR)

products
├── id (SERIAL)
├── product_id (VARCHAR, UNIQUE)
├── product_name (VARCHAR)
├── category (VARCHAR)
└── price (DECIMAL)

transactions
├── id (SERIAL)
├── transaction_id (VARCHAR, UNIQUE)
├── event_id (FK → events)
├── product_id (FK → products)
├── quantity (INTEGER)
├── total_amount (DECIMAL)
├── payment_method (VARCHAR)
└── timestamp (TIMESTAMP)
```

**Índices**:
- `idx_events_timestamp` - Queries temporais
- `idx_events_user_id` - Análise por usuário
- `idx_transactions_product_id` - Análise de produtos
- `idx_products_category` - Agregações por categoria

**Views Materializadas**:
- `sales_by_category` - Vendas agregadas por categoria
- `top_products` - Produtos mais vendidos
- `daily_metrics` - Métricas diárias

### 5. Dashboard Web

**Responsabilidade**: Visualização em tempo real

**Tecnologia**:
- Flask (Python web framework)
- Plotly.js para gráficos
- HTML/CSS/JavaScript

**APIs REST**:

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/` | GET | Página principal do dashboard |
| `/health` | GET | Health check |
| `/api/metrics/summary` | GET | Métricas resumidas |
| `/api/metrics/timeline` | GET | Série temporal de eventos |
| `/api/metrics/top-products` | GET | Top 10 produtos |
| `/api/metrics/by-category` | GET | Métricas por categoria |
| `/api/metrics/event-types` | GET | Distribuição de tipos |
| `/api/metrics/realtime` | GET | Métricas do último minuto |

**Atualização**:
- Polling a cada 5 segundos
- Gráficos interativos com Plotly
- Responsivo (mobile-friendly)

## Fluxo de Dados Completo

```
┌─────────────┐
│   Producer  │ Gera eventos a 2/s
└──────┬──────┘
       │
       ▼ Kafka Protocol
┌─────────────┐
│    Kafka    │ Armazena em tópico
└──────┬──────┘
       │
       ▼ Consumer Group
┌─────────────┐
│   Consumer  │ Processa em lotes
└──────┬──────┘
       │
       ▼ SQL
┌─────────────┐
│  PostgreSQL │ Persiste dados
└──────┬──────┘
       │
       ▼ REST API
┌─────────────┐
│  Dashboard  │ Visualiza métricas
└─────────────┘
```

## Padrões de Design Utilizados

### 1. Producer-Consumer Pattern
Kafka implementa naturalmente este padrão, permitindo desacoplamento entre produtores e consumidores.

### 2. Connection Pool Pattern
Consumer usa pool de conexões PostgreSQL para melhor performance.

### 3. Batch Processing Pattern
Eventos são processados em lotes para reduzir I/O.

### 4. Retry Pattern
Producer implementa retry com backoff exponencial.

### 5. Health Check Pattern
Todos os serviços expõem endpoints de health check.

## Escalabilidade

### Horizontal Scaling

**Producer**:
```bash
docker-compose up -d --scale producer=3
```
Múltiplos producers podem gerar eventos simultaneamente.

**Consumer**:
```bash
docker-compose up -d --scale consumer=3
```
Kafka distribui partições entre consumers no mesmo grupo.

### Vertical Scaling

- Aumentar recursos de containers
- Ajustar tamanhos de batch
- Aumentar connection pool

### Kafka Partitioning

```python
# Particionar por user_id para manter ordem
producer.send(
    topic='events',
    key=event['user_id'],  # Garante mesma partição
    value=event
)
```

## Monitoramento

### Métricas Coletadas

**Producer**:
- Eventos gerados/segundo
- Latência de envio
- Taxa de erro

**Consumer**:
- Eventos processados/segundo
- Lag do consumer
- Taxa de sucesso

**Database**:
- Conexões ativas
- Query time
- Tamanho da base

### Logging

Todos os componentes usam logging estruturado:

```python
logger.info(
    f"Evento processado: {event_id} | "
    f"Tipo: {event_type} | "
    f"Latência: {latency}ms"
)
```

## Segurança

### Boas Práticas Implementadas

1. **Credenciais**: Via variáveis de ambiente
2. **Network isolation**: Docker network privada
3. **Least privilege**: Usuários de banco com mínimos privilégios
4. **Input validation**: Sanitização de inputs
5. **SQL injection protection**: Prepared statements

### Melhorias Futuras

- [ ] TLS/SSL para Kafka
- [ ] Autenticação JWT no dashboard
- [ ] Encryption at rest para PostgreSQL
- [ ] Rate limiting nas APIs
- [ ] CORS configuration

## Performance

### Benchmarks (Ambiente Local)

| Métrica | Valor |
|---------|-------|
| Throughput Producer | ~2000 eventos/s |
| Throughput Consumer | ~1500 eventos/s |
| Latência E2E | < 100ms (p95) |
| CPU Usage | ~30% (total) |
| Memory Usage | ~2GB (total) |

### Otimizações Aplicadas

1. Batch processing
2. Connection pooling
3. Índices apropriados
4. Prepared statements
5. Async I/O onde possível

## Disaster Recovery

### Backup Strategy

**PostgreSQL**:
```bash
# Backup manual
docker-compose exec postgres pg_dump -U admin pipeline_db > backup.sql

# Restore
docker-compose exec -T postgres psql -U admin pipeline_db < backup.sql
```

**Kafka**:
- Retention de 7 dias
- Replicação (em cluster)

### High Availability

Para produção, considerar:
- Kafka cluster (3+ brokers)
- PostgreSQL replicação (master-slave)
- Load balancer para dashboard
- Container orchestration (Kubernetes)

## Troubleshooting

### Problemas Comuns

**1. Consumer Lag**
```bash
# Verificar lag
docker-compose exec kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --group ecommerce-consumer-group \
  --describe
```

Solução: Aumentar número de consumers

**2. Database Locks**
```sql
-- Verificar locks
SELECT * FROM pg_locks WHERE NOT granted;
```

Solução: Otimizar queries, reduzir batch size

**3. Memory Issues**
```bash
# Verificar uso de memória
docker stats
```

Solução: Ajustar heap size do Kafka/JVM

## Dependências

```
Producer → Kafka
Consumer → Kafka, PostgreSQL
Dashboard → PostgreSQL
Kafka → Zookeeper
```

## Referências

- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [PostgreSQL Best Practices](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [Python Kafka Client](https://kafka-python.readthedocs.io/)
- [Flask Documentation](https://flask.palletsprojects.com/)
