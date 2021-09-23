# module a6

# fib: int[>= 0] -> int[>= 0]
# Purpose: consumes an integer n >= 0 and produces
#    an int which is the n-th Fibonacci number F(n)
# Examples:
#    fib(0) => 0
#    fib(1) => 1
#    fib(2) => 1
#    fib(10) => 55
#    fib(47) == 2971215073

def fib(n): 

    # fib_acc: int[>0] int[>0] int[>0] int[>=0] -> int[>0]
    # Purpose: accumulate the i-th Fibonacci number F(i) in the parameter a
    #   and the (i-1)-th Fibonacci number F(i-1) in the parameter b.  
    #   Produces F(n) when the inputs (n,i,a,b) satisfy all of:
    #       0<i<=n, F(i)=a and F(i-1)=b
    # Examples:
    #   fib_acc(n,1,1,0) => F(n)
    #   fib_acc(n,i, F(i), F(i-1)) => F(n)
    def fib_acc(n,i,a,b):
        if (i==n):
            return a
        else:
            return fib_acc(n,i+1,a+b,a)
          
    if (n==0):
        return 0
    else:
        return fib_acc(n,1,1,0)


