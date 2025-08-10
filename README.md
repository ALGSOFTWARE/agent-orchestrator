# MIT Tracking - Agente Conversacional de Logística

🤖 Agente de IA especializado em consultas logísticas usando CrewAI e Ollama local

---

## 🇧🇷 Português

### 📋 Sobre o Projeto
MIT Tracking é um agente conversacional inteligente especializado em logística, focado em:
- **CT-e (Conhecimento de Transporte Eletrônico)** - Consultas por número
- **Rastreamento de Containers** - Status em tempo real
- **BL (Bill of Lading)** - Conhecimentos de embarque
- **ETA/ETD** - Previsões de chegada e saída

### 🛠 Tecnologias
- Node.js 22 (ESM)
- CrewAI + Langchain
- Ollama (Mistral local)
- Docker

### 🚀 Como Executar

#### Pré-requisitos
```bash
# 1. Instalar Ollama
ollama serve
ollama pull mistral
```

#### Método 1: Docker (Recomendado)
```bash
# Build e execução
docker build -t crewai-ollama .
docker run -it --rm crewai-ollama
```

#### Método 2: Local
```bash
# Instalar dependências
npm install

# Executar versão interativa (recomendado)
npm start
# ou
npm run interactive

# Executar apenas demonstração
npm run demo
```

### 💬 Como Interagir com o Agente

Após executar `npm start`, você terá acesso a uma interface interativa:

```bash
👤 Você: [Digite sua pergunta aqui]
🤖 MIT Tracking: [Resposta do agente]
```

#### Comandos Especiais:
- `/menu` - Mostrar menu de comandos
- `/exemplos` - Ver exemplos de consultas
- `/limpar` - Limpar histórico da conversa
- `/sair` - Encerrar o programa

#### Exemplos de Consultas:
- "Onde está o meu BL?"
- "Me mostre o CT-e da carga X"
- "CT-e número 351234567890123456789012345678901234"
- "Qual o status da minha entrega?"
- "Como consultar ETA de um container?"
- "Quais documentos preciso para rastreamento?"

---

## 🇺🇸 English

### 📋 About the Project
MIT Tracking is an intelligent conversational agent specialized in logistics, focused on:
- **CT-e (Electronic Transport Document)** - Queries by number
- **Container Tracking** - Real-time status
- **BL (Bill of Lading)** - Shipping documents
- **ETA/ETD** - Arrival and departure predictions

### 🛠 Technologies
- Node.js 22 (ESM)
- CrewAI + Langchain  
- Ollama (Local Mistral)
- Docker

### 🚀 How to Run

#### Prerequisites
```bash
# 1. Install Ollama
ollama serve
ollama pull mistral
```

#### Method 1: Docker (Recommended)
```bash
# Build and run
docker build -t crewai-ollama .
docker run -it --rm crewai-ollama
```

#### Method 2: Local
```bash
# Install dependencies
npm install

# Run interactive version (recommended)
npm start
# or
npm run interactive

# Run demo only
npm run demo
```

### 💬 How to Interact with the Agent

After running `npm start`, you'll have access to an interactive interface:

```bash
👤 You: [Type your question here]
🤖 MIT Tracking: [Agent response]
```

#### Special Commands:
- `/menu` - Show command menu
- `/exemplos` - Show query examples
- `/limpar` - Clear conversation history
- `/sair` - Exit program

### 💬 Query Examples
- "Where is my BL?"
- "Show me CT-e for cargo X"
- "CT-e number 351234567890123456789012345678901234"
- "What's the status of my delivery?"

---

## 🇫🇷 Français

### 📋 À Propos du Projet
MIT Tracking est un agent conversationnel intelligent spécialisé en logistique, axé sur:
- **CT-e (Document de Transport Électronique)** - Requêtes par numéro
- **Suivi de Conteneurs** - Statut en temps réel
- **BL (Connaissement)** - Documents d'expédition
- **ETA/ETD** - Prévisions d'arrivée et de départ

### 🛠 Technologies
- Node.js 22 (ESM)
- CrewAI + Langchain
- Ollama (Mistral local)
- Docker

### 🚀 Comment Exécuter

#### Prérequis
```bash
# 1. Installer Ollama
ollama serve
ollama pull mistral
```

#### Méthode 1: Docker (Recommandé)
```bash
# Build et exécution
docker build -t crewai-ollama .
docker run -it --rm crewai-ollama
```

#### Méthode 2: Local
```bash
# Installer les dépendances
npm install

# Exécuter version interactive (recommandé)
npm start
# ou
npm run interactive

# Exécuter démo seulement
npm run demo

# Exécuter tests
npm test
```

## 🧪 Tests / Testes / Testes

O projeto inclui uma suíte completa de testes unitários e de integração:

```bash
# Executar todos os testes / Run all tests / Exécuter tous les tests
npm test

# Relatório de cobertura / Coverage report / Rapport de couverture
npm run test:coverage

# Modo watch / Watch mode / Mode surveillance
npm run test:watch

# Saída detalhada / Verbose output / Sortie détaillée
npm run test:verbose
```

### Tipos de Teste / Test Types / Types de Tests:
- **Testes Unitários / Unit Tests / Tests Unitaires**: Componentes individuais
- **Testes de Integração / Integration Tests / Tests d'Intégration**: Conexão com Ollama
- **Testes de Interface / Interface Tests / Tests d'Interface**: Comandos e interações
- **Smoke Tests**: Verificações básicas de configuração

### 💬 Comment Interagir avec l'Agent

Après avoir exécuté `npm start`, vous aurez accès à une interface interactive:

```bash
👤 Vous: [Tapez votre question ici]
🤖 MIT Tracking: [Réponse de l'agent]
```

#### Commandes Spéciales:
- `/menu` - Afficher le menu des commandes
- `/exemplos` - Voir exemples de requêtes
- `/limpar` - Effacer l'historique de conversation
- `/sair` - Quitter le programme

### 💬 Exemples de Requêtes
- "Où est mon BL?"
- "Montrez-moi le CT-e pour la cargaison X"
- "CT-e numéro 351234567890123456789012345678901234"
- "Quel est le statut de ma livraison?"

---

## 📁 Structure du Projet / Project Structure / Structure du Projet
```
crewai-agent/
├── agents/
│   └── conversationalAgent.js    # Agente logístico / Logistics agent / Agent logistique
├── index.js                      # Entrada principal / Main entry / Entrée principale
├── .env                          # Configurações / Config / Configuration
├── Dockerfile                    # Container Node.js 22
├── .dockerignore                 # Docker exclusions
└── package.json                  # Dependencies / Dépendances
```

## 🔧 Solução de Problemas / Troubleshooting / Dépannage

### Erro de Conexão Ollama / Ollama Connection Error / Erreur de Connexion Ollama
```bash
# Verificar se Ollama está rodando / Check if Ollama is running / Vérifier si Ollama fonctionne
ollama serve

# Verificar modelo instalado / Check installed model / Vérifier le modèle installé
ollama list

# Reinstalar modelo se necessário / Reinstall model if needed / Réinstaller le modèle si nécessaire
ollama pull mistral
```

## 📄 Licença / License / Licence
MIT
