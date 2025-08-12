import os

db_path = "pessoas.db"  # caminho do banco

if os.path.exists(db_path):
    os.remove(db_path)
    print(f"Banco '{db_path}' deletado com sucesso.")
else:
    print(f"O arquivo '{db_path}' não existe.")
