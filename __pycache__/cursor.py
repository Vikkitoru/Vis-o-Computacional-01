import pyautogui
import time

print("Posicione o mouse sobre o cartão 'A fazer' e aguarde...")
time.sleep(3)  # Dê 3 segundos para se posicionar

# Pega a posição atual do mouse
x, y = pyautogui.position()

print(f"Coordenadas do mouse: {x}, {y}")
