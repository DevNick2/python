#!/usr/bin/python3

import math


def calculo_area_circulo(raio):
    print(f"Área do circulo: {math.pi * (raio ** 2)}")


if __name__ == '__main__':
    raio = int(input('Informe o raio: '))

    calculo_area_circulo(raio)
