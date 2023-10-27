from peewee import Model, PostgresqlDatabase, CharField, FloatField, IntegerField, DateTimeField, SqliteDatabase

# db = SqliteDatabase('database.db')

db = PostgresqlDatabase(
    'labtrans_teste',  # Nome do banco de dados
    user='admin',  # Nome de usuário do PostgreSQL
    password='admin',  # Senha do PostgreSQL
    host='localhost',  # Host do PostgreSQL (pode ser 'localhost' se estiver na mesma máquina)
    port=5432  # Porta do PostgreSQL (geralmente 5432)
)

class BaseModel(Model):
    class Meta:
        database = db

class Highway(BaseModel):
    name = CharField()
    highway = IntegerField()
    UF = CharField()
    item = CharField()
    latitude = FloatField()
    longitude = FloatField()
    exp_km_calc = FloatField()

class Results(BaseModel):
    highway = IntegerField(unique=True)
    buraco = IntegerField()
    remendo = IntegerField()
    trinca = IntegerField()
    placa = IntegerField()
    drenagem = IntegerField()
    created_at = DateTimeField()

def create_tables_if_not_exist():
    tables = [Highway, Results]
    print('Tabelas foram atualizadas')
    db.connect()
    
    for table in tables:
        if not table.table_exists():
            db.create_tables([table])
    
    db.close()
# Chame essa função para criar as tabelas se elas não existirem
create_tables_if_not_exist()

