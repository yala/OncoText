from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import pdb
import re
import time

import numpy as np
import tensorflow as tf
import sys
sys.path.append("..")

from constants import *

def data_type():
  return tf.float32

def diagName(d):
    diag = "_".join(d.split())
    diag = re.sub(r'\W','',diag)
    return diag


# Given tensor of shape [batch_size, None, Hidden], get out last hiddens, aka tensor of [batch_size, Hidden]
def getLastOutput(output):#s, inp, lens, batch_size):
    output_rs = tf.transpose(output,[1,0,2])
    return output_rs[-1]
    

class TextCNN(object):
    def __init__(self, is_training, config):

        inps = {}
        tars = {}
        lens = {}
        self._inps = inps
        self._tars = tars
        self._lens = lens
        self._filter_sizes = config.filter_sizes
        self.b_filters  = config.num_filters


        size = config.hidden_size
        vocab_size = config.vocab_size
        batch_size = config.batch_size


        for d in diagnoses:
            diag = diagName(d)
            inps[diag] = tf.placeholder( tf.int32, shape=(batch_size, None), name="input_"+diag)
            tars[diag] = tf.placeholder( tf.int32, shape=(batch_size, None), name="target_"+diag)
            lens[diag] = tf.placeholder( tf.int32, shape=(batch_size), name="lens_"+diag)
    

        with tf.device("/cpu:0"):
            self._embeddings = tf.placeholder( data_type(), shape=(vocab_size, config.embed_size), name="embeddings" )
            embedding = self._embeddings

        inputs = {}
        featureMaps = {}

        for i,d in enumerate(diagnoses):
            diag = diagName(d)
            inputs_reg =  tf.nn.embedding_lookup(embedding, inps[diag])
            inputs[diag] = tf.expand_dims(inputs_reg, -1)


            if i == 0:
                with tf.variable_scope("SharedCNN", reuse=None):
                    featureMaps[diag] = self.buildCNN(inputs[diag], config)                        
            else:                    
                with tf.variable_scope("SharedCNN", reuse=True):
                    featureMaps[diag] = self.buildCNN(inputs[diag], config)

        self._costs = {}
        self._precisions = {}
        self._recalls = {}


        for d in diagnoses:
            diag = diagName(d)      
            num_classes = len(constantValidLabelDict[d])
            featMap = featureMaps[diag]
            size = tf.shape(featMap)[1]

            softmax_w = tf.get_variable("sofmax_w_"+diag, [size, num_classes], dtype=data_type())
            softmax_b = tf.get_variable("softmax_b_"+diag, [num_classes] ,dtype=data_type())

            
            logits     = tf.matmul( featMap , softmax_w ) + softmax_b 
            probablities = tf.nn.softmax(logits)

            predictions = tf.argmax(probablities, axis=1)
            correct_ans = tf.argmax(tars[diag], axis=1)

            self._costs[diag] = tf.nn.softmax_cross_entropy_with_logits(logits, tars[diag], name="SoftMax"+diag)
            self._precisions[diag] = tf.contrib.metrics.streaming_precision(predictions, correct_ans, name="recall_"+diag)                            
            self._recalls[diag] = tf.contrib.metrics.streaming_recall(predictions, correct_ans, name="precision_"+diag )


        self._joint_loss  =  tf.reduce_sum( tf.pack([self._costs[diagName(d)] for d in diagnoses]) )
        



        self._optimizer = tf.train.AdamOptimizer().minimize(self._joint_loss)
    
    
    def buildCNN(self, inputText, config):
        pooled_outputs = []
        for size in config.filter_sizes:
            with tf.name_scope("conv-maxpool-%s" % size):
                # Convolution Layer
                filter_shape = [size, config.embed_size, 1, config.num_filters]
                W = tf.Variable(tf.truncated_normal(filter_shape, stddev=0.1), name="W")
                b = tf.Variable(tf.constant(0.1, shape=[config.num_filters]), name="b")
                pdb.set_trace()
                conv = tf.nn.conv2d(
                    inputText,
                    W,
                    strides=[1, 1, 1, 1],
                    padding="VALID",
                    name="conv")
                # Apply nonlinearity
                h = tf.nn.relu(tf.nn.bias_add(conv, b), name="relu")
                # Maxpooling over the outputs
                pooled = tf.nn.max_pool(
                    h,
                    size=[1, tf.shape(inputText)[1] - size + 1, 1, 1],
                    strides=[1, 1, 1, 1],
                    padding='VALID',
                    name="pool")
                pooled_outputs.append(pooled)
        # Combine all the pooled features
        num_filters_total = config.num_filters * len(config.filter_sizes)
        h_pool = tf.concat(3, pooled_outputs)
        h_pool_flat = tf.reshape(self.h_pool, [-1, num_filters_total])

        # Add dropout
        with tf.name_scope("dropout"):
            h_drop = tf.nn.dropout(self.h_pool_flat, self.dropout_keep_prob)

        return h_drop



    @property
    def tars(self):
        return self._tars

    @property
    def lens(self):
        return self._lens

    @property
    def inps(self):
        return self._inps

    @property
    def embeddings(self):
        return self._embeddings

    @property
    def batch_size(self):
        return self._batch_size

    @property
    def costs(self):
        return self._costs

    @property
    def joint_loss(self):
        return self._joint_loss


    @property
    def precision(self):
        return self._precisions

    @property
    def recall(self):
        return self._recalls

    @property
    def trainOp(self):
        return self._optimizer
