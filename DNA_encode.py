import numpy as np

QUA2BASE = {'0':'A','1':'T','2':'C','3':'G'}
BASE2QUA = {'A':'0','T':'1','C':'2','G':'3'}

def byte2base(data:bytes) -> str:
    res = ''
    for byte in data:
        if byte < 128:
            if byte < 64:
                qua = np.base_repr(byte,4).rjust(3,'0')
                dna = ''.join(QUA2BASE[x] for x in qua)
                if dna[0] == 'A' or dna[0] == 'T':
                    dna += 'C'
                else:
                    dna += 'A'
            else:
                byte = byte - 64
                qua = np.base_repr(byte,4).rjust(3,'0')
                dna = ''.join(QUA2BASE[x] for x in qua)
                if dna[0] == 'A' or dna[0] == 'T':
                    dna += 'G'
                else:
                    dna += 'T'
        else:
            byte -= 128
            if byte < 64:
                qua = np.base_repr(byte,4).rjust(3,'0')
                dna = ''.join(QUA2BASE[x] for x in qua)
                if dna[0] == 'A':
                    dna += 'TC'
                elif dna[0] == 'T':
                    dna += 'AC'
                elif dna[0] == 'C':
                    dna += 'GA'
                else:
                    dna += 'CA'
            else:
                byte = byte - 64
                qua = np.base_repr(byte,4).rjust(3,'0')
                dna = ''.join(QUA2BASE[x] for x in qua)
                if dna[0] == 'A':
                    dna += 'TG'
                elif dna[0] == 'T':
                    dna += 'AG'
                elif dna[0] == 'C':
                    dna += 'GT'
                else:
                    dna += 'CT'
        res += dna
    return res

def balance(dna:str) -> str:
    flag = 0
    new_dna = ''
    while flag < len(dna):
        pos1 = flag
        pos2 = flag+4
        sub_dna = dna[pos1:pos2]
        if sub_dna[0] in 'AT' and sub_dna[-1] in 'CG' and pos2 < len(dna)-1: 
            if pos2+1 >= len(dna) or pos2+2 >= len(dna) or pos2+3 >= len(dna):
                break
            if len(set(sub_dna[1:]+dna[pos2])) == 1 or len(set(sub_dna[2:]+dna[pos2:pos2+2])) == 1 or len(set(sub_dna[-1]+dna[pos2:pos2+3])) == 1:
                sub_dna = sub_dna[:-1] + sub_dna[0]
                if len(set(sub_dna)) == 1 and sub_dna[0] == 'A':
                    sub_dna = sub_dna[:-1] + 'TT'
                elif len(set(sub_dna)) == 1 and sub_dna[0] == 'T':
                    sub_dna = sub_dna[:-1] + 'AA'
        elif sub_dna[0] in 'CG' and sub_dna[-1] in 'AT' and pos2 < len(dna)-1:
            if pos2+1 >= len(dna) or pos2+2 >= len(dna) or pos2+3 >= len(dna):
                break
            if len(set(sub_dna[1:]+dna[pos2])) == 1 or len(set(sub_dna[2:]+dna[pos2:pos2+2])) == 1 or len(set(sub_dna[-1]+dna[pos2:pos2+3])) == 1:
                sub_dna = sub_dna[:-1] + sub_dna[0]
                if len(set(sub_dna)) == 1 and sub_dna[0] == 'C':
                    sub_dna = sub_dna[:-1] + 'GG'
                elif len(set(sub_dna)) == 1 and sub_dna[0] == 'G':
                    sub_dna = sub_dna[:-1] + 'CC'
        elif pos2 < len(dna) -1:
            pos2 = flag+5
            sub_dna = dna[pos1:pos2]
            if len(set(sub_dna[-1]+dna[pos2:pos2+3])) == 1:
                sub_dna = sub_dna[:-1] + sub_dna[0]
        else:
            sub_dna = dna[pos1:]
        flag = pos2
        new_dna += sub_dna
    return new_dna

def parse4bases(qua_list: list, sub_dna: str) -> list:
    judge = True
    if sub_dna[0] in 'AT' and sub_dna[-1] in 'CG': 
        if sub_dna[-1] == 'C':
            qua = ''.join(BASE2QUA[x] for x in sub_dna[:-1])
            qua_list.append(int(qua,4))
        else:
            qua = ''.join(BASE2QUA[x] for x in sub_dna[:-1])
            qua_list.append(int(qua,4)+64)
    elif sub_dna[0] in 'CG' and sub_dna[-1] in 'AT':
        if sub_dna[-1] == 'A':
            qua = ''.join(BASE2QUA[x] for x in sub_dna[:-1])
            qua_list.append(int(qua,4))
        else:
            qua = ''.join(BASE2QUA[x] for x in sub_dna[:-1])
            qua_list.append(int(qua,4)+64)
    else:
        judge = False
    return qua_list, judge


def base2byte(dna:str) -> bytes:
    bytearr = ''
    flag = 0
    qua_list = []
    raw_seq = ''
    while flag < len(dna):
        pos1 = flag
        pos2 = flag+4
        sub_dna = dna[pos1:pos2]
        qua_list, judge = parse4bases(qua_list, sub_dna)
        if pos2 >= len(dna):
            break
        if not judge:
            if sub_dna[0] == sub_dna[-1]:
                sub_dna = sub_dna[:-1] + dna[pos2]
                raw_seq += sub_dna
                qua_list, judge = parse4bases(qua_list, sub_dna)
            else:
                pos2 = flag+5
                sub_dna = dna[pos1:pos2]
                if len(set(sub_dna[-2:])) == 1 and len(set(dna[pos2:pos2+3])) == 1:
                    sub_dna = sub_dna[:-2] + dna[pos2]
                    raw_seq += sub_dna
                    qua_list, judge = parse4bases(qua_list, sub_dna)
                else:
                    raw_seq += sub_dna
                    if sub_dna[0] == sub_dna[-1]:
                        try:
                            sub_dna = sub_dna[:-1] + dna[pos2]
                        except:
                            pass

                    if sub_dna[-1] in 'CA':
                        qua = ''.join(BASE2QUA[x] for x in sub_dna[:-2])
                        qua_list.append(int(qua,4)+128)
                    else:
                        qua = ''.join(BASE2QUA[x] for x in sub_dna[:-2])
                        qua_list.append(int(qua,4)+192)
        else:
            raw_seq += sub_dna
        flag = pos2
    for i in qua_list:
        if i > 256:
            print(i)
    bytearr = bytearray(qua_list)
    return bytearr

def sub_encode(input_byte):
    dna = byte2base(input_byte)
    dna = balance(dna)
    return dna

def sub_decode(dna):
    byte = base2byte(dna)
    return byte
