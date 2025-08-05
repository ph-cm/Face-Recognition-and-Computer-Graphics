# Face-Recognition-and-Computer-Graphics

# Reconhecimento Facial com Informações (Face Cards)
Este projeto usa **visão computacional** e **reconhecimento facial** em tempo real para identificar pessoas conhecidas a partir de uma webcam, exibindo dinamicamente um "card" com suas informações ao lado do rosto detectado.

## Conceito
A ideia é utilizar a biblioteca `face_recognition`para:
  - Detectar rostos em tempo real via webcam
  - Comparar com uma base de rostos conhecidos
  - Exibir um "Card de Informações" personalizadas para cada pessoa conhecida
  - Quando um rosto nao for reconhecido, exibir um card com valores padrão

### Requisitos
 - Python3.7+
 - OpenCV(`cv2`)
 - face_recognition
 - dlib(dependencia do `face_recognition`)

## Funcionamento

### 1-Carregamento do rosto de referência
```python
imagem_referencia = face_recognition.load_image_file("foto_pedro.jpeg")
encoding_referencia = face_recognition.face_encodings(imagem_referencia)[0]
```
Carrega a imagem `foto_pedro.jpeg`, obtendo seu encoding facial(vetor de caracteristicas unicas

### 2-Dados associados ao rosto
```python
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
```
Cada rosto conhecido pode ter dados personalizados que serão exibidos dinamicamente no card.

### 3- Captura da webcam e reconhecimento
````python
video_capture = cv2.VideoCapture(0)
````

Laço principal:
  - Captura frame da webcam
  - Reduz tamanho para acelerar o processamento
  - Detecta rostos e calcula encodings
  - Compara com o rosto conhecido
  - Se for similar(abaixo da tolerancia 0.5), exibe nome e dados
  - Caso contrario, exibe "Desconhecido"

### 4- Exibição gráfica
  - Um retangulo verde é desenhado ao redor do rosto detectado
  - Ao lado, um card cinza exibe as informações textuais
    ````makefile
    Nome: Pedro Henrique
    Idade: 27
    Profissão: Engenheiro
    Projeto: Educacional
    ````
  - Tudo isso é mostrado em tempo real via `cv2.imshow`

## Possiveis expanções/atualizações
  - Suporte a multiplos rostos conhecidos.
  - Integração com banco de dados
  - Registro de presença ou tempo de reconhecimento
  - Detecção em vídeos pré-gravados ou via camera IP.
  - Interface gráfica(GUI com Tkinter ou PyQt
  - Integração com óculos de RA(Realidade Aumentada).



