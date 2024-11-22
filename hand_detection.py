import math
import cv2
import mediapipe as mp
import pyautogui
from time import sleep
# Função para calcular a distância 2D entre dois pontos
def calcular_distancia(p1, p2):
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

# Configurações do MediaPipe
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

cap = cv2.VideoCapture(1)

with mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.75,
    min_tracking_confidence=0.75) as hands:

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

                # Obtenção das coordenadas normalizadas (x, y) da ponta dos dedos e polegar
                h, w, _ = image.shape
                polegar = (hand_landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_TIP].x * w,
                           hand_landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_TIP].y * h)
                indicador = (hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP].x * w,
                             hand_landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP].y * h)
                medio = (hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_TIP].x * w,
                         hand_landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_TIP].y * h)
                anelar = (hand_landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_TIP].x * w,
                          hand_landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_TIP].y * h)

                # Calcula as distâncias entre polegar e outros dedos
                dist_indicador = calcular_distancia(polegar, indicador)
                dist_medio = calcular_distancia(polegar, medio)
                dist_anelar = calcular_distancia(polegar, anelar)

                # Imprime as distâncias
                print(f"Distância Polegar-Indicador: {dist_indicador:.2f}")
                print(f"Distância Polegar-Médio: {dist_medio:.2f}")
                print(f"Distância Polegar-Anelar: {dist_anelar:.2f}")

                # Controle do mouse
                if dist_indicador < 30:
                    pyautogui.move(0, -20)
                    sleep(1)
                if dist_medio < 20:
                    pyautogui.press("Win")
                    sleep(1)
                if dist_anelar < 20:
                    pyautogui.click()  # Clique esquerdo
                    sleep(1)

        cv2.imshow('MediaPipe Hands', image)

        if cv2.waitKey(5) & 0xFF == 27:
            break

cap.release()
