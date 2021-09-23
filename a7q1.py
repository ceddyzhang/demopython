##
##*************************************************************
##Assignment 7 Question 1
##Cedric Zhang
##Partial Search
##*************************************************************
##

duplicate_s = "Duplicate word: "
list_of_strings = ['apples','bananas','oranges']

##Part a

##partial_list_search: (listof str) str => (listof str)
##Purpose: Consumes a list_of_words and a target. Produces
##a sublist of list_of_words with strings that contain target
##Examples: partial_list_search([],'') => []
##partial_list_search(list_of_strings, '') => list_of_strings
##partial_list_search(list_of_strings,'banana') => ['bananas']
def partial_list_search(list_of_words, target):
   return filter (lambda x: target in x, list_of_words)
##Testing
##partial_list_search([],'banana') => []
print 'Part a Test 1'
ans = partial_list_search([], 'banana')
expected = []
print ans == expected

##partial_list_search(list_of_strings,'') => list_of_strings
print 'Part a Test 2'
ans = partial_list_search(list_of_strings, '')
expected = list_of_strings
print ans == expected

##partial_list_search(list_of_strings,'banana') => ['bananas']
print 'Part a Test 3'
ans = partial_list_search(list_of_strings, 'banana')
expected = ['bananas']
print ans == expected

##partial_list_search(list_of_strings,'an')
##=> ['bananas','oranges']
print 'Part a Test 4'
ans = partial_list_search(list_of_strings,'an')
expected = ['bananas', 'oranges']
print ans == expected


##Part b

##switch_to_list: str -> str
##Purpose: Consumes sow(string of words) and converts it to a
##list of strs where all strs are grouped and in lowercase
##Examples: switch_to_list('  abc def  ') => ['abc','def']
##switch_to_list('   a("s  babY II  ') => ['a("s','babY','II']
def switch_to_list(sow):
   def switch_to_list_acc(s,word,lst):
      if 0 == len(s):
         lst.append(word)
         return lst
      elif ' ' == s[0]:
         lst.append(word)
         return switch_to_list_acc(s[1:],'',lst)
      else:
         word = word+s[0]
         return switch_to_list_acc(s[1:],word,lst)
   return filter (lambda x: not x == '', switch_to_list_acc(sow,'',[]))
##Testing
##switch_to_list('  abc def  ') => ['abc','def']
print 'switch_to_list Test 1'
ans = switch_to_list('  abc def  ')
expected = ['abc','def']
print ans == expected

##switch_to_list('   a("s  babY II  ') => ['a("s','babY','II']
print 'switch_to_list Test 2'
ans = switch_to_list('   a("s  babY II  ')
expected = ['a("s','babY','II']
print ans == expected

##remove_duplicates: (listof any) (listof any) -> (listof any)
##Purpose: Consumes a lst and answer(accumulator). Produces a
##list where repeated elements are removed
##Effects: If a word is repeated for n times, then prints
##'Duplicate word: x' n-1 times
##Examples: remove_duplicates(['1','2','3','2'],[]) 
## =>['1','2','3'] and prints 'Duplicate word: 2' 1 time
##remove_duplicates([],[]) => [] with no effect
def remove_duplicates(lst,answer):
    if lst == []:
        return answer
    elif lst[0] in answer:
       print duplicate_s + lst[0]
       return remove_duplicates(lst[1:], answer)
    else:
       answer.append(lst[0])
       return remove_duplicates(lst[1:],answer)
##Testing
##remove_duplicates([],[])=>[]
print 'remove_duplicates Test 1(empty)'
answer = remove_duplicates([],[])
expected = []
print answer == expected

##remove_duplicates(['1','2','3','2'],[])=>['1','2','3']
print 'remove_duplicates Test 2'
##Should also see 'Duplicate word: 2' 1 time, 'Duplicate word: 3' 1 time
answer = remove_duplicates(['1','2','3','2','3'],[])
expected = ['1','2','3']
print answer == expected

##remove_duplicates(['1','2','3','2','3','2'],[])=>['1','2','3']
print 'remove_duplicates Test 3'
##Should also see 'Duplicate word: 2','Duplicate word: 3', 'Duplicate word: 2'
answer = remove_duplicates(['1','2','3','2','3','2'],[])
expected = ['1','2','3']
print answer == expected

##partial_str_search: str str -> (listof str[lower case])
##Purpose: Consumes a string_of_words and a target. Produces a
##list of words that contain the target
##Effects: If a word is repeated for n times, then prints
##'Duplicate word: x' n-1 times
##Examples: partial_str_search('', 'banana')=>[]. No effect
##partial_str_search('Apples Bananas ORANGES', 'banana')
## => ['bananas]. No effect.
##partial_str_search('Apples OranGes Bananas ORANGES oranges', 
##'an') => ['oranges','bananas'] and prints 'Duplicate word: 
##oranges' 2 times,
def partial_str_search(string_of_words, target):
   sow=string_of_words.strip().lower()
   low=switch_to_list(sow)
   search_result=partial_list_search(low,target)
   return remove_duplicates(search_result,[])
##Testings
##partial_str_search('', 'banana')=>[]
print 'partial_str_search Test 1(empty listofwords)'
answer = partial_str_search('', 'banana')
expected = []
print answer == expected

##partial_str_search('Apples OranGes Bananas ORANGES oranges', 
##'') => ['apples','oranges','bananas']
print 'partial_str_search Test 2(empty target)'
answer = partial_str_search('Apples OranGes Bananas ORANGES oranges', '')
##Prints 'Duplicate word: oranges' 2 times
expected = ['apples','oranges','bananas']
print answer == expected

##partial_str_search('Apples Bananas ORANGES', 'banana') 
## => ['bananas']
print 'partial_str_search Test 3'
answer = partial_str_search('Apples Bananas ORANGES', 'banana')
expected = ['bananas']
print answer == expected


##partial_str_search('Apples OranGes Bananas ORANGES oranges', 
##'an') => ['oranges','bananas']
print 'partial_str_search Test 4'
answer = partial_str_search('Apples OranGes Bananas ORANGES oranges Bananas', 'an')
##Prints 'Duplicate word: oranges' 2 times and 'Duplicate word: apples' 
expected = ['oranges','bananas']
print answer == expected