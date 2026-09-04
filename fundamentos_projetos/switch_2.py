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
        if i == 1 or i == 7:
            print("Fim de semana")
            continue
        else:
            print(f"{i} - {get_dia_semana(i)}")

print(" ")
print("Exemplo com match case")
print(" ")

def get_dia_semana_match_case(dia):
    match dia:
        case 1:
            return "Domingo"
        case 2:
            return "Segunda-feira"
        case 3:
            return "Terça-feira"
        case 4:
            return "Quarta-feira"
        case 5:
            return "Quinta-feira"
        case 6:
            return "Sexta-feira"
        case 7:
            return "Sábado"
        case _:
            return "Dia inválido"

for dia in range(9):
    print(f"{dia} - {get_dia_semana_match_case(dia)}")


def get_tipo_dia(dia):
    match dia:
        case 2 | 3 | 4 | 5 | 6 :
            return 'Dia de semana'
        case 1 | 7:
            return 'Fim de semana'
        case _:
            return '** inválido **'
            
 
for dia in range(0, 9):
    print(f'{dia}: {get_tipo_dia(dia)}')