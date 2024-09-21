'''
FilePath: aes.py
Author: wang yu
Date: 2023-08-07 16:06:51
LastEditTime: 2023-11-26 14:26:18
'''
'''
FilePath: aes.py
Author: wang yu
Date: 2023-08-07 16:06:51
LastEditTime: 2023-08-28 17:04:30

usage: python aes.py -i input -o output -t [encode or decode] -k key_fa
'''
from Crypto.Cipher import AES
import numpy as np
import argparse
import os
from DNA_encode import sub_encode, sub_decode

QUA2BASE = {'0':'A','1':'T','2':'C','3':'G'}
BASE2QUA = {'A':'0','T':'1','C':'2','G':'3'}

def get_opts():
    group = argparse.ArgumentParser()
    group.add_argument('-i', '--input', required=True, help="input file for crypt")
    group.add_argument('-o', '--output', required=True, help="result file")
    group.add_argument('-t', '--type', required=True, help="excute encode or decode")
    group.add_argument('-k', '--key', required=False, help="key for decryption")
    return group.parse_args()

# 字节填充
def pad(data, block_size):
    padding_size = block_size - len(data) % block_size
    padding = "0" * padding_size
    return data + padding.encode(), padding_size

# 除去填充字节
def unpad(data, padding_size):
    if padding_size > len(data):
        raise ValueError("不合法填充")
    return data[:-padding_size]

# 字节转碱基
def byte2base(data:bytes) -> str:
    res = ''
    for byte in data:
        qua = np.base_repr(byte, 4).rjust(4,'0')
        dna = ''.join([QUA2BASE[x] for x in qua])
        res += dna
    return res

# 碱基转字节
def base2byte(dna:str) -> bytes:
    qua_data =  ''.join([BASE2QUA[x] for x in dna])
    bytearr = bytearray([int(qua_data[i:i + 4], 4) for i in range(0,len(qua_data),4)])
    return bytearr

# 计算GC比例
def getSetByGC(dna:str) -> set:
    gc_content = (dna.count("C") + dna.count("G")) / len(dna)
    if gc_content>=0.5:
        return {'A','T'}
    else:
        return {'G','C'}

#均衡
def add_base(dna:str) -> str:
    if len(dna)%5!=0:
        res_nu = len(dna)%5
        dna = add_base(dna[:-res_nu])+dna[-res_nu:]
        return dna
    
    dna = dna.upper()
    group = int(len(dna)/5)
    dna_res = ""
    for i in range(group):
        base5 = dna[i*5:i*5+5]
        base_set = getSetByGC(base5)
        if base5[-1] in base_set:
            dna_res += base5 + base_set.difference(base5[-1]).pop()
        else:
            if i<(group-1):
                next_base = dna[(i+1)*5]
                if next_base in base_set:
                    dna_res += base5 + base_set.difference(next_base).pop()
                else:
                    dna_res += base5 + list(base_set)[np.random.choice([0,1])]
            else:
                dna_res += base5 + list(base_set)[np.random.choice([0,1])]
    return dna_res

# 删除均衡
def del_base(dna:str) -> str:
    if len(dna)%6!=0:
        res_nu = len(dna)%6
        dna = del_base(dna[:-res_nu])+dna[-res_nu:]
        return dna

    dna = dna.upper()
    group = int(len(dna)/6)
    dna_res = ""
    for i in range(group):
        base5 = dna[i*6:i*6+5]
        dna_res += base5
    return dna_res
  
# 加密过程
def encrypt(data, key):
    iv = os.urandom(AES.block_size)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    bk_size = AES.block_size
    padding_data, padding_size = pad(data, bk_size)
    ciphertext = cipher.encrypt(padding_data)
    return iv + ciphertext, padding_size

# 解密过程
def decrypt(ciphertext, key, padding_size):
    iv = ciphertext[:AES.block_size]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    result = cipher.decrypt(ciphertext[AES.block_size:])
    return unpad(result, padding_size)

# 编码
def encode(input,key):
    with open(input, 'rb') as f:
        data = f.read()
    ciphertext, padding_size = encrypt(data, key)
    print(data[:10])
    blc_dna = sub_encode(ciphertext)
    # ciphertext_dna = byte2base(ciphertext)
    # blc_dna = add_base(ciphertext_dna)
    # 密文dna序列写入
    with open("ciphertext_aes.fa", 'w') as f:
        f.write(blc_dna)
    return padding_size

# 解码
def decode(input, key, padding_size, output):
    with open(input, 'r') as f:
        ciphertext_dna = f.read()
    ciphertext = sub_decode(ciphertext_dna)
    # deblac_dna = del_base(ciphertext_dna)
    # ciphertext = base2byte(deblac_dna)
    result = decrypt(ciphertext, key, padding_size)
    with open(output, 'wb') as f:
        f.write(result)


if __name__ == '__main__':
    opts = get_opts()
    input = opts.input
    output = opts.output
    t = opts.type

    if t == 'encode':
        key = os.urandom(16)
        padding_size = encode(input, key)
        key = key + str(padding_size).encode()
        key_dna = byte2base(key)
        # 密钥写入
        with open('AES_key.fa', 'w') as f:
            f.write(key_dna)

    elif t == 'decode':
        key_file = opts.key
        with open(key_file,'rb') as f:
            key_dna = f.read()
        key_dna = key_dna.decode()
        key = base2byte(key_dna)[:16]
        padding_size = base2byte(key_dna)[16:]
        padding_size = int(padding_size.decode())
        decode(input, key, padding_size, output)
    else:
        raise TypeError("please enter correct instruction: encode or decode")
    
