import matplotlib.pyplot as plt


sizes = [10, 50, 100, 500, 1000]#, 2000, 4000, 5000, 5500]
f1s   = [.49, .77, .854, .917, .926]#, .9356, .9357, .94, .945]
errs =  [.065, .031, .021, .012, .011, .0092, .0089, .00857, .0079]
acurr = [1-e for e in errs]
goalf1 = [.9 for e in f1s]
goalAcur = [.99 for e in f1s]

plt.plot(sizes, f1s)
plt.plot(sizes, goalf1)

print zip(sizes, f1s)
plt.show()

plt.plot(sizes, acurr)

plt.plot(sizes, goalAcur)

plt.show()