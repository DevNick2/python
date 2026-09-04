#!/usr/bin/python3

# constantes sempre com letras maiusculas
PALAVRAS_PROIBIDAS = {'futebol', 'politica', 'religiao'}
textos = [
    'João gosta de futebol e politica',
    'A praia foi divertida',
]

for texto in textos:
    intersecao = PALAVRAS_PROIBIDAS.intersection(set(texto.lower().split()))

    if intersecao:
        print("Texto possui pelo menos uma palavra proibida:", intersecao)
    else:
        print("Texto autorizado:", texto)