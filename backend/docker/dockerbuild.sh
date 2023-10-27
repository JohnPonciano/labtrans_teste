# Construa a imagem Docker (substitua 'postgres-server' pelo nome da imagem desejada)
docker build -t postgres-server .

# Copie o script SQL para o contêiner
docker cp init.sql postgres-container:/docker-entrypoint-initdb.d/init.sql

# Execute o contêiner
docker run --name postgres-container -e POSTGRES_DB=labtrans_teste -e POSTGRES_USER=admin -e POSTGRES_PASSWORD=admin -p 5432:5432 -d postgres-server
