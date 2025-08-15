import face_recognition
import cv2
import psycopg2
import json
import numpy as np
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

def carregar_dados_banco(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT nome, idade, profissao, projeto, imagem_referencia FROM pessoas")
    registros = cursor.fetchall()
    cursor.close()

    rostos_conhecidos = []
    nomes = []
    dados_pessoas = {}

    for nome, idade, profissao, projeto, imagem_bytes in registros:
        if imagem_bytes:
            temp_path = f"temp_{nome}.jpg"
            with open(temp_path, "wb") as temp_file:
                temp_file.write(imagem_bytes)

            imagem = face_recognition.load_image_file(temp_path)
            encoding = face_recognition.face_encodings(imagem)

            os.remove(temp_path)

            if encoding:
                rostos_conhecidos.append(encoding[0])
                nomes.append(nome)

        dados_pessoas[nome] = {
            "idade": idade,
            "profissao": profissao,
            "projeto": projeto
        }

    return rostos_conhecidos, nomes, dados_pessoas


rostos_conhecidos, nomes, dados_pessoas = carregar_dados_banco(conn)

video_capture = cv2.VideoCapture(0)

while True:
    ret, frame = video_capture.read()
    if not ret:
        break

    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = small_frame[:, :, ::-1]

    locais = face_recognition.face_locations(rgb_small_frame)
    encodings = face_recognition.face_encodings(rgb_small_frame, locais)

    for (top, right, bottom, left), face_encoding in zip(locais, encodings):
        distances = face_recognition.face_distance(rostos_conhecidos, face_encoding)
        min_distance = min(distances) if distances.size > 0 else 1.0
        tolerance = 0.6

        if min_distance < tolerance:
            index = distances.tolist().index(min_distance)
            nome = nomes[index]
        else:
            nome = "Desconhecido"

        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        info = dados_pessoas.get(nome, {"idade": "-", "profissao": "-", "projeto": "-"})

        cv2.putText(frame, f"Nome: {nome}", (right + 15, top + 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"Idade: {info['idade']}", (right + 15, top + 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"Profissao: {info['profissao']}", (right + 15, top + 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"Projeto: {info['projeto']}", (right + 15, top + 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    cv2.imshow("Reconhecimento Facial com Banco de Dados", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

video_capture.release()
cv2.destroyAllWindows()
conn.close()
