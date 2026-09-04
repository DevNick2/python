#!/usr/bin/python3
import math
import sys

ERRO = '\033[31m'
NORMAL = '\033[0m'

def help():
    print("É necessário informar o raio do círculo.")
    print("Sintaxe {} <raio>".format(sys.argv[0][2:]))

def calculo_area_circulo(raio):
    return math.pi * float(raio) ** 2

if __name__ == '__main__':
    if len(sys.argv) < 2:
        help()
        sys.exit(1)

    if not sys.argv[1].isnumeric():
        print(ERRO, "O raio informado não é um número válido.", NORMAL)
        help()
        sys.exit(1)

    raio = sys.argv[1]
    calculo = calculo_area_circulo(raio)
    print(f"Área do circulo: {calculo}")
