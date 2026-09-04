#!/usr/bin/python3

produto = {
    'nome': 'Caneta',
    'preço': 1.50,
    'importada': True,
    'estoque': 100
}

for chave in produto:
    print(chave)

for valor in produto.values():
    print(valor)

for chave, valor in produto.items():
    print(f"{chave} = {valor}")


# A variavel chave e valor estão disponiveis a partir
# do for acima, não estão restritos ao laço
print(chave, valor)