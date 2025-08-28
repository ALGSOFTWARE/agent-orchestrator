#!/bin/bash

# --- Configuração ---
OUTPUT_MD="documentacao_codigo.md"
OUTPUT_PDF="documentacao_final.pdf"
PROJECT_TITLE="Sistema de Gerenciamento de Documentos MIT"
AUTHOR="Move In Tech"
CITY="São Paulo"
YEAR="2025"
MONTH="Agosto"

# --- Início do Script ---
echo "Gerando documentação de código-fonte para o projeto: $PROJECT_TITLE"

# 1. Limpar arquivos antigos
rm -f "$OUTPUT_MD" "$OUTPUT_PDF"

# 2. Criar o arquivo Markdown com o cabeçalho YAML para o Pandoc
echo "---
title: '$PROJECT_TITLE'
subtitle: 'Documentação de Código-Fonte para Fins de Registro de Software'
author: '$AUTHOR'
date: '$MONTH de $YEAR'
lang: 'pt-BR'
mainfont: 'Liberation Serif'
fontsize: 12pt
papersize: a4
geometry: 'left=3cm,right=2cm,top=3cm,bottom=2cm'
---

\newpage
\tableofcontents
\newpage

" > "$OUTPUT_MD"

echo "Cabeçalho ABNT criado em $OUTPUT_MD"

# 3. Encontrar arquivos e adicionar ao Markdown
echo "Procurando arquivos de código-fonte..."

# Abordagem mais simples: listar tudo e filtrar com grep
find . -type f | grep -vE "(\.git/|node_modules/|venv/|\.next/|__pycache__/|\.pyc$|\.swp$|${OUTPUT_MD}|${OUTPUT_PDF}|gerar_documentacao.sh|\.env)" | while read -r file; do

    # Pular arquivos que não são de texto
    if ! grep -qI "." "$file"; then
        echo "Pulando arquivo binário: $file"
        continue
    fi

    echo "Processando: $file"

    # Determinar a linguagem para syntax highlighting
    lang="text"
    ext="${file##*.}"
    case "$ext" in
        py) lang="python" ;;
        js) lang="javascript" ;;
        ts|tsx) lang="typescript" ;;
        css) lang="css" ;;
        json) lang="json" ;;
        sh) lang="bash" ;;
        yml|yaml) lang="yaml" ;;
        md) lang="markdown" ;;
        Dockerfile) lang="dockerfile" ;;
    esac

    # Adicionar ao arquivo MD
    echo -e "\n\newpage\n" >> "$OUTPUT_MD"
    ESCAPED_FILE=$(echo "$file" | sed 's/_/\\_/g') # Escapa underscores para o LaTeX
    echo "# Arquivo: ${ESCAPED_FILE}" >> "$OUTPUT_MD"
    echo -e "\n\`\`\`$lang" >> "$OUTPUT_MD"
    cat "$file" >> "$OUTPUT_MD"
    echo -e "\n\`\`\`\n" >> "$OUTPUT_MD"
done

FILE_COUNT=$(grep -c "# Arquivo:" "$OUTPUT_MD")
echo "$FILE_COUNT arquivos foram adicionados ao $OUTPUT_MD."

if [ "$FILE_COUNT" -eq 0 ]; then
    echo "ERRO: Nenhum arquivo de código-fonte foi encontrado. Abortando."
    exit 1
fi

# 4. Converter para PDF com Pandoc
echo "Convertendo para PDF com Pandoc... Isso pode levar alguns minutos."
pandoc "$OUTPUT_MD" -o "$OUTPUT_PDF" --from markdown --pdf-engine=xelatex --toc

# 5. Verificar e limpar
if [ -f "$OUTPUT_PDF" ]; then
    echo "SUCESSO! O arquivo '$OUTPUT_PDF' foi criado."
    rm "$OUTPUT_MD"
    echo "Arquivo temporário '$OUTPUT_MD' removido."
else
    echo "ERRO: A conversão para PDF falhou. O arquivo intermediário '$OUTPUT_MD' foi mantido para depuração."
fi
