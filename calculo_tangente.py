import math

def tg_by_2_points(p1, p2):
    ref = (p2[0], p1[1])  # Ponto de referência no triângulo retângulo
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = ref

    # Definindo vetores A e B
    A = (x2 - x1, y2 - y1)
    B = (x3 - x1, y3 - y1)
    
    # Produto escalar de A e B
    produto_escalar = A[0] * B[0] + A[1] * B[1]
    
    # Magnitudes dos vetores
    magnitude_A = math.sqrt(A[0]**2 + A[1]**2)
    magnitude_B = math.sqrt(B[0]**2 + B[1]**2)
    
    # Cálculo de cos(theta) e sen(theta)
    cos_theta = produto_escalar / (magnitude_A * magnitude_B)
    sen_theta = math.sqrt(1 - (cos_theta)**2)
    
    # Tangente de theta
    tg_theta = sen_theta / cos_theta

    # Calcula o ângulo em radianos e converte para graus
    angulo_em_radianos = math.atan(tg_theta)
    angulo_em_graus = math.degrees(angulo_em_radianos)

    return angulo_em_graus, p1, p2, ref
