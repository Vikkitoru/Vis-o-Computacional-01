import math
import cv2
import mediapipe as mp
import pyautogui
import time
import webbrowser  # Para abrir URLs de forma portátil

# Classe para calcular distâncias
class CalculadoraDistancia:
    @staticmethod
    def calcular_2d(ponto1, ponto2):
        return math.sqrt((ponto2[0] - ponto1[0])**2 + (ponto2[1] - ponto1[1])**2)  # Sem arredondamento

# Classe para representar um dedo
class Dedo:
    def __init__(self, nome, ponta, dobradiça, articulacao, metacarpo):
        self.nome = nome
        self.ponta = ponta
        self.dobradiça = dobradiça
        self.articulacao = articulacao
        self.metacarpo = metacarpo
        
    def distancia_para(self, outro_ponto, ponto_referido="ponta"):
        pontos = {
            "ponta": (self.ponta.x, self.ponta.y),
            "dobradiça": (self.dobradiça.x, self.dobradiça.y),
            "metacarpo": (self.metacarpo.x, self.metacarpo.y),
            "articulacao": (self.articulacao.x, self.articulacao.y)
        }
        if ponto_referido not in pontos:
            raise ValueError(f"Ponto referido '{ponto_referido}' não é válido. Use 'ponta', 'dobradiça', 'articulacao' ou 'metacarpo'.")

        ponto_atual = pontos[ponto_referido]
        return CalculadoraDistancia.calcular_2d(ponto_atual, outro_ponto)

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
        self.anelar = Dedo(
            "Anelar",
            hand_landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_TIP],
            hand_landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_DIP],
            hand_landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_PIP],
            hand_landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_MCP]
        )
        self.mindinho = Dedo(
            "Mindinho",
            hand_landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_TIP],
            hand_landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_DIP],
            hand_landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_PIP],
            hand_landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_MCP]
        )

# Função para abrir URLs
def abrir_site(url):
    webbrowser.open(url)

# Configurações do MediaPipe
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

cap = cv2.VideoCapture(1)

with mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.8,
    min_tracking_confidence=0.8) as hands:
    
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

                # Cria uma instância da mão com os dedos
                mao = Mao(hand_landmarks)

                # Obtém as coordenadas das pontas do indicador e do polegar
                ponta_indicador = (mao.indicador.ponta.x, mao.indicador.ponta.y)
                ponta_polegar = (mao.polegar.ponta.x, mao.polegar.ponta.y)
                ponta_medio = (mao.medio.ponta.x, mao.medio.ponta.y)
                ponta_anelar = (mao.anelar.ponta.x, mao.anelar.ponta.y)

                # Calcula a distância entre os dedos
                dist_polegar_indicador = CalculadoraDistancia.calcular_2d(ponta_indicador, ponta_polegar)
                dist_polegar_medio = CalculadoraDistancia.calcular_2d(ponta_medio, ponta_polegar)
                dist_polegar_anelar = CalculadoraDistancia.calcular_2d(ponta_anelar, ponta_polegar)

                # Define uma distância mínima para os gestos
                distancia_minima = 0.02  # Valor lógico para teste

                # Automação com PyAutoGUI
                if dist_polegar_indicador < distancia_minima:
                    print(f"Movimento de pinça: {dist_polegar_indicador}")
                    abrir_site("https://trello.com")

                if dist_polegar_medio < distancia_minima:
                    print(f"Movimento polegar-médio: {dist_polegar_medio}")
                    abrir_site("https://google.com")

        cv2.imshow('MediaPipe Hands', image)

        if cv2.waitKey(5) & 0xFF == 27:
            break

cap.release()
