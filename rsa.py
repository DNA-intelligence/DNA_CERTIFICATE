'''
FilePath: rsa.py
Author: wang yu
Date: 2023-08-07 16:06:51
LastEditTime: 2024-09-21 20:20:34
'''

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
import numpy as np
import argparse
from DNA_encode import sub_encode, sub_decode

QUA2BASE = {'0':'A','1':'T','2':'C','3':'G'}
BASE2QUA = {'A':'0','T':'1','C':'2','G':'3'}

def get_opts():
    group = argparse.ArgumentParser()
    group.add_argument('-i', '--input', required=True, help="input file for encrypt or encrypted")
    group.add_argument('-o', '--output', required=True, help="result file")
    group.add_argument('-t', '--type', required=True, help="excute encode or decode")
    return group.parse_args()

# 生成密钥
def generate_key():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size = 4096         # 1024{62}, 4096{446}
    )
    public_key = private_key.public_key()

    # 私钥序列化
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    # 共钥序列化
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    # 保存公钥
    with open("public.pem", 'wb') as f:
        f.write(public_key_pem)
    # 保存私钥
    with open("private.pem", 'wb') as f:
        f.write(private_key_pem)
    
    return public_key, private_key

# 加密过程
def Encrypt(data, public_key):
    ciphertext = public_key.encrypt(
        data,
        padding = padding.OAEP(
            mgf = padding.MGF1(algorithm=hashes.SHA256()),
            algorithm = hashes.SHA256(),
            label = None
        )
    )
    return ciphertext

# 解密过程
def Decrypt(ciphertext, private_key):
    result = private_key.decrypt(
        ciphertext,
        padding = padding.OAEP(
            mgf = padding.MGF1(algorithm=hashes.SHA256()),
            algorithm = hashes.SHA256(),
            label = None
        )
    )
    return result

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
    count = 0
    for i in range(group):
        base5 = dna[i*5:i*5+5]
        base_set = getSetByGC(base5)
        if base5[-1] in base_set:
            dna_res += base5 + base_set.difference(base5[-1]).pop()
        else:
            count += 1
            print(count)
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
  
# 编码
def encode(input, public_key):
    ciphertext = b''
    with open(input, 'rb') as f:
        while True:
            data = f.read(446)
            if not data:
                break
            ciphertext += Encrypt(data,public_key)
    blc_dna = sub_encode(ciphertext)
    # ciphertext_dna = byte2base(ciphertext)
    # blc_dna = add_base(ciphertext_dna)
    # 密文dna序列写入
    with open("ciphertext_rsa.fa", 'w') as f:
        f.write(blc_dna)

    # compress_bit = huffman_compress.huff_compress(ciphertext_dna)
    # compress_dna = byte2base(compress_bit.encode())
    # with open('compress_rsa.fa', 'w') as f:
    #     f.write(compress_dna)


# 解码
def decode(input, output):
    # 从文件加载私钥
    with open('private.pem', 'rb') as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None,
            backend=default_backend
        )
    plaintext = b''
    # 读取密文
    with open(input, 'r') as f:
        ciphertext_dna = f.read()
    ciphertext = sub_decode(ciphertext_dna)
    # deblc_dna = del_base(ciphertext_dna)
    # ciphertext = bytes(base2byte(deblc_dna))
    # 解密
    for i in range(0, len(ciphertext), 512):
        if i == len(ciphertext) // 512 * 512:
           plaintext += Decrypt(bytes(ciphertext[i:]),private_key)
        else:
            plaintext += Decrypt(bytes(ciphertext[i:i+512]),private_key)

    with open(output, 'wb') as f:
        f.write(plaintext)

if __name__ == '__main__':
    opts = get_opts()
    input = opts.input
    output = opts.output
    t = opts.type

    if t == "encode":
        public_key, private_key = generate_key()
        encode(input, public_key)
    elif t == "decode":
        decode(input, output)
    else:
        raise TypeError("please enter correct instruction: encode or decode")
