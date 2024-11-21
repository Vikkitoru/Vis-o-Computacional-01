import math
import cv2
import mediapipe as mp
import pyautogui
import time

# Classe para calcular distâncias
class CalculadoraDistancia:
    @staticmethod
    def calcular_2d(ponto1, ponto2):
        """
        Calcula a distância 2D entre dois pontos.
        :param ponto1: Coordenadas (x, y) do primeiro ponto.
        :param ponto2: Coordenadas (x, y) do segundo ponto.
        :return: Distância em unidades normalizadas.
        """
        return math.sqrt((ponto2[0] - ponto1[0])**2 + (ponto2[1] - ponto1[1])**2)

# Classe para representar um dedo
class Dedo:
    def __init__(self, nome, ponta, dobradiça, metacarpo):
        self.nome = nome
        self.ponta = ponta
        self.dobradiça = dobradiça
        self.metacarpo = metacarpo

    def distancia_para(self, outro_ponto, ponto_referido="ponta"):
        """
        Calcula a distância 2D entre o ponto referido do dedo e outro ponto.
        :param outro_ponto: Coordenadas (x, y) do outro ponto.
        :param ponto_referido: O ponto do dedo a ser usado para o cálculo ("ponta", "dobradiça" ou "metacarpo").
        :return: Distância em unidades normalizadas.
        """
        pontos = {
            "ponta": (self.ponta.x, self.ponta.y),
            "dobradiça": (self.dobradiça.x, self.dobradiça.y),
            "metacarpo": (self.metacarpo.x, self.metacarpo.y)
        }
        
        if ponto_referido not in pontos:
            raise ValueError(f"Ponto referido '{ponto_referido}' não é válido. Use 'ponta', 'dobradiça' ou 'metacarpo'.")

        ponto_atual = pontos[ponto_referido]
        return CalculadoraDistancia.calcular_2d(ponto_atual, outro_ponto)

# Classe para representar uma mão com seus dedos
class Mao:
    def __init__(self, hand_landmarks):
        self.polegar = Dedo(
            "Polegar",
            hand_landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_CMC],
            hand_landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_MCP],
            hand_landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_IP],
            hand_landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_TIP]
        )
        self.indicador = Dedo(
            "Indicador",
            hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_MCP],
            hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_PIP],
            hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_DIP],
            hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP]
        )
        self.medio = Dedo(
            "Médio",
            hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_MCP],
            hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_PIP],
            hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_DIP],
            hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_TIP]
        )
        self.anelar = Dedo(
            "Anelar",
            hand_landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_MCP],
            hand_landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_PIP],
            hand_landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_DIP],
            hand_landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_TIP]
        )
        self.mindinho = Dedo(
            "Mindinho",
            hand_landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_MCP],
            hand_landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_PIP],
            hand_landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_DIP],
            hand_landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_TIP]
        )


# Configurações do MediaPipe
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

cap = cv2.VideoCapture(0)

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
              
                # Calculando a distância entre a ponta do indicador e a ponta do polegar
                distancia_1 = mao.indicador.distancia_para((mao.polegar.ponta.x, mao.polegar.ponta.y), "ponta")
                distancia_1 = round(distancia_1 * 100, 1)

                distancia_2 = mao.medio.distancia_para((mao.indicador.ponta.x, mao.indicador.ponta.y), "ponta")
                distancia_2 = round(distancia_2 * 100, 1)
                
                ref = 4.5
                # Exibe a distância no console
                print(f"\nDistância entre a ponta do indicador e do polegar: {distancia_1} unidades.")
                print(f"\nDistância entre a ponta do dedo médio e do indicador: {distancia_2} unidades.")
                if (distancia_1 * distancia_2) < pow(ref, 2):
                    print("Pinça dupla fechada!")
                elif distancia_1 < pow(ref, 1):
                    pyautogui.hotkey('ctrl', 'alt', 't')
                    time.sleep(1)
                    print("Pinça simples fechada!")
                


        cv2.imshow('MediaPipe Hands', image)

        if cv2.waitKey(5) & 0xFF == 27:
            break

cap.release()
