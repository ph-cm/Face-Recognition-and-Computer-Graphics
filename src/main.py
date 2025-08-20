import cv2
import face_recognition
import mediapipe as mp
import psycopg2
import json
import numpy as np
import os

# ------------------------------
# Configuração do banco
# ------------------------------
with open("config.json", "r") as f:
    config = json.load(f)

conn = psycopg2.connect(
    host=config["db_host"],
    port=config["db_port"],
    database=config["db_name"],
    user=config["db_user"],
    password=config["db_pass"]
)

# ------------------------------
# Carregar dados do banco
# ------------------------------
def carregar_dados_banco(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT nome, idade, profissao, projeto, imagem_referencia FROM pessoas")
    registros = cursor.fetchall()
    cursor.close()

    rostos_conhecidos = []
    nomes = []
    dados_pessoas = {}
    fotos_perfil = {}

    for nome, idade, profissao, projeto, imagem_bytes in registros:
        if imagem_bytes:
            temp_path = f"temp_{nome}.jpg"
            with open(temp_path, "wb") as temp_file:
                temp_file.write(imagem_bytes)

            imagem = face_recognition.load_image_file(temp_path)
            encoding = face_recognition.face_encodings(imagem)
            foto_cv = cv2.imread(temp_path)

            os.remove(temp_path)

            if encoding:
                rostos_conhecidos.append(encoding[0])
                nomes.append(nome)
                fotos_perfil[nome] = foto_cv

        dados_pessoas[nome] = {
            "idade": idade,
            "profissao": profissao,
            "projeto": projeto
        }

    return rostos_conhecidos, nomes, dados_pessoas, fotos_perfil


rostos_conhecidos, nomes, dados_pessoas, fotos_perfil = carregar_dados_banco(conn)

# ------------------------------
# Inicializa captura de vídeo
# ------------------------------
video_capture = cv2.VideoCapture(0)
mp_face_detection = mp.solutions.face_detection

# ------------------------------
# Loop principal
# ------------------------------
with mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.6) as face_detection:
    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_detection.process(rgb_frame)

        if results.detections:
            for detection in results.detections:
                bboxC = detection.location_data.relative_bounding_box
                h, w, _ = frame.shape
                x, y, w_box, h_box = int(bboxC.xmin * w), int(bboxC.ymin * h), \
                                     int(bboxC.width * w), int(bboxC.height * h)

                # Recorte do rosto
                face_crop = rgb_frame[y:y+h_box, x:x+w_box]
                nome = "Desconhecido"

                encodings = face_recognition.face_encodings(face_crop)
                if encodings:
                    face_encoding = encodings[0]
                    distances = face_recognition.face_distance(rostos_conhecidos, face_encoding)
                    min_distance = min(distances) if distances.size > 0 else 1.0
                    if min_distance < 0.6:
                        index = distances.tolist().index(min_distance)
                        nome = nomes[index]

                # Retângulo no rosto
                cv2.rectangle(frame, (x, y), (x+w_box, y+h_box), (0, 255, 0), 2)

                # Dados da pessoa
                info = dados_pessoas.get(nome, {"idade": "-", "profissao": "-", "projeto": "-"})
                card_x, card_y = x + w_box + 15, y
                card_w, card_h = 260, 130

                # Fundo translúcido
                overlay = frame.copy()
                cv2.rectangle(overlay, (card_x, card_y),
                              (card_x + card_w, card_y + card_h),
                              (40, 40, 40), -1)
                frame = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)

                # Foto de perfil no card (miniatura)
                if nome in fotos_perfil:
                    foto = fotos_perfil[nome]
                    foto = cv2.resize(foto, (60, 60))

                    # Coordenadas da área do card para a foto
                    y1, y2 = card_y + 10, card_y + 70
                    x1, x2 = card_x + 10, card_x + 70

                    # Garante que está dentro do frame
                    if y2 <= frame.shape[0] and x2 <= frame.shape[1]:
                        frame[y1:y2, x1:x2] = foto


                # Texto no card
                cv2.putText(frame, f"Nome: {nome}", (card_x+80, card_y+35),
                            cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)
                cv2.putText(frame, f"Idade: {info['idade']}", (card_x+80, card_y+60),
                            cv2.FONT_HERSHEY_DUPLEX, 0.6, (200, 200, 200), 1)
                cv2.putText(frame, f"Profissao: {info['profissao']}", (card_x+80, card_y+85),
                            cv2.FONT_HERSHEY_DUPLEX, 0.6, (200, 200, 200), 1)
                cv2.putText(frame, f"Projeto: {info['projeto']}", (card_x+10, card_y+110),
                            cv2.FONT_HERSHEY_DUPLEX, 0.6, (180, 220, 255), 1)

        cv2.imshow("Reconhecimento Facial com Cards", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

video_capture.release()
cv2.destroyAllWindows()
conn.close()
