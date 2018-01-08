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


SMALL_TRAIN_SIZE = 800
random.seed(0)


class PathologyDataset(data.Dataset):

    def __init__(self, args, reports, label_map, word_to_indx, text_key, name, max_length=720):
        self.name = name
        self.args = args
        diagnosis = args.aspect
        self.word_to_indx  = word_to_indx
        self.max_length = max_length
        self.dataset = reports
        self.text_key = text_key

        self.class_balance = {}
        for i, sample in tqdm.tqdm(enumerate(self.dataset)):
            sample['x'] = self.processLine(sample[text_key])
            if name == 'test':
                 sample['y'] = 0
            else:
                sample['y'] = label_map[diagnosis].index(sample[diagnosis])
            sample['i'] = i
            val = sample[diagnosis]
            if not val in self.class_balance:
                self.class_balance[ val ] = 0
            self.class_balance[val] += 1
        print ("Class balance", self.class_balance)
        args.num_class = len(label_map)


    ## Convert one line from beer dataset to {Text, Tensor, Labels}
    def processLine(self, raw_text):
        text = raw_text.split()[:self.max_length]
        x =  utils.get_indices_tensor(text, self.word_to_indx, self.max_length)
        return x

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self,index):
        full_sample = self.dataset[index]
        sample = { 'x': full_sample['x'],
                   'i': full_sample['i'],
                   'y': full_sample['y'],
                   'text': full_sample[self.text_key]}
        return sample
