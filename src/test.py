import face_recognition
import cv2

# Inicia a câmera
video_capture = cv2.VideoCapture(0)

while True:
    # Captura frame por frame
    ret, frame = video_capture.read()

    # Converte de BGR (OpenCV) para RGB (face_recognition)
    rgb_frame = frame[:, :, ::-1]

    # Localiza rostos no frame
    face_locations = face_recognition.face_locations(rgb_frame)

    # Desenha um retângulo ao redor de cada rosto detectado
    for top, right, bottom, left in face_locations:
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

    # Exibe o resultado
    cv2.imshow('Reconhecimento Facial', frame)

    # Sai com 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libera a câmera e fecha janelas
video_capture.release()
cv2.destroyAllWindows()
