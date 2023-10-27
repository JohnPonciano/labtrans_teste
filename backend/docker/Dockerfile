# Use a imagem oficial do PostgreSQL
FROM postgres:13

# Defina variáveis de ambiente para o PostgreSQL
ENV POSTGRES_DB=mydatabase
ENV POSTGRES_USER=myuser
ENV POSTGRES_PASSWORD=mypassword

# Exponha a porta padrão do PostgreSQL (5432)
EXPOSE 5432

# Copie o script SQL para o diretório /docker-entrypoint-initdb.d/
COPY init.sql /docker-entrypoint-initdb.d/

