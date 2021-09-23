##
##*************************************************************
##Assignment 6 Question 3
##Cedric Zhang
##Fibonacci Sequence
##*************************************************************
##

import math

##fib:int[<72] -> int
##Purpose: Calculates the nth Fibonacci number as long n<72
##Example: fib(1) => 1
## fib (2) => 1
## fib (3) => 2
## fib (5) => 5
def fib(n):
    gr=(1+math.sqrt(5))/2
    return int((gr**n-(1-gr)**n)/math.sqrt(5))

##determine the thrshold
import a6
def mytest(x):
    if fib(x)==a6.fib(x):
        return mytest(x+1)
    else:
        return x

print mytest(1)

##Testing
##fib(0) => 0
print 'Test 1 fib(0)'
print 0 == fib(0)

##fib(1) == fib(2) == 1
print 'Test 2 fib(1) and fib(2)'
print 1 == fib(1) and fib(1) == fib(2)

##fib(6) => 8
print 'Test 3'
print 8 == fib(6)

##fib(71) => 308061521170129L
print 'Test 4'
print fib(71) == 308061521170129L and fib(71) == a6.fib(71)

##fib(72) => not accurate
print 'Test 5'
print not fib(72) == a6.fib(72)