import argparse
import re

def get_opts():
    group = argparse.ArgumentParser()
    group.add_argument('--input', '-i', help='input file', required=True)
    group.add_argument('--output', '-o', help='output file', required=True)
    group.add_argument('--index', '-x', help='index inforamtion file', required=True)
    group.add_argument('--primer', '-p', help='primer information file', required=help)
    return group.parse_args()

class Merger():
    def __init__(self, index_file, primer_file):
        self.index_dict = self._read_index(index_file)
        self.primer_list = self._read_primer(primer_file)
        
    def _read_index(self, index_file):
        index_dict = dict()
        with open(index_file,'r') as f:
            for n, i in enumerate(f.readlines()):
                i = i.strip()
                index = ''.join(i.split(','))
                index_dict[n] = index
        return index_dict
    
    def _read_str(self, str_file):
        str_dict = dict()
        with open(str_file, 'r') as f:
            for i in f.readlines():
                id, info = i.strip().split('\t')
                info = [int(a) for a in info.split(',')]
                str_dict[id] = info
        return str_dict

    def _read_primer(self, primer_file):
        primer_list = []
        with open(primer_file, 'r') as f:
            for i in f.readlines():
                _, primer = i.strip().split('\t')
                primer_list += primer.split(',')
        return primer_list
    
    def merge(self, input):
        seqs_dict = dict()
        with open(input, 'r') as f:
            for i in f.readlines():
                i = i.strip()
                if not i.startswith('>'):
                    idx = i[:20]+i[-20:]
                    seqs_dict[idx] = i[20:-20]

        merge_seq = ''
        for i in range(len(seqs_dict)):
            print(i)
            key = self.index_dict[i]
            seq = seqs_dict[key]
            for primer in self.primer_list:
                pattern = re.compile(primer)
                replacement = ''
                seq = re.sub(pattern, replacement, seq)
            merge_seq += seq
        return merge_seq

if __name__ == '__main__':
    opts = get_opts()
    input = opts.input
    output = opts.output
    index_file = opts.index
    primer_file = opts.primer
    
    merger = Merger(index_file, primer_file)
    out_seq = merger.merge(input)
    with open(output, 'w') as f:
        f.write(out_seq)
