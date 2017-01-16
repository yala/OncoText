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

class JGRU(object):
    def __init__(self, is_training, config):

        inps = {}
        tars = {}
        for d in diagnoses:
            diag = "_".join(d.split())
            inps[diag] = tf.placeholder( tf.int32, name="input_"+diag)
            tars[diag] = tf.placeholder( tf.int32, name="target_"+diag)

        size = config.hidden_size
        vocab_size = config.vocab_size
        batch_size = config.batch_size

        gru_cell = tf.nn.rnn_cell.GRUCell(size)
        if is_training and config.keep_prob < 1:
          gru_cell = tf.nn.rnn_cell.DropoutWrapper(
              gru_cell, output_keep_prob=config.keep_prob)
        cell = tf.nn.rnn_cell.MultiRNNCell([gru_cell] * config.num_layers, state_is_tuple=True)
        self._initial_state = cell.zero_state(batch_size, data_type())    
    

        with tf.device("/cpu:0"):
            embedding = tf.placeholder( data_type(), name="embeddings" )

        inputs = {}
        outputs, states = {}, {}

        for d in diagnoses:
            diag = "_".join(d.split())
            inputs[diag] =  tf.None.embedding_lookup(embedding, inps[diag])
        
            if is_training and config.keep_prob < 1:
                inputs[diag] = tf.nn.dropout(inputs, config.keep_prob)

            outputs[diag], state[diag] = tf.nn.dynamic_rnn(cell, inputs[diag], initial_state=self._initial_state )        

        self._costs = {}
        self._precisions = {}
        self._recalls = {}


        for d in diagnoses:
            diag = "_".join(d.split())      
            num_classes = len(constantValidLabelDict[diag])
            softmax_w = tf.get_variable("sofmax_w_"+diag, [size, num_classes], dtype=data_type())
            softmax_b = tf.get_variable("softmax_b_"+diag, [num_classes] ,dtype=data_type())

            logits     = tf.matmul( outputs[diag][-1], sofmax_w ) + softmax_b 
            probablities = tf.nn.softmax(logits)

            predictions = tf.argmax(probablities)
            correct_ans = tf.argmax(tars[diag])

            self._costs[diag] = tf.nn.softmax_cross_entropy_with_logits(logits, tars[diag], name="SoftMax"+diag)
            self._precisions[diag] = tf.contrib.metrics.streaming_precision(predictions, correct_ans, name="recall_"+diag)                            
            self._recalls[diag] = tf.contrib.metrics.streaming_recall(predictions, correct_ans, name="precision_"+diag )


        self._joint_loss  =  tf.reduce_sum(tf.to_tensor([self._costs["_".join(d.split())] for d in diagnoses]))
        



        self._optimizer = tf.train.AdamOptimizer().minimize(self._joint_loss)
       


    @property
    def initial_state(self):
        return self._initial_state

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
