import face_recognition
import cv2
import sqlite3
import os

# Função para carregar dados e encodings do banco
def carregar_dados_banco():
    conn = sqlite3.connect("pessoas.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nome, idade, profissao, projeto, imagem_referencia FROM pessoas")
    registros = cursor.fetchall()
    conn.close()

    rostos_conhecidos = []
    nomes = []
    dados_pessoas = {}

    print("\n=== Debug: Carregando dados do banco ===")
    print(f"Total de registros encontrados: {len(registros)}")

    for nome, idade, profissao, projeto, img_path in registros:
        print(f"\nProcessando registro: {nome}")
        print(f"  Caminho da imagem no banco: {img_path}")

        if img_path and os.path.exists(img_path):
            print("  → Imagem encontrada. Carregando...")
            imagem = face_recognition.load_image_file(img_path)
            encoding = face_recognition.face_encodings(imagem, model="small")
            if encoding:
                rostos_conhecidos.append(encoding[0])
                nomes.append(nome)
                print("  ✅ Encoding gerado com sucesso!")
            else:
                print("  ⚠ Nenhum rosto detectado nessa imagem!")
        else:
            print("  ❌ Imagem não encontrada no caminho informado.")

        dados_pessoas[nome] = {
            "idade": idade,
            "profissao": profissao,
            "projeto": projeto
        }

    print(f"\nTotal de encodings carregados: {len(rostos_conhecidos)}\n")
    return rostos_conhecidos, nomes, dados_pessoas

# Carregar dados do banco
rostos_conhecidos, nomes, dados_pessoas = carregar_dados_banco()

# Iniciar captura de vídeo
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
        min_distance = min(distances) if len(distances) > 0 else 1.0
        tolerance = 0.6

        if min_distance < tolerance:
            index = distances.tolist().index(min_distance)
            nome = nomes[index]
        else:
            nome = "Desconhecido"

        # Escalar para tamanho original
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Desenhar retângulo no rosto
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Card lateral
        card_x1 = right + 10
        card_y1 = top
        card_x2 = card_x1 + 250
        card_y2 = bottom
        cv2.rectangle(frame, (card_x1, card_y1), (card_x2, card_y2), (0, 0, 255), cv2.FILLED)

        # Buscar dados da pessoa
        info = dados_pessoas.get(nome, dados_pessoas["Desconhecido"])

        cv2.putText(frame, f"Nome: {nome}", (card_x1 + 10, card_y1 + 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"Idade: {info['idade']}", (card_x1 + 10, card_y1 + 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"Profissao: {info['profissao']}", (card_x1 + 10, card_y1 + 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(frame, f"Projeto: {info['projeto']}", (card_x1 + 10, card_y1 + 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    cv2.imshow("Reconhecimento Facial com Banco de Dados", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

video_capture.release()
cv2.destroyAllWindows()
