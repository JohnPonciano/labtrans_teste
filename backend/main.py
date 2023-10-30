from collections import defaultdict
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
# FIX COOOORS GOD WHY
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

# Função para calcular a distância em KM usando Shapely
def calculate_distance(longitudes, latitudes):
    if len(longitudes) != len(latitudes):
        raise ValueError("Os arrays de longitude e latitude devem ter o mesmo tamanho")

    # Criando um objeto LineString a partir dos pontos de latitude e longitude
    line = geometry.LineString(list(zip(longitudes, latitudes)))

    # Armazenando as distâncias normalizadas em uma lista
    normalized_distances = [line.project(geometry.Point(lon, lat), normalized=True) for lon, lat in zip(longitudes, latitudes)]

    # Calculando o comprimento total da linha em unidades de longitude/latitude
    total_length = line.length

    # Calculando as distâncias em quilômetros multiplicando as distâncias normalizadas pelo comprimento total da linha
    distances_in_km = [normalized_distance * total_length for normalized_distance in normalized_distances]

    # Arredondando a distância para o valor mais próximo
    distances = sum(round(distance) for distance in distances_in_km) / 1000
    return distances



def populate_results_table():
    highways = Highway.select(Highway.highway).distinct()

    # Iterar sobre as rodovias
    for highway in highways:
        results = Highway.select().where(Highway.highway == highway.highway)

        # Inicializar contadores para os tipos de itens por rodovia
        item_counts = defaultdict(int)

        # Iterar sobre os dados para contar as ocorrências por tipo de item
        for row in results:
            if row.item == "Buraco":
                item_counts["buraco"] += 1
            elif row.item == "Remendo":
                item_counts["remendo"] += 1
            elif row.item == "Trinca":
                item_counts["trinca"] += 1
            elif row.item in ["Placa", "Faixa Central" , "Faixa Lateral"]:
                item_counts["placa"] += 1
            elif row.item in ["Drenagem", "Rocada"]:
                item_counts["drenagem"] += 1

        # Armazenar os novos dados na tabela Results
        print("Armazenando novos dados no banco!")
        Results.create(
            highway=highway.highway,
            buraco=item_counts["buraco"],
            remendo=item_counts["remendo"],
            trinca=item_counts["trinca"],
            placa=item_counts["placa"],
            drenagem=item_counts["drenagem"],
            created_at=datetime.now()
        )

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

    data_by_km_exp = defaultdict(lambda: defaultdict(int))  # Dicionário para contar itens por km_exp

    # Iterar sobre os dados para contar as ocorrências por km_exp
    for row in data:
        km_exp = row.exp_km_calc
        if row.item == "Buraco":
            data_by_km_exp[km_exp]["buraco"] += 1
        elif row.item == "Remendo":
            data_by_km_exp[km_exp]["remendo"] += 1
        elif row.item == "Trinca":
            data_by_km_exp[km_exp]["trinca"] += 1
        elif row.item in ["Placa", "Faixa Central","Faixa Lateral"]:
            data_by_km_exp[km_exp]["placa"] += 1
        elif row.item in ["Drenagem", "Rocada"]:
            data_by_km_exp[km_exp]["drenagem"] += 1

    # Preparar os dados para escrita no arquivo CSV
    output_data = []
    for km_exp, item_counts in data_by_km_exp.items():
        output_data.append({
            "highway": highway,
            "Km": km_exp,
            "buraco": item_counts["buraco"],
            "remendo": item_counts["remendo"],
            "trinca": item_counts["trinca"],
            "placa": item_counts["placa"],
            "drenagem": item_counts["drenagem"]
        })

    # Nome do arquivo CSV
    filename = f"export/Result_{datetime.now():%Y_%m}_highway_{highway}.csv"
    
    # Escrever os dados no arquivo CSV
    with open(filename, "w", newline="") as csvfile:
        fieldnames = output_data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_data)

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
            elif row.item == "Placa" or row.item == "Faixa Central" or row.item == "Faixa Lateral":
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
        "longitude": longitudes,
        "latitudes": latitudes
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

# Rota para retornar todas as linhas da tabela Highway
@app.get("/all-rows")
async def get_all_rows():

    # Consulta para obter todas as linhas da tabela Highway
    all_rows = Highway.select()

    # Converter os resultados em um formato adequado para retorno
    rows_list = [
        {
            "highway": row.highway,
            "UF": row.UF,
            "item": row.item,
            "latitude": row.latitude,
            "longitude": row.longitude,
            "exp_km_calc": row.exp_km_calc,
            'id': row.id
        }
        for row in all_rows
    ]

    return {"all_rows": rows_list}

@app.get("/all-rows/{highway}")
async def get_all_rows_by_highway(highway: str):
    # Consulta para obter todas as linhas da tabela Highway com base na estrada específica
    all_rows = Highway.select().where(Highway.highway == highway)

    # Converter os resultados em um formato adequado para retorno
    rows_list = [
        {
            "highway": row.highway,
            "UF": row.UF,
            "item": row.item,
            "latitude": row.latitude,
            "longitude": row.longitude,
            "exp_km_calc": row.exp_km_calc,
            "id": row.id
        }
        for row in all_rows
    ]

    return {"all_rows": rows_list}

@app.get("/point/{id}")
async def get_point_by_id(id: int):
    all_rows = Highway.select().where(Highway.id == id)

    rows_list = [
        {
            "highway": row.highway,
            "UF": row.UF,
            "item": row.item,
            "latitude": row.latitude,
            "longitude": row.longitude,
            "exp_km_calc": row.exp_km_calc,
            "id": row.id
        }
        for row in all_rows
    ]

    return {
        'point': rows_list
    }

# Endpoint para editar latitude e longitude de um ponto por ID
@app.put("/point/{id}")
async def update_point_by_id(id: int, latitude: float, longitude: float):

    try:
        db.connect()
        query = Highway.update(latitude=latitude, longitude=longitude).where(Highway.id == id)
        query.execute()

        return {"message": "Latitude e Longitude atualizados com sucesso"}

    except Exception as e:
        return {"error": f"Erro ao atualizar Latitude e Longitude: {e}"}

    finally:
        if not db.is_closed():
            db.close()

# Endpoint para deletar um ponto por ID
@app.delete("/point/{id}")
async def delete_point_by_id(id: int):

    try:
        db.connect()
        query = Highway.delete().where(Highway.id == id)
        query.execute()

        return {"message": "Ponto deletado com sucesso"}

    except Exception as e:
        return {"error": f"Erro ao deletar o ponto: {e}"}

    finally:
        if not db.is_closed():
            db.close()
            
if __name__ == "__main__":
    import uvicorn
    from models import create_tables_if_not_exist
    
    # Chame essa função para criar as tabelas se elas não existirem
    create_tables_if_not_exist()

    uvicorn.run(app, host="0.0.0.0", port=8000)
