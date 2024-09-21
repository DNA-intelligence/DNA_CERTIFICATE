'''
FilePath: encrypt_with_str.py
Author: wang yu
Date: 2023-11-24 15:14:53
LastEditTime: 2024-09-21 18:01:53
'''
'''
FilePath: split_info_with_primer.py
Author: wang yu
Date: 2023-11-20 13:56:26
LastEditTime: 2023-11-24 14:31:24
'''
import argparse

def get_opts():
    group = argparse.ArgumentParser()
    group.add_argument('--input', '-i', help='input file', required=True)
    group.add_argument('--output', '-o', help='output file', required=True)
    group.add_argument('--index', '-x', help='index inforamtion file', required=True)
    group.add_argument('--str', '-s', help='STR information file', required=True)
    group.add_argument('--primer', '-p', help='primer information file', required=help)
    return group.parse_args()

class Splitor():
    def __init__(self, index_file, str_file, primer_file):
        self.index_list = self._read_index(index_file)
        self.str_dict = self._read_str(str_file)
        self.primer_dict = self._read_primer(primer_file)
        
    def _read_index(self, index_file):
        with open(index_file,'r') as f:
            index_list = [i.strip().split(',') for i in f.readlines()]
        return index_list
    
    def _read_str(self, str_file):
        str_dict = dict()
        with open(str_file, 'r') as f:
            for i in f.readlines():
                id, info = i.strip().split('\t')
                info = [int(a) for a in info.split(',')]
                str_dict[id] = info
        return str_dict

    def _read_primer(self, primer_file):
        primer_dict = dict()
        with open(primer_file, 'r') as f:
            for i in f.readlines():
                id, primer = i.strip().split('\t')
                primers = primer.split(',')
                primer_dict[id] = primers
        return primer_dict

    def split_data(self, input):
        gene_fa = dict()
        count = 0
        summ = 0
        seq = ''
        pos = 0
        final_id = ''
        res = ''
        new_dict = dict()

        with open(input, 'r') as f:
            info_seq = f.read()

        print(self.index_list)
        for key, value in self.str_dict.items():
            summ += len(self.primer_dict[key][0])
            seq += self.primer_dict[key][0]
            len_list = len(value)
            pre = 0
            new_dict[key] = []
            for i in range(len_list-1, -1, -1):
                if i != len_list-1 and value[i] - pre < 30:
                    new_dict[key].append(value[i])
                    continue
                if pre == 0:
                    seg = value[i]- pre
                else:
                    seg = value[i]- pre - len(self.primer_dict[key][1])
                seq += info_seq[pos:pos+seg] + self.primer_dict[key][1]
                pre = value[i]
                pos += seg
                summ += seg + len(self.primer_dict[key][1])
            seq += info_seq[pos:pos+50]
            pos += 50
            summ += 50
            if summ >= 2000:
                summ = len(self.primer_dict[key][0])
                id = "gene_" + str(count)
                gene_fa[id] = seq
                count += 1
                seq = ''
        for key, value in new_dict.items():
            if not value:
                continue
            print(value)
            summ += len(self.primer_dict[key][0])
            seq += self.primer_dict[key][0]
            len_list = len(value)
            new_dict[key] = []
            for i in range(len_list):
                if i == 0:
                    seq += info_seq[pos:pos+value[i]] + self.primer_dict[key][1]
                    pos += value[i]
                    summ += value[i] + len(self.primer_dict[key][1])
                else:
                    seg = value[i] -value[i-1] -len(self.primer_dict[key][1])
                    seq += info_seq[pos:pos+seg] + self.primer_dict[key][1]
                    pos += seg
                    summ += seg + len(self.primer_dict[key][1])
                if summ >= 2000:
                    summ = len(self.primer_dict[key][0])
                    id = "gene_" + str(count)
                    gene_fa[id] = seq
                    count += 1
                    seq = ''
            seq += info_seq[pos:pos+50]
            pos += 50
            summ += 50
        print(len(info_seq[pos:]))
        if not seq:
            final_id = "gene_" + str(count)
            res = info_seq[pos:]
            print("res length: {}".format(len(res)))
            if len(res) <= 2500 and len(res) > 0:
                gene_fa[final_id] = res
            elif len(res) > 2500:
                while pos <= len(info_seq) and len(res) > 2500:
                    split_id = "gene_" + str(count)
                    split_seq = info_seq[pos:pos+2500]
                    gene_fa[split_id] = res
                    pos += 2500
                    count += 1
                res = info_seq[pos:]
                res_id = "gene_" + str(count)
                gene_fa[res_id] = res
        else:
            final_id = 'gene_' + str(count)
            count += 1
            gene_fa[final_id] = seq
            res = info_seq[pos:]
            split_seq = ''
            while pos <= len(info_seq) and len(res) > 2500:
                split_id = "gene_" + str(count)
                split_seq = info_seq[pos:pos+2500]
                gene_fa[split_id] = split_seq
                pos += 2500
                count += 1
            if len(res) > 0:
                res = info_seq[pos:]
                res_id = "gene_" + str(count)
                gene_fa[res_id] = res
        return gene_fa

if __name__ == '__main__':
    opts = get_opts()
    input = opts.input
    output = opts.output
    index_file = opts.index
    str_file = opts.str 
    primer_file = opts.primer
    
    splitor = Splitor(index_file, str_file, primer_file)
    gene_fa = splitor.split_data(input)
    flag = 0
    with open(output, 'w') as f:
        for key, value in gene_fa.items():
            f.write(">" + key + "\n")
            f.write(splitor.index_list[flag][0] + value + splitor.index_list[flag][1] + "\n")
            flag += 1
    


