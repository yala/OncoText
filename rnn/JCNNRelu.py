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

    

class TextCNN(object):
    def __init__(self, max_length, embeddingMatrix, config):

        inps = {}
        tars = {}
        self._inps = inps
        self._tars = tars
        self._filter_sizes = config.filter_sizes
        self._filters  = config.num_filters
        self.max_length = max_length


        size = config.hidden_size
        vocab_size = config.vocab_size
        batch_size = config.batch_size

        self._keep_prob = tf.placeholder( tf.float32, name="keep_prob")

        for d in diagnoses:
            diag = diagName(d)
            inps[diag] = tf.placeholder( tf.int32, shape=(batch_size, None), name="input_"+diag)
            tars[diag] = tf.placeholder( tf.int32, shape=(batch_size, None), name="target_"+diag)
    

        with tf.device("/cpu:0"):
            self._embeddings = tf.get_variable(name="embeddings", shape=(vocab_size, config.embed_size), initializer=tf.constant_initializer(embeddingMatrix), trainable=True)
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
        self._predictions = {}
        self._correct_ans = {}

        useRelu = True
        for d in diagnoses:
            diag = diagName(d)      
            num_classes = len(constantValidLabelDict[d])
            featMap = featureMaps[diag]
            size = 160 # size of feature map

            if useRelu:
                softmax_w = tf.get_variable("sofmax_w_"+diag, [size/2, num_classes], dtype=data_type())
                softmax_b = tf.get_variable("softmax_b_"+diag, [num_classes] ,dtype=data_type())
                relu_w = tf.get_variable("relu_w_"+diag, [size, size/2], dtype=data_type())
                relu_b = tf.get_variable("relu_b_"+diag, [size/2] ,dtype=data_type())
                reluActiv = tf.matmul(featMap, relu_w) + relu_b
                relu = tf.nn.relu(reluActiv)
                logits = tf.matmul(reluActiv, softmax_w) + softmax_b
            else:
                softmax_w = tf.get_variable("sofmax_w_"+diag, [size, num_classes], dtype=data_type())
                softmax_b = tf.get_variable("softmax_b_"+diag, [num_classes] ,dtype=data_type())
                logits     = tf.matmul( featMap , softmax_w ) + softmax_b 
            probablities = tf.nn.softmax(logits)

            self._predictions[diag] = tf.argmax(probablities, axis=1)
            self._correct_ans[diag] = tf.argmax(tars[diag], axis=1)

            self._costs[diag] = tf.reduce_sum(tf.nn.softmax_cross_entropy_with_logits(logits, tars[diag], name="SoftMax"+diag))


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
                    ksize=[1, self.max_length - size + 1, 1, 1],
                    strides=[1, 1, 1, 1],
                    padding='VALID',
                    name="pool")
                pooled_outputs.append(pooled)
        # Combine all the pooled features
        num_filters_total = config.num_filters * len(config.filter_sizes)
        h_pool = tf.concat(3, pooled_outputs)
        h_pool_flat = tf.reshape(h_pool, [-1, num_filters_total])

        # Add dropout
        with tf.name_scope("dropout"):
            h_drop = tf.nn.dropout(h_pool_flat, self._keep_prob)

        return h_drop



    @property
    def tars(self):
        return self._tars

    @property
    def inps(self):
        return self._inps

    @property
    def embeddings(self):
        return self._embeddings

    @property
    def keep_prob(self):
        return self._keep_prob

    @property
    def batch_size(self):
        return self._batch_size

    @property
    def costs(self):
        return self._costs

    @property
    def predAndGold(self):
        return  self._predictions, self._correct_ans

    @property
    def joint_loss(self):
        return self._joint_loss

    @property
    def trainOp(self):
        return self._optimizer
