import base64
from Cryptodome.Cipher import AES

text = "SADFAS"
key = 'QWE1ER2T3Y4U4I5O5PAD2SFH4JK3HX4Z'
IV = 'QWE1ER2T3Y4U4I5O'

mode = AES.MODE_CBC
encryptor = AES.new(key.encode('utf8'), mode, IV=IV.encode('utf8'))

length = 16 - (len(text) % 16)

# pad to 16 byte boundary in CBC mode
cbc_pad_text = text + bytes([length])*length
ciphertext = encryptor.encrypt(cbc_pad_text)

base64_ciphertext = base64.b64encode(ciphertext).decode("ascii")
print(base64_ciphertext)
