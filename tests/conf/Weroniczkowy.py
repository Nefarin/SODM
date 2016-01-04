import numpy

def weroniczka(a, b, c=0):
    print(a)
    xs = []
    ys = {}
    ks = ()
    zs = set()

    k = "abc"
    k = k + "cde"

    xs.append("asdasb")
    xs.append(3)
    xs.append(232)

    xs = xs + [23, 232]

    ys['W'] = 5
    ys['K'] = 7

    ks = ("asbsasdas", 7)
    name, number = ks

    zs.add(3)
    zs.add(5)
    zs.add(7)
    zs.add(3)

    print(xs)
    print(ys)
    print(ks)
    print(zs)

    for x in xs:
        print(x)
    print("Slownik")
    for k in ys:
        print(ys[k])

    for j in xrange(5, 10):
        print(j)

    return 0

def generatorWeroniczek():
    lista = range(3)
    for i in lista:
        yield i

def genWeroniczka():
    generator = generatorWeroniczek()
    for k in generator:
        print(k)
def weroniczkaAdvanced():
    wp = [x*x if x != 2 else 99 for x in range(1,4)]
    print(wp)

class Weroniczka(object):
    def __init__(self, abc):
        self.abc = abc
    def printAbc(self):
        print(self.abc)

#weroniczka(0,0)
#weroniczkaAdvanced()
#genWeroniczka()

weroniczka = Weroniczka("sdasd")
weroniczka.printAbc()