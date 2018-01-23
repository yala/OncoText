import torch
import torch.utils.data as data
import gzip
import tqdm
import pickle
import json
import pdb
from rationale_net.datasets.abstract_dataset import AbstractDataset
import rationale_net.utils.dataset as utils
import random
import copy
from sklearn.utils import murmurhash3_32

SMALL_TRAIN_SIZE = 800
random.seed(0)


class PathologyDataset(data.Dataset):

    def __init__(self, args, reports, label_map, text_key, name, vocab_size=1e6, max_length=720):
        self.name = name
        self.args = args
        diagnosis = args.aspect
        self.vocab_size  = vocab_size
        self.max_length = max_length
        self.dataset = reports
        self.text_key = text_key
        self.samples = copy.deepcopy( self.dataset)
        self.class_balance = {}
        for i, sample in tqdm.tqdm(enumerate(self.samples)):
            sample['x'] = self.processLine(sample[text_key])
            if name == 'test':
                 sample['y'] = 0
                 val = 'NA'
            else:
                sample['y'] = label_map[diagnosis].index(sample[diagnosis])
                val = sample[diagnosis]
                args.num_class = len(label_map[diagnosis])
            sample['val'] = val
            sample['i'] = i
            if not val in self.class_balance:
                self.class_balance[ val ] = 0
            self.class_balance[val] += 1
        print ("Class balance", self.class_balance)

        weight_per_class = 1. / len(self.class_balance)
        self.weights = [ weight_per_class / self.class_balance[d['val']]
                             for d in self.samples ]


    def hash(self, token):
        """Unsigned 32 bit murmurhash for feature hashing."""
        return murmurhash3_32(token, positive=True) % self.vocab_size

    ## Convert one line from beer dataset to {Text, Tensor, Labels}
    def processLine(self, raw_text):
        text = raw_text.split()[:self.max_length]
        x =  [self.hash(token) for token in text]
        return x

    def __len__(self):
        return len(self.samples)

    def __getitem__(self,index):
        full_sample = self.samples[index]
        sample = { 'x': full_sample['x'],
                   'i': full_sample['i'],
                   'y': full_sample['y'],
                   'text': full_sample[self.text_key]}
        return sample
