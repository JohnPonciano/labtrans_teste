import csv
import datetime
from operator import itemgetter
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from jinja2 import Environment, FileSystemLoader
from models import Highway, Results, db
from datetime import datetime
import shapely.geometry as geometry
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
env = Environment(loader=FileSystemLoader("templates"))
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Função para listar arquivos exportados

def get_exported_files():

    export_folder = Path("export")
    exported_files = [f.name for f in export_folder.iterdir() if f.is_file()]
    return exported_files


def calculate_distance_on_line_string(longitudes, latitudes):
    if len(longitudes) != len(latitudes):
        raise ValueError(
            "Os arrays de longitude e latitude devem ter o mesmo tamanho")

    # Crie um objeto LineString a partir dos pontos
    line = geometry.LineString(zip(longitudes, latitudes))

    # Projete todos os pontos na LineString e armazene as distâncias normalizadas em uma lista
    normalized_distances = [line.project(geometry.Point(
        lon, lat), normalized=True) for lon, lat in zip(longitudes, latitudes)]

    # Calcule o comprimento total da linha em unidades de longitude/latitude
    total_length = line.length

    # Calcule as distâncias em quilômetros multiplicando as distâncias normalizadas pelo comprimento total da linha
    distances_in_km = [normalized_distance *
                       total_length for normalized_distance in normalized_distances]

    # Arredonde a distância para o valor mais próximo
    rounded_distances = [round(distance) for distance in distances_in_km]
    distances = sum(rounded_distances)
    distances = distances / 1000000
    distances = f"{distances:.1f}"
    distances = float(distances)
    return distances
# Função para preencher a tabela Rodovias com base nos dados da tabela Results


def populate_results_table():
    highways = Highway.select(Highway.highway).distinct()

    # Itere sobre as rodovias
    for highway in highways:
        # Tente obter a entrada existente na tabela Results
        existing_entry = Results.get_or_none(highway=highway.highway)

        # Se a entrada já existe, exclua-a
        if existing_entry:
            existing_entry.delete_instance()

        results = Highway.select().where(Highway.highway == highway.highway)

        # Inicialize contadores para os tipos de itens
        buraco_count = 0
        remendo_count = 0
        trinca_count = 0
        placa_count = 0
        drenagem_count = 0

        # Itere sobre os dados para contar as ocorrências
        for row in results:
            if row.item == "Buraco":
                buraco_count += 1
            elif row.item == "Remendo":
                remendo_count += 1
            elif row.item == "Trinca":
                trinca_count += 1
            elif row.item == "Placa" or row.item == "Faixa Central":
                placa_count += 1
            elif row.item == "Drenagem" or row.item == "Rocada":
                drenagem_count += 1

        # Crie uma nova entrada com os valores atualizados
        print("Armazenando novos dados no banco!")
        Results.create(
            highway=highway.highway,
            buraco=buraco_count,
            remendo=remendo_count,
            trinca=trinca_count,
            placa=placa_count,
            drenagem=drenagem_count,
            created_at=datetime.now()
        )
# Rota para renderizar a página de upload HTML


@app.get("/upload-page")
async def upload_page(request: Request):
    template = env.get_template("upload.html")
    return HTMLResponse(content=template.render())

# Rota para renderizar a página de lista HTML


@app.get("/lista")
async def lista(request: Request):
    template = env.get_template("lista.html")
    files = get_exported_files()
    return HTMLResponse(content=template.render(files=files))

# Rota para fazer upload do CSV inicial


@app.post("/upload-csv/")
async def upload_csv(file: UploadFile):
    try:
        data_folder = Path("uploads")
        data_folder.mkdir(parents=True, exist_ok=True)
        file_path = data_folder / file.filename

        # Informe o status de início do upload
        print("Upload iniciado...")

        with file_path.open("wb") as buffer:
            buffer.write(file.file.read())

        # Informe o status de conclusão do upload
        print("Upload concluído.")

        print("Importando dados para o Banco")
        with db.atomic():
            with open(file_path, newline="") as csvfile:
                reader = csv.DictReader(csvfile)
                rows = list(reader)
                Highway.insert_many(rows).execute()

        # Informe o status de processamento dos dados
        print("Dados importados com sucesso!")

        # Preencha a tabela Rodovias com base nos dados carregados
        populate_results_table()
        # Informe o status de conclusão do processamento
        print("Tabela Rodovias atualizada com sucesso.")

        return {"message": "Dados importados com sucesso!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Rota para listar dados tratados e fazer download por rodovia


@app.get("/export-csv/{highway}")
async def export_csv(highway: int):
    data = Highway.select().where(Highway.highway == highway)

    # Inicialize contadores para os tipos de itens
    buraco_count = 0
    remendo_count = 0
    trinca_count = 0
    placa_count = 0
    drenagem_count = 0
    longitudes = []
    latitudes = []

    # Itere sobre os dados para contar as ocorrências
    for row in data:
        if row.item == "Buraco":
            buraco_count += 1
        elif row.item == "Remendo":
            remendo_count += 1
        elif row.item == "Trinca":
            trinca_count += 1
        elif row.item == "Placa" or row.item == "Faixa Central":
            placa_count += 1
        elif row.item == "Drenagem" or row.item == "Rocada":
            drenagem_count += 1

    for i in range(len(data)):
        latitude = data[i].latitude
        if isinstance(latitude, float):
            latitudes.append(latitude)
        elif isinstance(latitude, str):
            latitude = latitude.replace(".", "").strip()
            latitude = f"{latitude[:-6]}.{latitude[-6:]}"
            latitude = float(latitude)
            latitudes.append(latitude)
        else:
            raise ValueError(
                f"Unexpected type for longitude: {type(latitude)}")

    for i in range(len(data)):
        longitude = data[i].longitude
        if isinstance(longitude, float):
            longitudes.append(longitude)
        elif isinstance(longitude, str):
            longitude = longitude.replace(".", "").strip()
            longitude = f"{longitude[:-6]}.{longitude[-6:]}"
            longitude = float(longitude)
            longitudes.append(longitude)
        else:
            raise ValueError(
                f"Unexpected type for longitude: {type(longitude)}")

    distances = calculate_distance_on_line_string(longitudes, latitudes)

    # Defina os campos do arquivo de saída
    output_data = {
        "highway": highway,
        "km_exp": data[0].exp_km_calc,
        "Km": distances,
        "buraco": buraco_count,
        "remendo": remendo_count,
        "trinca": trinca_count,
        "placa": placa_count,
        "drenagem": drenagem_count  # Adicione +1 em drenagem para o item "Rocada"
    }
    print('Dados Tratados! ')
    print(output_data)
    filename = f"export/Result_{datetime.now():%Y_%m}_highway_{highway}.csv"
    with open(filename, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=output_data.keys())
        writer.writeheader()
        writer.writerow(output_data)

    return FileResponse(filename)

# Rota para listar todas as rodovias disponíveis com contagem de itens


@app.get("/list-highways")
async def list_highways():

    highways = Highway.select(Highway.highway).distinct()
    highway_data = []

    for h in highways:
        data = Highway.select().where(Highway.highway == h.highway)

        # Inicialize contadores para os tipos de itens
        buraco_count = 0
        remendo_count = 0
        trinca_count = 0
        placa_count = 0
        drenagem_count = 0
        longitudes = []
        latitudes = []

        # Itere sobre os dados para contar as ocorrências
        for row in data:
            if row.item == "Buraco":
                buraco_count += 1
            elif row.item == "Remendo":
                remendo_count += 1
            elif row.item == "Trinca":
                trinca_count += 1
            elif row.item == "Placa" or row.item == "Faixa Central":
                placa_count += 1
            elif row.item == "Drenagem" or row.item == "Rocada":
                drenagem_count += 1

        for i in range(len(data)):
            latitude = data[i].latitude
            if isinstance(latitude, float):
                latitudes.append(latitude)
            elif isinstance(latitude, str):
                latitude = latitude.replace(".", "").strip()
                latitude = f"{latitude[:-6]}.{latitude[-6:]}"
                latitude = float(latitude)
                latitudes.append(latitude)
            else:
                raise ValueError(
                    f"Unexpected type for longitude: {type(latitude)}")

        for i in range(len(data)):
            longitude = data[i].longitude
            if isinstance(longitude, float):
                longitudes.append(longitude)
            elif isinstance(longitude, str):
                longitude = longitude.replace(".", "").strip()
                longitude = f"{longitude[:-6]}.{longitude[-6:]}"
                longitude = float(longitude)
                longitudes.append(longitude)
            else:
                raise ValueError(
                    f"Unexpected type for longitude: {type(longitude)}")

        distances = calculate_distance_on_line_string(longitudes, latitudes)
        highway_item_data = {
            "highway": h.highway,
            "Km_exp": data[0].exp_km_calc,
            "Km": distances,
            "buraco": buraco_count,
            "remendo": remendo_count,
            "trinca": trinca_count,
            "placa": placa_count,
            "drenagem": drenagem_count
        }

        highway_data.append(highway_item_data)

    return highway_data

# Rota para listar rodovia especifica


@app.get("/list-highways/{highway}")
async def list_highways(highway: int):

    data = Highway.select().where(Highway.highway == highway)
    highway_data = []
    # Inicialize contadores para os tipos de itens
    buraco_count = 0
    remendo_count = 0
    trinca_count = 0
    placa_count = 0
    drenagem_count = 0
    longitudes = []
    latitudes = []

    # Itere sobre os dados para contar as ocorrências
    for row in data:
        if row.item == "Buraco":
            buraco_count += 1
        elif row.item == "Remendo":
            remendo_count += 1
        elif row.item == "Trinca":
            trinca_count += 1
        elif row.item == "Placa" or row.item == "Faixa Central":
            placa_count += 1
        elif row.item == "Drenagem" or row.item == "Rocada":
            drenagem_count += 1

    for i in range(len(data)):
        latitude = data[i].latitude
        if isinstance(latitude, float):
            latitudes.append(latitude)
        elif isinstance(latitude, str):
            latitude = latitude.replace(".", "").strip()
            latitude = f"{latitude[:-6]}.{latitude[-6:]}"
            latitude = float(latitude)
            latitudes.append(latitude)
        else:
            raise ValueError(
                f"Unexpected type for longitude: {type(latitude)}")

    for i in range(len(data)):
        longitude = data[i].longitude
        if isinstance(longitude, float):
            longitudes.append(longitude)
        elif isinstance(longitude, str):
            longitude = longitude.replace(".", "").strip()
            longitude = f"{longitude[:-6]}.{longitude[-6:]}"
            longitude = float(longitude)
            longitudes.append(longitude)
        else:
            raise ValueError(
                f"Unexpected type for longitude: {type(longitude)}")

    distances = calculate_distance_on_line_string(longitudes, latitudes)

    highway_item_data = {
        "km_exp": data[0].exp_km_calc,
        "Km": distances,
        "highway": highway,
        "buraco": buraco_count,
        "remendo": remendo_count,
        "trinca": trinca_count,
        "placa": placa_count,
        "drenagem": drenagem_count,
    }

    highway_data.append(highway_item_data)

    return highway_data

# Rota para listar todos os arquivos CSV exportados


@app.get("/list-exported-csv")
async def list_exported_csv():
    export_folder = Path("export")
    exported_files = [f.name for f in export_folder.iterdir() if f.is_file()]
    return exported_files

# Rota para encontrar o quilômetro com a maior incidência de um item em uma rodovia


@app.get("/maior-incidencia/{item}")
async def maior_incidencia(item: str):
    try:
        # Consulte o banco de dados para obter os dados da tabela Results.
        results = Results.select().dicts()

        # Inicialize um dicionário para rastrear os valores de incidência para cada highway.
        incidencias = {}

        # Itere sobre os resultados para calcular as incidências para cada highway.
        for result in results:
            if item in result:
                incidencia_item = result[item]
                highway = result['highway']
                incidencias[highway] = incidencia_item

        # Ordene as rodovias com base nos valores de incidência em ordem decrescente.
        rodovias_ordenadas = sorted(
            incidencias.items(), key=itemgetter(1), reverse=True)

        if rodovias_ordenadas:
            return {
                "incidencia": item,
                "rodovias_maior_incidencia": [
                    {
                        "highway": item[0],
                        "incidentes": item[1]
                    }
                    for item in rodovias_ordenadas
                ]

            }
        else:
            return {"message": f"Nenhuma rodovia encontrada com maior incidência do item {item}."}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    from models import create_tables_if_not_exist
    
    # Chame essa função para criar as tabelas se elas não existirem
    create_tables_if_not_exist()

    uvicorn.run(app, host="0.0.0.0", port=8000)
