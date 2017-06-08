from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import cPickle as p
import numpy as np
import sys
sys.path.append("..")
from constants import *


class PathInput(object):

    def __init__(self, path, config):
        self.data = p.load(open(path,'rb'))
        self.batch_size = config.batch_size
        self.config = config

    def get_batch(self):
        batch = {}
        working_dict = {}
        maxLength = 0
        ## Sample sentences and find max length
        for diag in self.data.keys():
            batch_data = np.random.choice(len(self.data[diag][0]), self.batch_size)
            lens =  np.array([ len(self.data[diag][0][i]) for i in batch_data], dtype=np.int32 )
            maxSentLength = np.max(lens)
            if maxSentLength > maxLength:
                maxLength = maxSentLength
            working_dict[diag] = batch_data

        # Find bucket length for this batch
        bucket = self.config.bucket_lengths[0]  
        for b in self.config.bucket_lengths:
            if maxLength < b:
                bucket = b
                break

        # pad all sentences to match bucket length
        for diag in self.data.keys():
            batch_data = working_dict[diag]
            inp = np.array([ np.hstack( [ \
                    self.data[diag][0][i][0][:bucket], np.zeros(bucket-len(self.data[diag][0][i][0]))] \
                ) for i in batch_data], dtype=np.int32)
            tar = np.array([ self.data[diag][1][i] for i in batch_data], dtype=np.int32)
            assert inp.shape[-1] == bucket
            batch[diag] = inp, tar

        return batch, bucket

class TestInput(object):

    def __init__(self, path, config):
        self.data = p.load(open(path,'rb'))
        self.batch_size = config.batch_size
        self.config = config
        self.length = len(self.data)
        self.index = 0

    def get_batch(self):
        batch = {}
        maxLength = 0
        ## Sample sentences and find max length
        startIndex = min( self.index, self.length - self.config.batch_size)
        batch_data = range(startIndex, startIndex + self.config.batch_size )

        lens =  np.array([ len(self.data[i]['NN_Text']) for i in batch_data], dtype=np.int32 )
        maxSentLength = np.max(lens)
        if maxSentLength > maxLength:
            maxLength = maxSentLength
        working_arr = batch_data

        # Find bucket length for this batch
        bucket = self.config.bucket_lengths[0]  
        for b in self.config.bucket_lengths:
            if maxLength < b:
                bucket = b
                break

        # pad all sentences to match bucket length
        for diag in nn_diagnoses:
            batch_data = working_arr
            inp = np.array([ np.hstack( [ \
                self.data[i]['NN_Text'], np.zeros(bucket-len(self.data[i]['NN_Text']))] \
                ) for i in batch_data], dtype=np.int32)
            try:
                tar = np.array([ self.data[i][diag] for i in batch_data], dtype=np.int32)
            except Exception, e:
                print(batch_data)

                print(diag)
                print( [ self.data[i][diag] for i in batch_data])
                print( [ self.data[i][diag] for i in batch_data])
                raw_input()

            batch[diag] = inp, tar

        self.index += self.config.batch_size 
        self.index %= self.length
        return batch, bucket

class UnlabledInput(object):

    def __init__(self, path, config):
        self.data = p.load(open(path,'rb'))
        evalOnly = True
        if evalOnly:
            self.data = [d for d in self.data if ('test_set' in d and d['test_set'] ) or ('pakistani' in d and d['pakistani'] )]
        self.batch_size = config.batch_size
        self.config = config
        self.length = len(self.data)
        self.index = 0

    def get_batch(self):
        batch = {}
        maxLength = 0
        ## Sample sentences and find max length
        startIndex = min( self.index, self.length - self.config.batch_size)
        batch_data = range(startIndex, startIndex + self.config.batch_size )

        lens =  np.array([ len(self.data[i]['NN_Text']) for i in batch_data], dtype=np.int32 )
        maxSentLength = np.max(lens)
        if maxSentLength > maxLength:
            maxLength = maxSentLength
        working_arr = batch_data

        # Find bucket length for this batch
        bucket = self.config.bucket_lengths[0]  
        for b in self.config.bucket_lengths:
            if maxLength < b:
                bucket = b
                break

        # pad all sentences to match bucket length
        for diag in nn_diagnoses:
            batch_data = working_arr
            inp = np.array([ np.hstack( [ \
                self.data[i]['NN_Text'][:bucket], \
		np.zeros(max(0,bucket-len(self.data[i]['NN_Text'])))] \
                ) for i in batch_data], dtype=np.int32)
            try:
                tar = np.array([ self.data[i][diag] for i in batch_data], dtype=np.int32)
            except Exception, e:
                print(batch_data)

                print(diag)
                print( [ self.data[i][diag] for i in batch_data])
                print( [ self.data[i][diag] for i in batch_data])
                raw_input()

            batch[diag] = inp, tar

        reports = [ self.data[i] for i in batch_data]

        self.index += self.config.batch_size 
        self.index %= self.length
        return batch, reports, bucket
