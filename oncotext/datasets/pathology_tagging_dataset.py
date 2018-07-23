import torch
import torch.utils.data as data
import gzip
import tqdm
import pickle
import json
import pdb
from rationale_net.datasets.abstract_dataset import AbstractDataset
import rationale_net.utils.embedding as utils
import random
import copy
from sklearn.utils import murmurhash3_32

SMALL_TRAIN_SIZE = 800
random.seed(0)


class PathologyTaggingDataset(data.Dataset):

    def __init__(self, args, reports, label_map, text_key, name):
        self.name = name
        self.args = args
        self.diagnosis = args.aspect
        self.dataset = reports
        self.text_key = text_key
        self.samples = copy.deepcopy(self.dataset)
        ## class_balance['0']: how many reports did not have an exact match for the label in the report text (y tensor is all 0)
        ## class_balance['1']: how many reports had 1 or more exact matches for the label, or parts of the label, in the report text (y tensor has 1(s)) 
        self.class_balance = {'0': 0, '1': 0}

        for i, sample in tqdm.tqdm(enumerate(self.samples)):
            sample['x'], sample['y'], sample['val'], sample['match'] = self.processLine(sample)
            sample['i'] = i
            self.class_balance[sample['match']] += 1
            
        print ("Class balance", self.class_balance)
        args.num_class = args.num_tags

                        
    def hash(self, token):
        """Unsigned 32 bit murmurhash for feature hashing."""
        return murmurhash3_32(token, positive=True) % self.args.vocab_size

    
    ## Convert each sample to {x, y, label, match}, where
    ## x: tensor of text tokens
    ## y: tensor of [1 if token matches label, else 0, for each token in x]
    ## label: original value of label
    ## match: '0' if label not in text, '1' if it is
    def processLine(self, sample):
        text = sample[self.text_key].split()[:self.args.max_length]
        text_indx = [self.hash(token) for token in text]
        if len(text_indx) < self.args.max_length:
            nil_indx = 0
            text_indx.extend([nil_indx for _ in range(self.args.max_length - len(text_indx))])

        x = torch.LongTensor([text_indx])

        label_indx = [0 for _ in range(len(text_indx))]

        if self.name == "test":
            label = 'NA'
            match = '0'
        else:
            label = sample[self.diagnosis]
            ## array of values in the label (for when the label spans multiple tokens)
            val = label.split()
            match = '0'
            ## for each token in text, if the following tokens match the label, set each corresponding index in y to 1
            for i in range(len(text)):
                if text[i:i+len(val)] == val:
                    match = '1'
                    label_indx[i:i+len(val)] = [1 for _ in range(len(val))]
                    
        y = torch.LongTensor(label_indx)
        
        return x, y, label, match

    
    def __len__(self):
        return len(self.samples)

    
    def __getitem__(self, index):
        full_sample = self.samples[index]
        sample = { 'x': full_sample['x'],
                   'i': full_sample['i'],
                   'y': full_sample['y'],
                   'text': full_sample[self.text_key]}
        return sample
