##
##*************************************************************
##Assignment 7 Question 3
##Cedric Zhang
##CSV
##*************************************************************
##

a_csv_data =['Trevor, 87.5, 84.5','Bruce, 73.0, 75.0','Lucy, 96.4, 94.9']
a_list_data = [['Trevor','87.5','84.5'],['Bruce','73.0','75.0'],['Lucy','96.4','94.9']]

##convert_str: str str (listof str) -> (listof str)
##Purpose: Consumes a s which represents a row, 
##entry(accumulator), and loe(accumulator). Produces the row
##in a list of str form
##Examples: convert_str('','',[]) => []
##convert_str('Bruce, 73.0, 75.0','',[])
## => ['Bruce','73.0','75.0']
def convert_str(s,entry,loe):
    if s=='':
        if entry=='':
            return loe
        else:
            loe.extend([entry])
            return loe
    elif s[0]==' ':
        return convert_str(s[1:],entry,loe)
    elif s[0]==',':
        loe.extend([entry])
        entry=''
        return convert_str(s[1:],'',loe)
    else:
        entry = entry + s[0]
        return convert_str(s[1:],entry,loe)
##Testing
##convert_str('Bruce, 73.0, 75.0','',[])
## => ['Bruce','73.0','75.0']
print 'convert_str Test 1'
answer = convert_str('Bruce, 73.0, 75.0','',[])
expected = ['Bruce','73.0','75.0']
print answer == expected

##convert_str('Trevor, 87.5, 84.5,','',[])
## => ['Trevor','87.5','84.5']
print 'convert_str Test 2(ends with comma)'
answer = convert_str('Trevor, 87.5, 84.5,','',[])
expected = ['Trevor','87.5','84.5']
print answer == expected

##convert_str(' Lucy ,  96.4 ,  94.9','',[])
## => ['Bruce','73.0','75.0']
print 'convert_str Test 3(multiple white space)'
answer = convert_str(' Lucy ,  96.4 ,  94.9','',[])
expected = ['Lucy','96.4','94.9']
print answer == expected

##csv_to_list: (listof str) -> (listof (listof str))
##Purpose: Consumes a csv_data and converts it to a nested list
##Example: csv_to_list([]) => []
##csv_to_list(a_csv_data)
## => [['Trevor','87.5','84.5'], ['Bruce','73.0','75.0'], ['Lucy','96.4','94.9']]
def csv_to_list(csv_data):
   return map(lambda x: convert_str(x,'',[]),csv_data)
##Testing
##csv_to_list([]) => []
print 'csv_to_list Test 1(empty)'
answer = csv_to_list([])
expected = []
print answer == expected

print 'csv_to_list Test 2'
answer = csv_to_list(a_csv_data)
expected = [['Trevor','87.5','84.5'], ['Bruce','73.0','75.0'], ['Lucy','96.4','94.9']]
print answer == expected

##Part b

##convert_list: (listof str) -> str
##Purpose: Consumes a lst which represents a row in CSV and
##converts that to a string
##Examples: convert_list([]) => ''
##convert_list(['Trevor','87.5','84.5'])
## => 'Trevor, 87.5, 84.5'
def convert_list(lst):
    def convert_list_helper(l):
        if l==[]:
            return ''
        else:
            return ', '+l[0]+convert_list_helper(l[1:])
    return (convert_list_helper(lst))[2:]
##Testing
##convert_list([]) => ''
print 'convert_list Test 1(empty list)'
answer = convert_list([])
expected = ''
print answer == expected

##convert_list(['Trevor','87.5','84.5']) => 'Trevor,87.5,84.5'
print 'convert_list Test 2'
answer = convert_list(['Trevor','87.5','84.5'])
expected = 'Trevor, 87.5, 84.5'
print answer == expected

##convert_list([''Bruce','73.0','75.0']) => 'Bruce,73.0,75.0'
print 'convert_list Test 3'
answer = convert_list(['Bruce','73.0','75.0'])
expected = 'Bruce, 73.0, 75.0'
print answer == expected

##list_to_csv: (listof (listof str)) -> (listof str)
##Purpose: Consumes a list_data, and converts that to CSV
##Examples:list_to_csv([]) => []
##list_to_csv(a_list_data)
##=>['Trevor, 87.5, 84.5','Bruce, 73.0, 75.0','Lucy, 96.4, 94.9']
def list_to_csv(list_data):
   return map(convert_list, list_data)
##Testing
##list_to_csv([]) => []
print 'list_to_csv Test 1(empty)'
answer = list_to_csv([])
expected = []
print answer == expected

##list_to_csv(a_list_data) => ['Trevor, 87.5, 84.5','Bruce, 73.0, 75.0','Lucy, 96.4, 94.9']
print 'list_to_csv Test 2'
answer = list_to_csv(a_list_data)
expected = ['Trevor, 87.5, 84.5','Bruce, 73.0, 75.0','Lucy, 96.4, 94.9']
print answer == expected

##Part c
chg_val_s1 = 'Value at row '
chg_val_s2 = ' column '
chg_val_s3 = ' changed.'

##change_value: (listof (listof str)), int[>=0], int[>=0], str
## -> None
##Purpose: Consumes a list_data, a row, a col, and a new_val.
##Produces None
##Effects: Replaces the value at specified row and col with the
##new_val. Prints the row and col changed.
##Examples: change_value(a_list_data,2,1,'95.0') changes Lucy's
##first mark to 95.0. Prints 'Value at row 2 column 1 changed'.
## change_value(a_list_data,0,0,'95.0') changes Trevor to 95.0
## Prints 'Value at row 0 column 0 changed'.
def change_value(list_data, row, col, new_val):
   print chg_val_s1+str(row)+chg_val_s2+str(col)+chg_val_s3
   list_data[row][col]=new_val
##Testing
##change_value(a_list_data,2,1,'95.0') => None
print 'change_value Test 1'
change_value(a_list_data,2,1,'95.0')
##Lucy's first mark is dropped to 95.0
expected = [['Trevor','87.5','84.5'],['Bruce','73.0','75.0'],['Lucy','95.0','94.9']]
print a_list_data == expected

##change_value(a_list_data,0,0,'95.0') => None
print 'change_value Test 2'
change_value(a_list_data,0,0,'95.0')
##Trevor changed to 95.0
expected = [['95.0','87.5','84.5'],['Bruce','73.0','75.0'],['Lucy','95.0','94.9']]
print a_list_data == expected


##Part d
##sort_csv: (listof str) int[>=0], bool -> (listof str)
##Purpose: Consumes a csv_data, sort_col, and whether we want
##it ascending or not. Produces the sorted csv
##Examples: sort_csv([]) => []
##sort_csv(a_csv_data,0, True)
## =>['Bruce, 73.0, 75.0','Lucy, 96.4, 94.9','Trevor, 87.5, 84.5']
##sort_csv(a_csv_data, 1, False) 
## => ['Lucy, 96.4, 94.9','Trevor, 87.5, 84.5','Bruce, 73.0, 75.0']
def sort_csv(csv_data, sort_col, ascending):
   converted = csv_to_list(csv_data)
   converted.sort(lambda x,y: cmp(x[sort_col],y[sort_col]),reverse=not ascending)
   return list_to_csv(converted)
##Testing
##sort_csv([], 0, True) => []
print 'sort_csv Test 1(empty)'
answer = sort_csv([],0,True)
expected = []
print answer == expected

##sort_csv(a_csv_data, 0, True) =>
##['Bruce, 73.0, 75.0','Lucy, 96.4, 94.9','Trevor, 87.5, 84.5']
print 'sort_csv Test 2'
answer = sort_csv(a_csv_data,0,True)
expected = ['Bruce, 73.0, 75.0','Lucy, 96.4, 94.9','Trevor, 87.5, 84.5']
print answer == expected

##sort_csv(a_csv_data, 0, True) =>
##['Lucy, 96.4, 94.9','Trevor, 87.5, 84.5','Bruce, 73.0, 75.0']
print 'sort_csv Test 3'
answer = sort_csv(a_csv_data, 1, False)
expected = ['Lucy, 96.4, 94.9','Trevor, 87.5, 84.5','Bruce, 73.0, 75.0']
print answer == expected