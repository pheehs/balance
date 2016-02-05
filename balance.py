#!/usr/bin/env python
#-*- coding:utf-8 -*-

import itertools
import multiprocessing as mp

N_PROC = 4

N = 13
FALSE_HEAVY = True

HEAVY = 10
LIGHT = 9
SAME = 0

LEFT_HEAVY = 0
RIGHT_HEAVY = 1
BALANCED = 2

def all_same(items):
    return all(x == items[0] for x in items)

class StrategyError(ValueError):
    pass

class Coin(object):
    def __init__(self, false):
        self.false = false
        self.labels = [None,None,None]

    def weight(self):
        if (self.false and FALSE_HEAVY) or (not self.false and not FALSE_HEAVY):
            return HEAVY
        else:
            return LIGHT

class Pair(object):
    def __init__(self, l, descr=""):
        # left,right: list/touple of indexes
        self.left = set(l[0])
        self.right = set(l[1])
        self.descr = descr
        #self.id = "".join(sorted([str(list(self.left)),str(list(self.right))]))

    def __repr__(self):
        return "<%s: %s>" % (self.descr, "".join(sorted([str(list(self.left)),str(list(self.right))])))
    def get_str(self):
        return "".join(sorted([str(list(self.left)),str(list(self.right))]))

        
def balance(coins, left, right):
    lweight = sum((coins[l].weight() for l in left))
    rweight = sum((coins[l].weight() for l in right))
    if lweight < rweight:
        return RIGHT_HEAVY
    elif lweight > rweight:
        return LEFT_HEAVY
    else:
        return BALANCED
    
def run(strategy, false_i):
    #print "coin%d is false"
    coins = [Coin(i == false_i) for i in xrange(N)]
    for step_i in xrange(3):
        left = strategy[step_i].left
        right = strategy[step_i].right
        if True not in [all_same((coins[c].labels[i] for c in left+right)) for i in xrange(step_i-1)]:
            raise StrategyError, "invalid strategy"
        res = balance(coins, left, right)
        
        if res == BALANCED:
            #print "BALANCED"
            for c in left+right:
                coins[c].labels[step_i] =  SAME
        elif res == RIGHT_HEAVY:
            #print "RIGHT HEAVY"
            for c in left:
                coins[c].labels[step_i] = LIGHT
            for c in right:
                coins[c].labels[step_i] = HEAVY
        elif res == LEFT_HEAVY:
            #print "LEFT HEAVY"
            for c in left:
                coins[c].labels[step_i] = HEAVY
            for c in right:
                coins[c].labels[step_i] = LIGHT
                
    # false coin is identical?
    if sum(1 for i in xrange(N) if coins[i].labels == coins[false_i].labels) != 1:
        raise StrategyError
        
    # ok for this false_i!
    return
        
def appendCombi(groups, source):
    for left,right in itertools.combinations(source, 2):
        #print left
        #print right
        if len(left) == len(right):
            if len([1 for c in left if c not in right]) == len(left):
                #print "append!"
                groups.append(Pair((left,right),"Another pair"))
    return groups

def submain(g):
    group_i,group = g
    balanced = [None,None,None]

    #print "%6d/%6d --" % (group_i+1, len_groups)
    balanced[0] = group
    left1 = group.left
    right1 = group.right
    others1 = set(xrange(N))-left1-right1
    #print left1
    #print right1
    #print others
    #raw_input(">")
    groups2 = []
    # make pairs from one previous label(left/right/others)
    for i in xrange(1,7):
        groups2 += [Pair(l,"New pair from left1") for l in itertools.combinations(itertools.combinations(left1,i), 2) if len([1 for c in l[0] if c not in l[1]]) == len(l[0])]
    for i in xrange(1,7):
        groups2 += [Pair(l,"New pair from right1") for l in itertools.combinations(itertools.combinations(right1,i), 2) if len([1 for c in l[0] if c not in l[1]]) == len(l[0])]
    for i in xrange(1,7):
        groups2 += [Pair(l,"New pair from others1") for l in itertools.combinations(itertools.combinations(others1,i), 2) if len([1 for c in l[0] if c not in l[1]]) == len(l[0])]
    # use the same group, except (left,right)
    groups2 = appendCombi(groups2, [left1,right1,others1])
    """
    _groups2 = []
    while len(groups2) > 0:
    c = groups2.pop()
    #remove double counted pairs
    #if sum(1 for g in _groups2 if c.id == g.id) > 0:
    #    continue
    #remove already balanced pairs
    #if c.id == balanced[0].id:
    #    continue
    #else:
    _groups2.append(c)
    
    groups2 = _groups2
    """
    #print groups2
    len_groups2 = len(groups2)
    for group2_i,group2 in enumerate(groups2):
        print "%6d/%6d  %6d/%6d" % (group_i+1, len_groups, group2_i+1, len_groups2)
        balanced[1] = group2
        left2 = group2.left
        right2 = group2.right
        others2 = set(xrange(N))-left2-right2
        #print left2
        #print right2
        #print others2
        #raw_input(">")
        
        groups3 = []
        for i in xrange(1,7):
            groups3 += [Pair(l,"New pair from previous left") for l in itertools.combinations(itertools.combinations(left2,i), 2) if len([1 for c in l[0] if c not in l[1]]) == len(l[0])]
        for i in xrange(1,7):
            groups3 += [Pair(l,"New pair from previous right") for l in itertools.combinations(itertools.combinations(right2,i), 2) if len([1 for c in l[0] if c not in l[1]]) == len(l[0])]
        for i in xrange(1,7):
            groups3 += [Pair(l,"New pair from previous others") for l in itertools.combinations(itertools.combinations(others2,i), 2) if len([1 for c in l[0] if c not in l[1]]) == len(l[0])]
                # use the same/past group
        groups3 = appendCombi(groups3, [left1,right1,others1,left2,right2,others2])
        """
        _groups3 = []
        while len(groups3) > 0:
        c = groups3.pop()
        #remove double counted pairs
        #if sum(1 for g in _groups3 if c.id == g.id) > 0:
        #    continue
        #remove already balanced pairs
        #if c.id == balanced[0].id or c.id == balanced[1].id:
        #    continue
        #else:
        _groups3.append(c)
        
        groups3 = _groups3
        """
        #print groups3
        for group3_i,group3 in enumerate(groups3):
            #print "[T=2] %d/%d" % (group3_i+1,len(groups3))
            balanced[2] = group3
            left3 = group3.left
            right3 = group3.right
            others3 = set(xrange(N))-left3-right3
            #print left3
            #print right3
            #print others3
            #raw_input(">")
            
            try:
                for false_i in xrange(N):
                    run(balanced,false_i)
                """
                if balance_run(encode(balanced[0].left),
                encode(balanced[0].right),
                encode(balanced[1].left),
                encode(balanced[1].right),
                encode(balanced[2].left),
                encode(balanced[2].right)) == 1:
                raise StrategyError
                """
            except StrategyError:
                # to next strategy
                continue
            else:
                # not strategy error
                print "------- found strategy! ---------"
                with open("strategy.txt", "a") as logfile:
                    for i in xrange(3):
                        logfile.write(balanced[i].get_str())
                        logfile.write(",")
                    logfile.write("\n")
        
                    

if __name__ == "__main__":
    groups = []
    for i in xrange(1,7):
        groups += [Pair(l,"First pair") for l in itertools.combinations(itertools.combinations(xrange(N),i), 2) if len([1 for c in l[0] if c not in l[1]]) == len(l[0])]
    global len_groups
    len_groups = len(groups)

    pool = mp.Pool(N_PROC)
    callback = pool.map(submain, enumerate(groups))


# T=0　のとき
# 純粋に2グループに分けるような方法を一つ
# T>=1　のとき
# あるラベル(OTHERS/LEFT/RIGHT)の中から２グループ抽出
# 違うラベル（Tが違っても良い）のグループを２つ選ぶ
# これはないんじゃね？ー＞//今までの結果を使わずに、純粋に２グループに分ける方法を一つ選ぶ

