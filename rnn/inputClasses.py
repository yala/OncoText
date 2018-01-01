from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import cPickle as p
import numpy as np
import sys
sys.path.append("..")
from constants import *

NN_DIAGS = p.load(open('/home/nlp/pathology/rnn/diagDictTrain_mghMar.p'))
NN_DIAGS = [k for k in NN_DIAGS if len(NN_DIAGS[k][0])>0]

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
        for diag in NN_DIAGS:
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
        for diag in NN_DIAGS:
            batch_data = working_dict[diag]
            inp = []
            for i in batch_data:
                if len( self.data[diag][0][i][0]) < bucket:
                    inp.append( np.hstack( [self.data[diag][0][i][0], np.zeros( bucket - len( self.data[diag][0][i][0]) )] ) )
                else:
                    inp.append( self.data[diag][0][i][0][:bucket] )
            inp = np.array( inp, dtype=np.int32)  
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
        self.validInds = {}
        for diag in NN_DIAGS:
            self.validInds[diag] = [i for i in range(len(self.data)) if diag in self.data[i]]

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
        for diag in NN_DIAGS:
            batch_data = [self.validInds[diag][ind] for ind in working_arr if ind < len(self.validInds[diag])]
            #batch_data = working_arr
            inp = np.array([ np.hstack( [ \
                self.data[i]['NN_Text'], np.zeros(bucket-len(self.data[i]['NN_Text']))] \
                                    ) for i in batch_data], dtype=np.int32)
            try:
                tar = np.array([ self.data[i][diag] for i in batch_data], dtype=np.int32)
            except Exception, e:
                print(batch_data)
                #print(self.data[0])

                print(diag)
                print( [ self.data[i][diag] for i in batch_data])
                #print( [ self.data[i][diag] for i in batch_data])
                #raw_input()

            batch[diag] = inp, tar

        self.index += self.config.batch_size 
        self.index %= self.length
        return batch, bucket

class UnlabledInput(object):

    def __init__(self, path, config):
        self.data = p.load(open(path,'rb'))
        self.batch_size = config.batch_size
        self.config = config
        self.length = len(self.data)
        self.index = 0
        self.validInds = {}
        for diag in NN_DIAGS:
            self.validInds[diag] = [i for i in range(len(self.data)) if diag in self.data[i]]

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
        for diag in NN_DIAGS:
            batch_data = [self.validInds[diag][ind] for ind in working_arr if ind < len(self.validInds[diag])]
            #batch_data = working_arr
            inp = np.array([ np.hstack( [ \
                self.data[i]['NN_Text'][:bucket], \
		np.zeros(max(0,bucket-len(self.data[i]['NN_Text'])))] \
                                    ) for i in batch_data], dtype=np.int32)
            try:
                tar = np.array([ self.data[i][diag] for i in batch_data], dtype=np.int32)
            except Exception, e:
                print(batch_data)

                print(diag)
                print(self.data[0].keys())
                print( [ self.data[i][diag] for i in batch_data])
                #print( [ self.data[i][diag] for i in batch_data])
                #raw_input()

            batch[diag] = inp, tar

        reports = [ self.data[i] for i in batch_data ]

        self.index += self.config.batch_size 
        self.index %= self.length
        return batch, reports, bucket
