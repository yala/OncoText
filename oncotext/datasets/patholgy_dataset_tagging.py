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


class PathologyDatasetTagging(data.Dataset):

    def __init__(self, args, reports, label_map, text_key, name):
        self.name = name
        self.args = args
        self.diagnosis = args.aspect
        self.dataset = reports
        self.text_key = text_key
        self.samples = copy.deepcopy( self.dataset)
        self.class_balance = {'0': 0, '1': 0}
        for i, sample in tqdm.tqdm(enumerate(self.samples)):
            sample['x'], sample['y'], sample['val'], sample['match'] = self.processLine(sample)
            sample['i'] = i

            self.class_balance[sample['match']] += 1
            
        print ("Class balance", self.class_balance)
        args.num_class = args.num_tags

        self.class_balance['0'] = (self.class_balance['0'] * args.max_length) + (self.class_balance['1'] * (args.max_length - 1)) 
        weight_per_class = 1. / args.num_class
        self.weights = [ weight_per_class / self.class_balance[d['match']] for d in self.samples ]

                        
    def hash(self, token):
        """Unsigned 32 bit murmurhash for feature hashing."""
        return murmurhash3_32(token, positive=True) % self.args.vocab_size

    
    ## Convert one line from beer dataset to {Text, Tensor, Labels}
    def processLine(self, sample):
        text = sample[self.text_key].split()[:self.args.max_length]
        text_indx = [self.hash(token) for token in text]
        if len(text_indx) < self.args.max_length:
            nil_indx = 0
            text_indx.extend([nil_indx for _ in range(self.args.max_length - len(text_indx))])

        x = torch.LongTensor([text_indx])

        label_indx = [0 for _ in range(len(text_indx))]
        val = 'NA'
        match = '0'
        if self.name != "test":
            val = sample[self.diagnosis]
            if val in text:
                label_indx[text.index(val)] = 1
                match = '1'
                
        y = torch.LongTensor(label_indx)
        
        return x, y, val, match

    
    def __len__(self):
        return len(self.samples)

    
    def __getitem__(self, index):
        full_sample = self.samples[index]
        sample = { 'x': full_sample['x'],
                   'i': full_sample['i'],
                   'y': full_sample['y'],
                   'text': full_sample[self.text_key]}
        return sample
