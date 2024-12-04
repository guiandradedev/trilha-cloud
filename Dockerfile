# Etapa 1: Imagem base 
FROM python:3.9-slim 

# Etapa 2: Definir diretório de trabalho 
WORKDIR /app 

# Etapa 3: Copiar arquivos 
COPY . /app 

# Etapa 4: Instalar dependências 
RUN pip install --no-cache-dir -r requirements.txt 

# Etapa 5: Configurar variáveis de ambiente 
ENV FLASK_ENV=production 

# Etapa 6: Expor porta 
EXPOSE 5000 

# Etapa 7: Definir comando de execução 
CMD ["python", "app.py"] 