# Git Subtree Guide - MIT Project

Este guia explica como usar Git Subtree para gerenciar módulos independentes no projeto MIT.

## Configuração Atual

### Repositórios Configurados:
- **Projeto Principal:** MIT Logistics System
- **Frontend React:** https://github.com/ALGSOFTWARE/logistic-pulse-frontend-
- **Gatekeeper API:** https://github.com/ALGSOFTWARE/mit-gatekeeper-api
- **CrewAI Agents:** https://github.com/ALGSOFTWARE/mit-crewai-agents
- **Next.js Frontend:** https://github.com/ALGSOFTWARE/mit-nextjs-frontend

### SSH Keys Configuradas:
- **Pessoal:** `~/.ssh/id_ed25519` para `narradorww`
- **ALGSOFTWARE:** `~/.ssh/id_ed25519_algsoftware` para `dev@algsoftware.online`

## Como Usar o Subtree

### 1. Para desenvolver em qualquer módulo:

**Frontend React (logistic-pulse-31-main):**
```bash
cd /home/narrador/Projetos/MIT/logistic-pulse-31-main
npm run dev  # Porta 8080
```

**Gatekeeper API (gatekeeper-api):**
```bash
cd /home/narrador/Projetos/MIT/gatekeeper-api
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python app/main.py
```

**CrewAI Agents (python-crewai):**
```bash
cd /home/narrador/Projetos/MIT/python-crewai
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python api/main.py
```

**Next.js Frontend (frontend):**
```bash
cd /home/narrador/Projetos/MIT/frontend
npm install
npm run dev
```

### 2. Para sincronizar com o repositório independente:

**Opção A: Push direto para cada módulo (recomendada)**
```bash
# ===== FRONTEND REACT =====
cd /tmp
git clone git@github.com-algsoftware:ALGSOFTWARE/logistic-pulse-frontend-.git
cd logistic-pulse-frontend-
cp -r /home/narrador/Projetos/MIT/logistic-pulse-31-main/* .
git add . && git commit -m "sync: update from main project" && git push

# ===== GATEKEEPER API =====
cd /tmp
git clone git@github.com-algsoftware:ALGSOFTWARE/mit-gatekeeper-api.git
cd mit-gatekeeper-api
cp -r /home/narrador/Projetos/MIT/gatekeeper-api/* .
rm -f .env && rm -rf venv/ && find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
git add . && git commit -m "sync: update from main project" && git push

# ===== CREWAI AGENTS =====
cd /tmp
git clone git@github.com-algsoftware:ALGSOFTWARE/mit-crewai-agents.git
cd mit-crewai-agents
cp -r /home/narrador/Projetos/MIT/python-crewai/* .
rm -f .env* && rm -rf venv/ && find . -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
git add . && git commit -m "sync: update from main project" && git push

# ===== NEXT.JS FRONTEND =====
cd /tmp
git clone git@github.com-algsoftware:ALGSOFTWARE/mit-nextjs-frontend.git
cd mit-nextjs-frontend
cp -r /home/narrador/Projetos/MIT/frontend/* .
rm -rf node_modules/ .next/
git add . && git commit -m "sync: update from main project" && git push
```

**Opção B: Subtree (quando funcionar)**
```bash
cd /home/narrador/Projetos/MIT
# Primeiro fazer pull das mudanças remotas (se houver)
git subtree pull --prefix=logistic-pulse-31-main logistic-pulse-frontend main --squash

# Depois fazer push das suas mudanças
git subtree push --prefix=logistic-pulse-31-main logistic-pulse-frontend main
```

### 3. Para colaboração:

**Desenvolver direto no repo independente:**
```bash
git clone git@github.com-algsoftware:ALGSOFTWARE/logistic-pulse-frontend-.git
cd logistic-pulse-frontend-
# Desenvolver normalmente
npm install
npm run dev
```

**Trazer mudanças de volta para o projeto principal:**
```bash
cd /home/narrador/Projetos/MIT
git subtree pull --prefix=logistic-pulse-31-main logistic-pulse-frontend main --squash
```

## Comandos Úteis

### Verificar configuração:
```bash
# Ver remotes configurados
git remote -v

# Ver chaves SSH
ssh-add -l

# Testar conexão SSH
ssh -T git@github.com-algsoftware
```

### SSH Config (já configurado):
```
# ~/.ssh/config
Host github.com-algsoftware
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_algsoftware
```

## Vantagens desta Configuração

1. **✅ Desenvolvimento Independent:** O frontend pode ser desenvolvido separadamente
2. **✅ Histórico Preservado:** Ambos os repositórios mantêm histórico completo  
3. **✅ Flexibilidade:** Pode ser usado em outros projetos
4. **✅ Colaboração:** Times diferentes podem trabalhar no frontend
5. **✅ Deploy Independent:** Frontend pode ter CI/CD próprio

## Próximos Módulos

Pode aplicar a mesma estratégia para:
- `gatekeeper-api/` → `ALGSOFTWARE/mit-gatekeeper-api`
- `python-crewai/` → `ALGSOFTWARE/mit-crewai-agents`  
- `frontend/` → `ALGSOFTWARE/mit-nextjs-frontend`

## Troubleshooting

**Se o subtree push falhar:**
- Use a Opção A (push direto) como alternativa
- Conflitos podem acontecer se houver mudanças simultâneas

**Se SSH falhar:**
- Verificar se a chave pública foi adicionada no GitHub
- Testar conexão: `ssh -T git@github.com-algsoftware`