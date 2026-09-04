#!/usr/bin/python3
import math
import sys

def help():
    print("É necessário informar o raio do círculo.")
    print("Sintaxe {} <raio>".format(sys.argv[0][2:]))

def calculo_area_circulo(raio):
    return math.pi * float(raio) ** 2

if __name__ == '__main__':
    if len(sys.argv) < 2:
        help()
        sys.exit(1)
    else:
        raio = sys.argv[1]
        calculo = calculo_area_circulo(raio)
        print(f"Área do circulo: {calculo}")

