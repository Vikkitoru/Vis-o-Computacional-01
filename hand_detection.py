import math
import cv2
import mediapipe as mp
import pyautogui
import calculo_tangente

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
        
    def obter_ponta(self):
        return (self.ponta.x, self.ponta.y)

# Classe para representar uma mão com seus dedos
class Mao:
    def __init__(self, hand_landmarks):
        self.dedos = {
            "Polegar": Dedo(
                "Polegar",
                hand_landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_TIP],
                hand_landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_IP],
                hand_landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_MCP],
                hand_landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_CMC]
            ),
            "Indicador": Dedo(
                "Indicador",
                hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP],
                hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_DIP],
                hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_PIP],
                hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_MCP]
            ),
            "Médio": Dedo(
                "Médio",
                hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_TIP],
                hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_DIP],
                hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_PIP],
                hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_MCP]
            ),
            "Anelar": Dedo(
                "Anelar",
                hand_landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_TIP],
                hand_landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_DIP],
                hand_landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_PIP],
                hand_landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_MCP]
            ),
            "Mindinho": Dedo(
                "Mindinho",
                hand_landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_TIP],
                hand_landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_DIP],
                hand_landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_PIP],
                hand_landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_MCP]
            )
        }

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

                h, w, _ = image.shape
                dedos = list(mao.dedos.values())
                todas_tangentes_menores_30 = True

                # Calcula a tangente entre as pontas de cada par de dedos
                for i, dedo1 in enumerate(dedos):
                    for j, dedo2 in enumerate(dedos):
                        if i < j:  # Evita combinações repetidas
                            ponto1 = dedo1.obter_ponta()
                            ponto2 = dedo2.obter_ponta()

                            tangente_result = calculo_tangente.tg_by_2_points(ponto1, ponto2)
                            tg_theta, ponto1, ponto2, ref = tangente_result

                            # Converte a tangente para graus
                            angulo_graus = tg_theta

                            # Checa se alguma tangente não cumpre a condição
                            if angulo_graus >= 30:
                                todas_tangentes_menores_30 = False

                            # Desenha o triângulo
                            cv2.line(image, (int(ponto1[0] * w), int(ponto1[1] * h)), (int(ponto2[0] * w), int(ponto2[1] * h)), (0, 255, 0), 1)
                            cv2.line(image, (int(ponto1[0] * w), int(ponto1[1] * h)), (int(ref[0] * w), int(ref[1] * h)), (255, 0, 0), 1)
                            cv2.line(image, (int(ponto2[0] * w), int(ponto2[1] * h)), (int(ref[0] * w), int(ref[1] * h)), (0, 0, 255), 1)

                # Se todas as tangentes forem < 30, aperta ESC
                if todas_tangentes_menores_30:
                    print("Todas as tangentes estão abaixo de 30 graus. Pressionando ESC.")
                    pyautogui.press('esc')

        cv2.imshow('MediaPipe Hands', image)

        if cv2.waitKey(5) & 0xFF == 27:
            break

cap.release()
