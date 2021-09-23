##
##*************************************************************
##Assignment 6 Question 1
##Cedric Zhang
##Valid SIN
##*************************************************************
##

##get_next_10: int -> int
##Purpose: Consumes an number x and produces the next multiple
##of 10 that's >=x
##Examples: get_next_10(0)=>0
##get_next_10(11)=>20
##get_next_10(20)=>20
def get_next_10(x):
    if 0 == x % 10:
        return x
    else:
        return 10* (x/10+1)
##Testing for get_next_10
##get_next_10(0) => 0
print "get_next_10 Test 1"
print 0 == get_next_10(0)

##get_next_10(11) => 20
print "get_next_10 Test 2"
print 20 == get_next_10(11)

##get_next_10(20) => 20
print "get_next_10 Test 3"
print 20 == get_next_10(20)
    
##is_valid_sin: str -> bool
##Purpose: Identifies whether the sin is valid or not
##Examples: is_valid_sin("") -> False
##is_valid_sin("124356874") -> True
##is_valid_sin("124356877") -> False
def is_valid_sin(sin):
    ##adddigits: int -> int
    ##Purpose: produces the sum of the digits of x
    ##Example: adddigits(0) => 0
    ##adddigits(1001229) => 15
    def adddigits (x):
        if x<10:
            return
        else:
            return x % 10 + adddigits(x/10)
    if not(len(sin)==9):
        return False
    else:
        C2=2*int(sin[1])
        C4=2*int(sin[3])
        C6=2*int(sin[5])
        C8=2*int(sin[7])
        first_sum=adddigits(C2)+adddigits(C4)+adddigits(C6)+adddigits(C8)
        second_sum=int(sin[0])+int(sin[2])+int(sin[4])+int(sin[6])
        total_sum=first_sum+second_sum
        next_10=get_next_10(total_sum)
        check=next_10-total_sum
        return check==int(sin[8])

##Testing
##is_valid_sin("") => False
print "Test 1"
expected=False
actual=is_valid_sin("")
print actual == expected

##is_valid_sin("124356874") => True
print "Test 2"
expected=True
actual=is_valid_sin("124356874")
print expected == actual

##is_valid_sin("124356877") => False
print "Test 3"
expected=False
actual=is_valid_sin("124356877")
print expected == actual

##is_valid_sin("123") => False
print "Test 4"
expected=False
actual=is_valid_sin("123")
print expected == actual