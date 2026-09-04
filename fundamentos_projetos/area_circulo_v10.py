#!/usr/bin/python3
import math
import sys

def calculo_area_circulo(raio):
    return math.pi * float(raio) ** 2

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("É necessário informar o raio do círculo.")
        print("Sintaxe area_circulo <raio>")
    else:
        raio = sys.argv[1]
        calculo = calculo_area_circulo(raio)
        print(f"Área do circulo: {calculo}")

