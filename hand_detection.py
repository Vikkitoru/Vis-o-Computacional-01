import math
import cv2
import mediapipe as mp
import pyautogui
from time import sleep
import webbrowser
from datetime import datetime


# Classe para calcular distâncias
class CalculadoraDistancia:
    @staticmethod
    def calcular_2d(ponto1, ponto2):
        return math.sqrt((ponto2[0] - ponto1[0])**2 + (ponto2[1] - ponto1[1])**2)


# Classe para representar um dedo
class Dedo:
    def __init__(self, nome, ponta, dobradiça, articulacao, metacarpo):
        self.nome = nome
        self.ponta = ponta
        self.dobradiça = dobradiça
        self.articulacao = articulacao
        self.metacarpo = metacarpo


# Classe para representar uma mão com seus dedos
class Mao:
    def __init__(self, hand_landmarks):
        self.polegar = Dedo(
            "Polegar",
            hand_landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_TIP],
            hand_landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_IP],
            hand_landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_MCP],
            hand_landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_CMC]
        )
        self.indicador = Dedo(
            "Indicador",
            hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP],
            hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_DIP],
            hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_PIP],
            hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_MCP]
        )
        self.medio = Dedo(
            "Médio",
            hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_TIP],
            hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_DIP],
            hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_PIP],
            hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_MCP]
        )
        self.mindinho = Dedo(
            "Mindinho",
            hand_landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_TIP],
            hand_landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_DIP],
            hand_landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_PIP],
            hand_landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_MCP]
        )
        
        # Determina se a mão é esquerda ou direita com base na posição do pulso (wrist)
        self.tipo = self.determinar_tipo_mao(hand_landmarks)

    def determinar_tipo_mao(self, hand_landmarks):
        wrist_x = hand_landmarks.landmark[mp.solutions.hands.HandLandmark.WRIST].x
        if wrist_x > 0.5:  # Se o pulso estiver mais à direita da imagem
            return "Direita"
        else:  # Caso contrário, é a mão esquerda
            return "Esquerda"

    def polegar_fechado(self):
        # Calcula a distância entre a dobradiça do polegar e a dobradiça do mindinho
        dist_polegar_mindinho = CalculadoraDistancia.calcular_2d(
            (self.polegar.ponta.x, self.polegar.ponta.y),
            (self.mindinho.dobradiça.x, self.mindinho.dobradiça.y)
        )
        return dist_polegar_mindinho < 0.05  # Ajuste conforme necessário

    def dedos_levantados(self):
        # Retorna um dicionário indicando se os dedos estão levantados ou não
        dedos_levantados = {
            "polegar": CalculadoraDistancia.calcular_2d(
                (self.polegar.ponta.x, self.polegar.ponta.y),
                (self.polegar.metacarpo.x, self.polegar.metacarpo.y)
            ) > 0.09,  # Defina um valor mínimo para considerar o dedo levantado
            "indicador": CalculadoraDistancia.calcular_2d(
                (self.indicador.ponta.x, self.indicador.ponta.y),
                (self.indicador.metacarpo.x, self.indicador.metacarpo.y)
            ) > 0.09,
            "medio": CalculadoraDistancia.calcular_2d(
                (self.medio.ponta.x, self.medio.ponta.y),
                (self.medio.metacarpo.x, self.medio.metacarpo.y)
            ) > 0.09,
            "anelar": CalculadoraDistancia.calcular_2d(
                (self.anelar.ponta.x, self.anelar.ponta.y),
                (self.anelar.metacarpo.x, self.anelar.metacarpo.y)
            ) > 0.09,
            "mindinho": CalculadoraDistancia.calcular_2d(
                (self.mindinho.ponta.x, self.mindinho.ponta.y),
                (self.mindinho.metacarpo.x, self.mindinho.metacarpo.y)
            ) > 0.09
        }
        return dedos_levantados


# Função para abrir URLs
def abrir_site(url):
    webbrowser.open(url)


# Função para obter a data e hora atuais
def obter_data_hora():
    now = datetime.now()
    print(f"Data e Hora formatadas: {now.strftime('%d/%m/%Y %H:%M:%S')}")
    return now.strftime("%d/%m/%Y %H:%M:%S")


# Configurações do MediaPipe
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

cap = cv2.VideoCapture(1)

# Variável para controlar o estado do polegar
polegar_esta_fechado = False

with mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.9,
    min_tracking_confidence=0.9 ) as hands:

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        image = cv2.flip(image, 1)
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image)

        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())

                mao = Mao(hand_landmarks)

                distancia_minima = 0.05
                # Verifica se a mão é a esquerda antes de executar os comandos
                if mao.tipo == "Esquerda":  # Só realiza as ações para a mão esquerda
                    # Detecta o movimento de pinça polegar-indicador para abrir o Trello
                    
                    dist_polegar_indicador = CalculadoraDistancia.calcular_2d(
                        (mao.polegar.ponta.x, mao.polegar.ponta.y),
                        (mao.indicador.ponta.x, mao.indicador.ponta.y)
                    )
                    if dist_polegar_indicador < distancia_minima:
                        print("Movimento de pinça com polegar e indicador detectado. Abrindo Trello.")
                        abrir_site("https://trello.com/b/XHNZaytY/teste-de-produtividade")
                        sleep(3)

                    # Detecta o movimento de pinça polegar-médio para fechar a aba
                    dist_polegar_medio = CalculadoraDistancia.calcular_2d(
                        (mao.polegar.ponta.x, mao.polegar.ponta.y),
                        (mao.medio.ponta.x, mao.medio.ponta.y)
                    )
                    if dist_polegar_medio < distancia_minima:
                        print("Movimento de pinça com polegar e médio detectado. Fechando aba.")
                        pyautogui.hotkey("ctrl", "w")
                        sleep(3)

                # Verifica se a mão é a direita antes de executar os comandos
                elif mao.tipo == "Direita":  # Só realiza as ações para a mão direita
                    # Detecta o movimento de pinça polegar-indicador para abrir o Trello
                    dist_polegar_indicador = CalculadoraDistancia.calcular_2d(
                        (mao.polegar.ponta.x, mao.polegar.ponta.y),
                        (mao.indicador.ponta.x, mao.indicador.ponta.y)
                    )
                    if dist_polegar_indicador < distancia_minima:
                        print("Movimento de pinça com polegar e indicador da mão direita detectado. Criando novo documento.")
                        pyautogui.hotkey("n")
                        sleep(1)

                    # Detecta o movimento de pinça polegar-médio para escrever nova atividade
                    dist_polegar_medio = CalculadoraDistancia.calcular_2d(
                        (mao.polegar.ponta.x, mao.polegar.ponta.y),
                        (mao.medio.ponta.x, mao.medio.ponta.y)
                    )
                    if dist_polegar_medio < distancia_minima:
                        print("Movimento de pinça com polegar e médio da mão direita detectado. Escrevendo nova atividade.")
                        pyautogui.write(f"Nova atividade - {obter_data_hora()}")
                        pyautogui.press('enter')
                        sleep(1)

        cv2.imshow('MediaPipe Hands', image)

        if cv2.waitKey(1) & 0xFF == 27:  # 27 é o código ASCII para a tecla Esc
            break

cap.release()
cv2.destroyAllWindows()