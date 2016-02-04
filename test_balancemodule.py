import balancemodule

def encode(l):
    n = 0
    for i in xrange(12,-1,-1):
        n = n << 1
        if i in l:
            n = n | 1
    return n

print balancemodule.balance_run(encode([0]),
                                encode([1]),
                                encode([2,3]),
                                encode([4,5]),
                                encode([2]),
                                encode([3]))
