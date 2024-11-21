import math

def tg_by_2_points (p1, p2):
    ref = (p2[0], p1[1])
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = ref

    # Definindo vetores A e B
    A = (x2 - x1, y2 - y1)
    B = (x3 - x1, y3 - y1)
    
    # Produto escalar de A e B
    produto_escalar = A[0] * B[0] + A[1] * B[1]
    
    # Magnitudes dos vetores
    magnitude_A = math.sqrt(A[0]*2 + A[1]*2)
    magnitude_B = math.sqrt(B[0]*2 + B[1]*2)
    cos_theta = produto_escalar / (magnitude_A * magnitude_B)
    sen_theta = math.sqrt(1 - (cos_theta)**2)
    tg_theta = sen_theta / cos_theta
    
    return tg_theta

# Exemplo de uso
ponto1 = (5, 5)
ponto2 = (0, 0)

tangente = tg_by_2_points(ponto1, ponto2)
tangente = round(tangente,2)
print(f"Tangente de theta: {tangente}")