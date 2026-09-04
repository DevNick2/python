#!/usr/bin/python3


def get_dia_semana(dia):
    switcher = {
        1: "Domingo",
        2: "Segunda-feira",
        3: "Terça-feira",
        4: "Quarta-feira",
        5: "Quinta-feira",
        6: "Sexta-feira",
        7: "Sábado"
    }
    return switcher.get(dia, "Dia inválido")

if __name__ == "__main__":
    for i in range(0, 9):
        print(f"{i} - {get_dia_semana(i)}")