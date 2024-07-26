
import random


def randomColor():
    r = random.randrange(0,255)
    g = random.randrange(0,255)
    b = random.randrange(0,255)
    y = random.randrange(0,255)

    return (r,g,b,y)