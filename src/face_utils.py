import face_recognition
import cv2
import numpy as np

# Carregar a imagem do seu rosto e aprender o encoding
imagem_referencia = face_recognition.load_image_file("foto_pedro.jpeg")
encoding_referencia = face_recognition.face_encodings(imagem_referencia)[0]

# Lista com os rostos conhecidos e nomes
rostos_conhecidos = [encoding_referencia]
nomes = ["Pedro Henrique"]  # Coloque seu nome ou o que quiser

# Dicionário com informações para cada pessoa
dados_pessoas = {
    "Pedro Henrique": {
        "idade": "27",
        "profissao": "Engenheiro",
        "projeto": "Educacional"
    },
    "Desconhecido": {
        "idade": "-",
        "profissao": "-",
        "projeto": "-"
    }
}

# Abrir webcam
video_capture = cv2.VideoCapture(0)

while True:
    ret, frame = video_capture.read()
    if not ret:
        break

    # Reduzir tamanho para acelerar (opcional)
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = small_frame[:, :, ::-1]  # BGR -> RGB

    # Encontrar locais e encodings dos rostos no frame atual
    locais = face_recognition.face_locations(rgb_small_frame)
    encodings = face_recognition.face_encodings(rgb_small_frame, locais)

    for (top, right, bottom, left), face_encoding in zip(locais, encodings):
        # Calcular as distâncias para os rostos conhecidos
        distances = face_recognition.face_distance(rostos_conhecidos, face_encoding)
        min_distance = min(distances) if len(distances) > 0 else 1.0  # distância alta se não tiver

        # Definir tolerância (limite para considerar o rosto conhecido)
        tolerance = 0.5

        if min_distance < tolerance:
            index = distances.tolist().index(min_distance)
            nome = nomes[index]
        else:
            nome = "Desconhecido"

        # Escalar posições de volta para o tamanho original da imagem
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Desenhar retângulo ao redor do rosto
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

        # Card simples: retângulo e texto ao lado do rosto
        card_x1 = right + 10
        card_y1 = top
        card_x2 = card_x1 + 200
        card_y2 = bottom

        # Fundo do card (retângulo sólido)
        cv2.rectangle(frame, (card_x1, card_y1), (card_x2, card_y2), (50, 50, 50), cv2.FILLED)

        # Pega as informações para o nome reconhecido
        info = dados_pessoas.get(nome, dados_pessoas["Desconhecido"])

        # Texto no card
        cv2.putText(frame, f"Nome: {nome}", (card_x1 + 10, card_y1 + 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Idade: {info['idade']}", (card_x1 + 10, card_y1 + 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Profissao: {info['profissao']}", (card_x1 + 10, card_y1 + 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Projeto: {info['projeto']}", (card_x1 + 10, card_y1 + 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    # Mostrar frame
    cv2.imshow("Reconhecimento Facial com Card", frame)

    # Pressione 'q' para sair
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Liberar tudo
video_capture.release()
cv2.destroyAllWindows()
