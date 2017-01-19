from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import cPickle as p
import tensorflow as tf
import time
import numpy as np
from JCNN import *
import sys
sys.path.append("..")
from constants import *

flags = tf.flags
logging = tf.logging
embeddings = p.load(open('embeddings.p','rb'))

def data_type():
  return tf.float32

class PathInput(object):

    def __init__(self, path, config):
        self.data = p.load(open(path,'rb'))
        self.batch_size = Config.batch_size
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
                self.data[diag][0][i], np.zeros(bucket-len(self.data[diag][0][i]))] \
                ) for i in batch_data], dtype=np.int32)
            tar = np.array([ self.data[diag][1][i] for i in batch_data], dtype=np.int32)
            batch[diag] = inp, tar
        return batch, bucket

class Config(object):
    init_scale = 0.1
    learning_rate = 1.0
    num_layers = 1
    max_grad_norm = 5
    embed_size = 100
    hidden_size = 100
    max_epoch = 100
    keep_prob = 1.0
    batch_size = 1
    vocab_size = 17082
    epoch_size = 1000
    filter_sizes = [1,3,5,7,9]
    bucket_lengths = [250,350,500,750,2600]
    num_filters = 32
    diagnoses = diagnoses

def run_epoch(session, models, train_input, config, verbose = True):
    epoch_size = 1000
    start_time = time.time()

    costs = 0.0

    for i in range(epoch_size):
        batch, bucket = train_input.get_batch()


        fetch = {
            'joint_loss':models[bucket].joint_loss,
            'trainOp': models[bucket].trainOp
        }

        feed_dict= {
            models[bucket].embeddings : embeddings
        }
        for d in diagnoses:
            diag = diagName(d)
            feed_dict[ models[bucket].inps[diag] ] = batch[d][0]
            feed_dict[ models[bucket].tars[diag] ] = batch[d][1]

        vals = session.run(fetch, feed_dict=feed_dict)

        cost = vals['joint_loss']

        costs += cost

    if i % 100 == 0:
        print("%.3f cost: %.3f speed: %.0f ms" %
        ( step * 1.0 , costs / i+1,
          (time.time() - start_time) )
        )

    return costs/epoch_size


def run_eval_epoch():
    return 0


def main(_):
    trainPath = 'diagDictTrain.p'
    # validPath = '../ReportDB+test.p'


    config = Config()
    train_input  = PathInput(trainPath, config)
        
    initializer = tf.random_uniform_initializer(-1*config.init_scale, config.init_scale)
    models = {}
    for i, bucket in enumerate(config.bucket_lengths):
        with tf.variable_scope("JCNN", reuse= (None if i == 0 else True), initializer = initializer) :
            models[bucket] = TextCNN(max_length=bucket, config=config)
    

    for d in diagnoses:
        diag = diagName(d)      
        diagLoss = tf.reduce_sum(tf.pack([models[b].costs[diag] for b in config.bucket_lengths]))

        tf.scalar_summary(diag+" Loss", diagLoss)

    jointLoss = tf.reduce_sum(tf.pack([models[b].joint_loss[diag] for b in config.bucket_lengths]))
    tf.scalar_summary("Joint Loss", jointLoss )


    saver = tf.train.Saver(tf.all_variables())
    session = tf.Session()
    session.run(tf.initialize_all_variables())
    ### run regular adversarial training
    for i in range(config.max_epoch):

        print("Epoch: %d " % (i + 1))
        train_cost  = run_epoch(session, models, train_input, config)
        print("Epoch: %d Train Error: %.3f" % (i + 1, train_cost))
        # valid_cost  = run_eval_epoch(session, model, valid_input, train_input.epoch_size)
        # print("Epoch: %d Valid Perplexity: %.3f" % (i + 1, valid_perplexity) ) 

        if FLAGS.save_path:
            print("Saving model to %s." % FLAGS.save_path)
            saver.save(session, 'jointRnn', global_step=i)



if __name__ == "__main__":

    tf.app.run()
    
