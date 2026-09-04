#!/usr/bin/python3

# Sortear um numero de 1 a 6, igual a um dado.
from random import randint

def sortear_dado():
    return randint(1, 6)

for i in range(1, 7):
    if i % 2 == 1:
        continue

    if i == sortear_dado():
        print(f"Acertou!", i)
        break
else:
    print(f"Errou!")