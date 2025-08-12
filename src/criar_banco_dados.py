import sqlite3

conn = sqlite3.connect("pessoas.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS pessoas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT UNIQUE,
    idade TEXT,
    profissao TEXT,
    projeto TEXT,
    imagem_referencia TEXT
)
""")

cursor.execute("""
INSERT OR REPLACE INTO pessoas (nome, idade, profissao, projeto, imagem_referencia)
VALUES (?, ?, ?, ?, ?)
""", ("Pedro Henrique", "22", "Engenheiro", "Computacao Grafica", "foto_pedro.jpeg"))

cursor.execute("""
INSERT OR REPLACE INTO pessoas (nome, idade, profissao, projeto, imagem_referencia)
VALUES (?, ?, ?, ?, ?)
""", ("Desconhecido", "-", "-", "-", ""))

conn.commit()
conn.close()

print("Banco pessoas.db criado e populado com sucesso!")
