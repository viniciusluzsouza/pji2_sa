import json
import random


a = {"nome":"magno", "sobrenome": "Andrade"}

print("a %s" % a)


print("nome: ", a['nome'])

a.update({"primeiro":"primeiro","nome":"magno", "sobrenome": "Andrade"})

print("update %s" % a)

b = json.dumps(a)
print("b= ", b)

c = json.loads(b)

print("c = %s" % c)

print("C sobrenome", c['sobrenome'])

print(json.dumps(c, indent=4, sort_keys=True))

def function(a, b):
    return a+b, a-b

x, y = function(3,4)

print("x:", x, "y:", y)

a = {"dic": "novo"}

print("new %s" % a)

c, d = input("tupla")

print(c, d)

cacas = []

# Sorteia cacas
for i in range(0, 5):
    caca = {}
    caca["x"] = random.randint(1, 5)
    caca["y"] = random.randint(1, 5)
    cacas.append(caca)

f = json.dumps(cacas)
g = json.loads(f)
print("Cacas: %s" % g)

print(cacas[0])

def valida(x, y):
    for i in range(len(g)):
        ca = g[i]
        print("ca", ca)
        if ca['x'] == x and ca['y'] == y:
            del g[i]
            return True
    return False

x = int(input("teste1x:"))
y = int(input("teste1y:"))
print(valida(x, y))
print("Cacas: %s" % g)

x = int(input("teste1x:"))
y = int(input("teste1y:"))
print(valida(x, y))
print("Cacas: %s" % g)