##
##*************************************************************
##Assignment 7 Question 2
##Cedric Zhang
##Caesar Code
##*************************************************************
##

A = ['_','.','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

##encypt_char: str[len=1] -> str
##Purpose: Encrypts a single character s to caesar code
##Examples: encrypt_char('z')=>'a'
##encrypt_char('a')=>'d'
def encrypt_char(s):
   return A[(A.index(s)+3)%28]
##Testing
##encrypt_char('a')=>'d'
print 'encrypt_char Test 1'
answer=encrypt_char('a')
expected='d'
print answer == expected

##encrypt_char('z')=>'a'
print 'encrypt_char Test 2'
answer=encrypt_char('z')
expected='a'
print answer == expected

##encrypt_char('x')=>'_'
print 'encrypt_char Test 3'
answer=encrypt_char('x')
expected='_'
print answer == expected

##caesar_encrypt: str -> str
##Purpose: Consumes plain text, and encrypts it to caesar code
##Example: caesar_encrypt('') => ''
##caesar_encrypt('hello._goodbye.') => 'khoorcbjrrge.hc'
def caesar_encrypt(plain):
   if plain=='':
      return ''
   else:
      return encrypt_char(plain[0]) + caesar_encrypt(plain[1:])
##Testing
##caesar_encrypt('') => ''
print 'caesar_encrypt Test 1'
answer = caesar_encrypt('')
expected = ''
print answer == expected

##caesar_encrypt('hello._goodbye.') => 'khoorcbjrrge.hc'
print 'caesar_encrypt Test 2'
answer = caesar_encrypt('hello._goodbye.')
expected = 'khoorcbjrrge.hc'
print answer == expected

##caesar_encrypt('hot') => 'krw'
print 'caesar_encrypt Test 3'
answer = caesar_encrypt('hot')
expected = 'krw'
print answer == expected

##decrypt_char: str[len=1] -> str
##Purpose: Consumes a single str and decrypts it
##Examples: decrypt_char('e')=>'b'
##decrypt_char('_')=>'x'
def decrypt_char(s):
   return A[(A.index(s)-3)%28]
##Testing
## decrypt_char('e')=>'b'
print 'decrypt_char Test 1'
answer = decrypt_char('e')
expected = 'b'
print answer == expected

## decrypt_char('_')=>'x'
print 'decrypt_char Test 2'
answer = decrypt_char('_')
expected = 'x'
print answer == expected

## decrypt_char('b')=>'_'
print 'decrypt_char Test 3'
answer = decrypt_char('b')
expected = '_'
print answer == expected

##caesar_decrypt: str -> str
##Purpose: Consumes a cipher text and decrypts it
##Examples: caesar_decrypt('') => ''
##caesar_decrypt('khoorcbjrrge.hc') => 'hello._goodbye.'
def caesar_decrypt(cipher):
   if cipher=='':
      return ''
   else:
      return decrypt_char(cipher[0]) + caesar_decrypt(cipher[1:])
##Testing
##caesar_decrypt('') => ''
print 'caesar_decrypt Test 1(empty text)'
answer = caesar_decrypt('')
expected = ''
print answer == expected

##caesar_decrypt('khoorcbjrrge.hc') => 'hello._goodbye.'
print 'caesar_decrypt Test 2'
answer = caesar_decrypt('khoorcbjrrge.hc')
expected = 'hello._goodbye.'
print answer == expected

##caesar_decrypt('krw') => 'hot'
print 'caesar_decrypt Test 3'
answer = caesar_decrypt('krw')
expected = 'hot'
print answer == expected