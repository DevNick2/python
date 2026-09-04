#!/usr/bin/python3
string = "paralelepípedo"


for letra in string:
    print(letra, end=",")
print("Fim")


aprovados = ["Ana", "Bia", "Carlos", "Daniel"]

for nome in aprovados:
    print(nome)

for posicao, nome in enumerate(aprovados):
    print(f"{posicao + 1}) - {nome}")


dias_semana = (
                "Segunda",
                "Terça",
                "Quarta",
                "Quinta",
                "Sexta",
                "Sábado",
                "Domingo"
            )

for dia in dias_semana:
    print(f"Hoje é {dia}")

for numero in {1, 2, 3, 4, 5}:
    print(f"Número = {numero}")