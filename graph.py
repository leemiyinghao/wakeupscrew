import numpy
from matplotlib import pyplot

raw = numpy.array([i/1000 for i in range(1000)])
x2 = raw**2
pyplot.plot(x2)
x3 = raw**3
pyplot.plot(x3)
x10 = raw**10
pyplot.plot(x10)
rx10 = 10 ** raw
pyplot.plot(rx10)
custom = 10**(raw*10)
pyplot.plot(custom)
pyplot.show()