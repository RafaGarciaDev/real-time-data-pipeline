# 🚀 Guia de Início Rápido

Este guia irá ajudá-lo a executar o pipeline de dados em tempo real em menos de 5 minutos!

## Pré-requisitos

Certifique-se de ter instalado:
- Docker Desktop (ou Docker Engine + Docker Compose)
- 4GB de RAM disponível
- 2GB de espaço em disco

## Passo a Passo

### 1. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/real-time-data-pipeline.git
cd real-time-data-pipeline
```

### 2. Inicie os Serviços

```bash
docker-compose up -d
```

Isso irá iniciar:
- Zookeeper (gerenciamento Kafka)
- Kafka (message broker)
- PostgreSQL (banco de dados)
- Producer (gerador de eventos)
- Consumer (processador de eventos)
- Dashboard (visualização web)

### 3. Aguarde a Inicialização

Os serviços levam cerca de 30-60 segundos para inicializar completamente.

Verifique o status:
```bash
docker-compose ps
```

Todos os serviços devem estar com status "Up".

### 4. Acesse o Dashboard

Abra seu navegador e acesse:
```
http://localhost:5000
```

Você verá o dashboard com métricas em tempo real!

## Verificando os Logs

Para ver o que está acontecendo:

```bash
# Todos os serviços
docker-compose logs -f

# Apenas o producer
docker-compose logs -f producer

# Apenas o consumer
docker-compose logs -f consumer
```

## Comandos Úteis

### Parar o Pipeline

```bash
docker-compose down
```

### Reiniciar Tudo (limpar dados)

```bash
docker-compose down -v
docker-compose up -d
```

### Acessar o Banco de Dados

```bash
docker-compose exec postgres psql -U admin -d pipeline_db
```

Queries úteis:
```sql
-- Total de eventos
SELECT COUNT(*) FROM events;

-- Produtos mais vendidos
SELECT * FROM top_products;

-- Vendas por categoria
SELECT * FROM sales_by_category;
```

### Escalar o Producer

Para gerar mais eventos:

```bash
docker-compose up -d --scale producer=3
```

## Troubleshooting

### O dashboard não carrega

1. Verifique se todos os containers estão rodando:
   ```bash
   docker-compose ps
   ```

2. Verifique os logs do dashboard:
   ```bash
   docker-compose logs dashboard
   ```

### Sem dados no dashboard

Aguarde alguns minutos para que eventos sejam gerados e processados.

Verifique se o producer está gerando eventos:
```bash
docker-compose logs producer | tail -20
```

### Erro de conexão com Kafka

Kafka pode levar até 60 segundos para estar pronto. Aguarde e reinicie:
```bash
docker-compose restart producer consumer
```

## Próximos Passos

Agora que seu pipeline está rodando, você pode:

1. **Personalizar os eventos**: Edite `src/producer.py` para gerar eventos customizados
2. **Adicionar processamento**: Modifique `src/consumer.py` para transformações de dados
3. **Criar novos gráficos**: Customize `templates/index.html` com visualizações personalizadas
4. **Integrar com APIs externas**: Adicione webhooks ou APIs no consumer
5. **Implementar alertas**: Configure notificações quando métricas ultrapassarem limites

## Recursos Adicionais

- [Documentação do Kafka](https://kafka.apache.org/documentation/)
- [Kafka-Python Docs](https://kafka-python.readthedocs.io/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [Flask Docs](https://flask.palletsprojects.com/)
- [Plotly Docs](https://plotly.com/python/)

## Ajuda

Se encontrar problemas, abra uma issue no GitHub com:
- Saída do `docker-compose ps`
- Logs relevantes
- Descrição do problema

Boa sorte! 🎉
