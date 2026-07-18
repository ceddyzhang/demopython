# you can write to stdout for debugging purposes, e.g.
# print("this is a debug message")

def solution(A):
    # Implement your solution here
    ans = 0
    cumulative_list = []
    cumulative_0 = 0
    cumulative_1 = 0
    for index,value in enumerate(A):
        if value == 1:
            ans = ans + cumulative_0
        else:
            cumulative_0 += 1
    if ans > 1000000000:
        ans = -1
    return ans
    

test_list = [0,1,0,1,1]
#test_list = [0,1,0]
print('Question is:' + str(test_list))
print('Answer is:' + str(solution(test_list)))