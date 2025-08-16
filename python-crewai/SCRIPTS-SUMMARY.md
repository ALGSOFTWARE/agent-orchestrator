# Scripts de Execução - MIT Tracking

📋 **Resumo completo** de todos os scripts disponíveis para executar o sistema MIT Tracking.

---

## 🚀 Scripts Principais

### 1. `./start-complete.sh` ⭐ **RECOMENDADO**
**O que faz:** Inicia **sistema completo** em Docker
```bash
./start-complete.sh
```

**Serviços inclusos:**
- ✅ **Ollama LLM** (porta 11434)
- ✅ **GraphQL API** (porta 8000) 
- ✅ **Agente Interativo CLI** (attach disponível)

**Endpoints disponíveis:**
- `http://localhost:8000/graphql` - GraphQL Playground
- `http://localhost:8000/docs` - API Documentation  
- `http://localhost:8000/health` - Health Check

**Quando usar:** Primeira execução ou quando quiser tudo funcionando

---

### 2. `./start-api.sh` 
**O que faz:** Inicia apenas **API GraphQL** em Docker
```bash
./start-api.sh
```

**Serviços inclusos:**
- ✅ **Ollama LLM** (porta 11434)
- ✅ **GraphQL API** (porta 8000)
- ❌ Sem agente CLI interativo

**Quando usar:** Apenas desenvolvimento de API ou integração externa

---

### 3. `./start-api-local.sh`
**O que faz:** Inicia **API local** (desenvolvimento)
```bash 
./start-api-local.sh
```

**Como funciona:**
- Cria ambiente virtual Python
- Instala dependências
- Roda API em http://127.0.0.1:8000
- Ollama opcional (pode rodar sem)

**Quando usar:** Desenvolvimento local da API

---

### 4. `./stop-all.sh`
**O que faz:** Para **todos os serviços** MIT Tracking
```bash
./stop-all.sh
```

**O que para:**
- Todos containers MIT (API, Ollama, Agent)
- Remove containers órfãos
- Opção de limpeza completa (volumes/images)

**Quando usar:** Para limpar tudo e começar do zero

---

## 🔧 Scripts de Apoio

### `python main.py`
**Agente CLI tradicional** (sem API)
- Execução direta do agente conversacional
- Requer Ollama rodando separadamente  
- Interface comando de linha tradicional

### Scripts Legados (backup-js-ts/)
- Scripts originais JavaScript/TypeScript
- Preservados para referência
- Não recomendados para uso atual

---

## 📊 Matriz de Decisão

| Cenário | Script Recomendado | Porquê |
|---------|-------------------|---------|
| **Primeira vez usando** | `./start-complete.sh` | Tudo funcionando de uma vez |
| **Desenvolvimento API** | `./start-api.sh` | Só o necessário para API |
| **Debug local** | `./start-api-local.sh` | Desenvolvimento com reload |
| **Usar só agente** | `python main.py` | CLI tradicional |
| **Testar tudo** | `./start-complete.sh` | Sistema completo |
| **Limpar bagunça** | `./stop-all.sh` | Reset completo |

---

## 🌐 Endpoints por Script

### start-complete.sh
```
✅ http://localhost:8000/graphql      # GraphQL Playground
✅ http://localhost:8000/docs         # API Docs  
✅ http://localhost:8000/health       # Health Check
✅ docker attach mit-agent            # CLI Agent
```

### start-api.sh  
```
✅ http://localhost:8000/graphql      # GraphQL Playground
✅ http://localhost:8000/docs         # API Docs
✅ http://localhost:8000/health       # Health Check
❌ No CLI Agent
```

### start-api-local.sh
```
✅ http://127.0.0.1:8000/graphql      # GraphQL Playground Local
✅ http://127.0.0.1:8000/docs         # API Docs Local
✅ http://127.0.0.1:8000/health       # Health Check Local
❌ No CLI Agent (use python main.py separado)
```

---

## 🚨 Troubleshooting

### "Docker não está rodando"
```bash
# Iniciar Docker primeiro
sudo systemctl start docker  # Linux
# ou iniciar Docker Desktop
```

### "Porta 8000 já está em uso"
```bash
# Ver que está usando a porta
sudo lsof -i :8000

# Parar tudo MIT primeiro
./stop-all.sh
```

### "Ollama não responde"
```bash
# Verificar logs
docker logs mit-ollama

# Restart apenas Ollama
docker restart mit-ollama
```

### "API não carrega"
```bash
# Ver logs da API
docker logs -f mit-api

# Health check manual
curl http://localhost:8000/health
```

---

## 🎯 Fluxo Recomendado

### Primera Execução
```bash
1. git clone [repo]
2. cd MIT/python-crewai  
3. ./start-complete.sh
4. Aguardar inicialização
5. Testar http://localhost:8000/graphql
6. Opcional: docker attach mit-agent
```

### Desenvolvimento
```bash
1. ./start-api-local.sh    # API local com reload
2. Fazer mudanças
3. Testar em http://127.0.0.1:8000
4. Commit mudanças
```

### Deploy/Teste Completo
```bash
1. ./stop-all.sh           # Limpar ambiente
2. ./start-complete.sh     # Sistema completo
3. Testar todos endpoints
4. docker logs -f mit-api  # Monitorar
```

---

## 📋 Checklist de Funcionamento

Após executar `./start-complete.sh`:

- [ ] GraphQL Playground carrega: http://localhost:8000/graphql
- [ ] API Docs disponível: http://localhost:8000/docs  
- [ ] Health check OK: http://localhost:8000/health
- [ ] Query teste funciona: `{ ctes { numero_cte } }`
- [ ] Agent CLI responde: `docker attach mit-agent`
- [ ] Logs sem erros: `docker logs mit-api`

**Se todos ✅ = Sistema funcionando perfeitamente! 🚀**

---

## 💡 Dicas

- **Use `start-complete.sh`** para demonstrações
- **Use `start-api.sh`** para desenvolvimento focado em API  
- **Use `stop-all.sh`** sempre que algo der errado
- **Logs são seus amigos:** `docker logs -f [container]`
- **Health check é confiável:** sempre verifique `/health`

🎉 **Sistema pronto para uso e desenvolvimento!**