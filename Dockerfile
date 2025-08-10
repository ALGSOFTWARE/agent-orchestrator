# MIT Tracking - CrewAI Agent with Ollama
FROM node:22-slim

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos de dependências
COPY package*.json ./

# Instala as dependências
RUN npm install --only=production

# Copia o código da aplicação
COPY . .

# Expõe a porta (se necessário para futuras funcionalidades web)
EXPOSE 3000

# Define variáveis de ambiente para container
ENV NODE_ENV=production
ENV OLLAMA_BASE_URL=http://host.docker.internal:11434
ENV OLLAMA_MODEL=mistral

# Adiciona usuário não-root para segurança
RUN groupadd -r mittracking && useradd -r -g mittracking -s /bin/false mittracking
RUN chown -R mittracking:mittracking /app
USER mittracking

# Health check para verificar se o container está funcionando
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD node --version || exit 1

# Comando para executar a aplicação
CMD ["node", "index.js"]