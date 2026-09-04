#!/usr/bin/python3

for x in range(1, 11):
    if x % 2 == 0: # apenas números ímpares
        continue # interrompe a repetição atual e vai para a próxima
    print(x)

for x in range(1, 11):
    if x == 5:
        break # interrompe a repetição atual e sai do laço
    print(x)