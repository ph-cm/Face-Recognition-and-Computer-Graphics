import psycopg2
import json
import os

# Ler configs do banco
with open("config.json", "r") as f:
    config = json.load(f)

# Conectar ao banco
conn = psycopg2.connect(
    host=config["db_host"],
    port=config["db_port"],
    database=config["db_name"],
    user=config["db_user"],
    password=config["db_pass"]
)
cursor = conn.cursor()

# === Entradas do usuário ===
nome = input("Nome: ")
idade = int(input("Idade: "))
profissao = input("Profissão: ")
projeto = input("Projeto: ")
caminho_imagem = input("Caminho da imagem: ")

# Verificar se arquivo existe
if not os.path.exists(caminho_imagem):
    print("❌ Arquivo de imagem não encontrado!")
    conn.close()
    exit()

# Ler imagem
with open(caminho_imagem, "rb") as f:
    imagem_bytes = f.read()

# Inserir no banco
cursor.execute("""
    INSERT INTO pessoas (nome, idade, profissao, projeto, imagem_referencia)
    VALUES (%s, %s, %s, %s, %s)
""", (nome, idade, profissao, projeto, psycopg2.Binary(imagem_bytes)))

conn.commit()
cursor.close()
conn.close()
print("✅ Pessoa inserida com sucesso!")
