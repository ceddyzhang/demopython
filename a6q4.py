##
##**********************************************************
##Assignment 6 Question 4
##Cedric Zhang
##tax payable
##**********************************************************
##

teen_rate = 0.05
young_rate = 0.1
mid_rate = 0.5
old_rate = 0.025

##taxes: float int fload bool float -> int[>=0]
##Purpose: Consumes a persons income, age, rent, whether is
##a student, and tuition. Produces his/her tax.
##Examples: taxes(0.00,20,1000.00,yes,1000.00) => 0
##taxes(45000.50,23,10000.00,False,0.00) => 3500
##taxes(400000.00,55,25000.00,True,100000.00) => 200000
def taxes(income, age, rent, student, tuition):
    def tax_rate (a):
        if student == True and (a>=35 and a<=55):
            if income>=400000:
                return 0.5
            else:
                return 0.25
        elif a<18:
            return teen_rate
        elif a>=18 and a<=29:
            return young_rate
        elif a>=30 and a<=64:
            return mid_rate
        else:
            return old_rate
    def rent_d (a):
        if a < 25:
            return rent
        else:
            return rent/2
    def tuit_d (a):
        if student == True:
            if a<18 or a>64:
                return tuition
            elif a>=18 and a<=29:
                return tuition*0.75
            else:
                return tuition*0.5
        else:
            return 0
    def no_refund (x):
        if x>0:
            return int(x)
        else:
            return 0
    if income>=250000:
        return no_refund(income*tax_rate(age))
    else:
        return no_refund ((income - rent_d(age)-tuit_d(age))*tax_rate(age))

##Testing
##taxes(0.00,19,3000.00,True,20000.00)=>0
print 'Test 1:0 income'
expected=0
actual=taxes(0.00,19,3000.00,True,20000.00)
print actual == expected

##taxes(25000.00,19,3000.00,True,20000.00)=>700
print 'Test 2:young student'
expected=700
actual=taxes(25000.00,19,3000.00,True,20000.00)
print actual == expected

##taxes( 25000.00, 17, 3000.00, True, 20000.00) => 100
print 'Test 3:teen student'
expected=100
actual=taxes(25000.00,17,3000.00,True, 20000.00)
print actual == expected

##taxes( 45000.50, 23, 10000.00, False, 0.00) => 3500
print 'Test 4:young non-student'
expected=3500
actual=taxes(45000.50,23,10000.00,False,0.00)
print expected == actual

##taxes( 15000.00, 77, 10000.00, True, 19000.00) => 0
print 'Test 5:senior student with no tax'
expected=0
actual=taxes( 15000.00, 77, 10000.00, True, 19000.00)
print actual == expected

##taxes( 15000.00, 77, 10000.00, False, 19000.00) => 0
print 'Test 6:senior non-student with tax'
expected=250
actual=taxes( 15000.00, 77, 10000.00, False, 19000.00)
print actual == expected

##taxes(400000.00, 55, 25000.00, True, 100000.00) => 200000
print 'Test 7:rich student'
expected=200000
actual=taxes(400000.00, 55, 25000.00, True, 100000.00)
print actual == expected

##taxes(400000.00, 55, 25000.00, False, 100000.00) => 200000
print 'Test 8:rich non-student'
expected=200000
actual=taxes(400000.00, 55, 25000.00, False, 100000.00)
print actual == expected