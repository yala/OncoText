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
    # #Code adapted from @mrry response in StackOverflow:
    # #http://stackoverflow.com/questions/36088277/how-to-select-rows-from-a-3-d-tensor-in-tensorflow
    # rows_per_batch = tf.shape(inp)[1]
    # indices_per_batch = 1

    # # Offset to add to each row in indices. We use `tf.expand_dims()` to make 
    # # this broadcast appropriately.
    # offset = tf.range(0, batch_size) * rows_per_batch

    # # Convert indices and logits into appropriate form for `tf.gather()`. 
    # flattened_indices = lens - 1 + offset
    # flattened_sequence_outputs = tf.reshape( outputs, tf.concat(0, [[-1],
    #                      tf.shape(outputs)[2:]]))

    # selected_rows = tf.gather(flattened_sequence_outputs, flattened_indices)
    # last_output  = tf.reshape(selected_rows,
    #                   tf.concat(0, [tf.pack([batch_size, indices_per_batch]),
    #                   tf.shape(outputs)[2:]]))
    pdb.set_trace()

    # Let's first fetch the last index of seq length
    # last_index would have a scalar value
    last_index = tf.shape(output)[1] - 1
    # Then let's reshape the output to [sequence_length,batch_size,num_units]
    # for convenience
    output_rs = tf.transpose(output,[1,0,2])
    # Last state of all batches
    last_state = tf.nn.embedding_lookup(output_rs,last_index)
    return last_state

class JGRU(object):
    def __init__(self, is_training, config):

        inps = {}
        tars = {}
        lens = {}

        size = config.hidden_size
        vocab_size = config.vocab_size
        batch_size = config.batch_size


        for d in diagnoses:
            diag = diagName(d)
            inps[diag] = tf.placeholder( tf.int32, shape=(batch_size, None), name="input_"+diag)
            tars[diag] = tf.placeholder( tf.int32, shape=(batch_size, None), name="target_"+diag)

        gru_cell = tf.nn.rnn_cell.GRUCell(size)
        if is_training and config.keep_prob < 1:
          gru_cell = tf.nn.rnn_cell.DropoutWrapper(
              gru_cell, output_keep_prob=config.keep_prob)

        cell = tf.nn.rnn_cell.MultiRNNCell([gru_cell] * config.num_layers, state_is_tuple=True)
        self._initial_state = cell.zero_state(batch_size, data_type())    
    

        with tf.device("/cpu:0"):
            embedding = tf.placeholder( data_type(), shape=(vocab_size, config.embed_size), name="embeddings" )

        inputs = {}
        outputs, states = {}, {}

        for i,d in enumerate(diagnoses):
            diag = diagName(d)
            inputs[diag] =  tf.nn.embedding_lookup(embedding, inps[diag])

            if is_training and config.keep_prob < 1:
                inputs[diag] = tf.nn.dropout(inputs, config.keep_prob)

            if i == 0:
                with tf.variable_scope("DynamicRNN", reuse=None):
                    outputs[diag], states[diag] = tf.nn.dynamic_rnn(cell, inputs[diag], initial_state=self._initial_state )       
            else:                    
                with tf.variable_scope("DynamicRNN", reuse=True):
                    outputs[diag], states[diag] = tf.nn.dynamic_rnn(cell, inputs[diag], initial_state=self._initial_state )        

        self._costs = {}
        self._precisions = {}
        self._recalls = {}


        for d in diagnoses:
            diag = diagName(d)      
            num_classes = len(constantValidLabelDict[d])
            softmax_w = tf.get_variable("sofmax_w_"+diag, [size, num_classes], dtype=data_type())
            softmax_b = tf.get_variable("softmax_b_"+diag, [num_classes] ,dtype=data_type())

            lastOut = getLastOutput(outputs[diag])
            logits     = tf.matmul( lastOut , softmax_w ) + softmax_b 
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
