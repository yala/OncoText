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

flags.DEFINE_string("save_path", "logs", "Model output directory")

FLAGS = flags.FLAGS

def data_type():
  return tf.float32

class TestInput(object):

    def __init__(self, path, config):
        self.data = p.load(open(path,'rb'))
        self.batch_size = Config.batch_size
        self.config = config
        self.length = len(self.data)
        self.index = 0

    def get_batch(self):
        batch = {}
        working_dict = {}
        maxLength = 0
        ## Sample sentences and find max length
        for diag in self.data.keys():
            startIndex = min( self.index, self.length - self.config.batch_size)
            batch_data = range(startIndex, startIndex + config.batch_size )
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

        self.index += self.config.batch_size 
        self.index %= self.length
        return batch, bucket

class PathInput(object):

    def __init__(self, path, config):
        self.data = p.load(open(path,'rb'))
        self.batch_size = Config.batch_size
        self.config = config

    def get_batch(self):
        batch = {}
        maxLength = 0
        ## Sample sentences and find max length
        
        batch_data = np.random.choice(len(self.data[diag][0]), self.batch_size)
        lens =  np.array([ len(self.data[diag][0][i]) for i in batch_data], dtype=np.int32 )
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
        for diag in self.data.keys():
            batch_data = working_arr
            inp = np.array([ np.hstack( [ \
                self.data[i]['NN_Text'], np.zeros(bucket-len(self.data[diag][0][i]))] \
                ) for i in batch_data], dtype=np.int32)
            tar = np.array([ self.data[i][diag] for i in batch_data], dtype=np.int32)
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
            'trainOp': models[bucket].trainOp,
            'precision': models[bucket].precision, 
            'recall': models[bucket].recall
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
            ( i  / epoch_size , costs / (i+1),
              (time.time() - start_time) )
            )
        if i == 0:
            for d in diagnoses:
                diag = diagName(d)
                print(d + " %.3f precision: %.3f recall:" %
                ( vals['precision'][diag], vals['recall'][diag]  )
            )

    return costs/epoch_size


def run_eval_epoch(session, models, dev_input, config, verbose = True):
    epoch_size = dev_input.length // config.batch_size
    start_time = time.time()

    costs = 0.0

    for i in range(epoch_size):
        batch, bucket = dev_input.get_batch()


        fetch = {
            'joint_loss':models[bucket].joint_loss,
            'predAndGold':models[bucket].predAndGold
        }

        feed_dict= {
            models[bucket].embeddings : embeddings
        }
        for d in diagnoses:
            diag = diagName(d)
            feed_dict[ models[bucket].inps[diag] ] = batch[d][0]
            feed_dict[ models[bucket].tars[diag] ] = batch[d][1]

        vals = session.run(fetch, feed_dict=feed_dict)
        pred, gold = vals['predAndGold']
        print("pred")
        print(pred)
        print("gold")
        print(gold)

        cost = vals['joint_loss']

        costs += cost

    costs /= epoch_size
    print("Dev cost", costs)
    return 0


def main(_):
    trainPath = 'diagDictTrain.p'
    devPath = 'devReps.p'


    config = Config()
    train_input  = PathInput(trainPath, config)
    dev_input = TestInput(devPath, config)
    with tf.Graph().as_default():
        initializer = tf.random_uniform_initializer(-1*config.init_scale, config.init_scale)
        models = {}
        for i, bucket in enumerate(config.bucket_lengths):
            with tf.variable_scope("JCNN", reuse= (None if i == 0 else True), initializer = initializer) :
                models[bucket] = TextCNN(max_length=bucket, config=config)
        

        for d in diagnoses:
            diag = diagName(d)      
            diagLoss = tf.reduce_sum(tf.pack([models[b].costs[diag] for b in config.bucket_lengths]))

            tf.scalar_summary(diag+" Loss", diagLoss)

        jointLoss = tf.reduce_sum(tf.pack([models[b].joint_loss for b in config.bucket_lengths]))
        tf.scalar_summary("Joint Loss", jointLoss )

        sessConf = tf.ConfigProto(
            allow_soft_placement=False,
            log_device_placement=True) 

        
        sv = tf.train.Supervisor(logdir=FLAGS.save_path)
        with sv.managed_session(config=sessConf) as session:
            ### run regular adversarial training
            for i in range(config.max_epoch):

                print("Epoch: %d " % (i + 1))
                train_cost  = run_epoch(session, models, train_input, config)
                print("Epoch: %d Train Error: %.3f" % (i + 1, train_cost))
                run_eval_epoch(session, models, dev_input, config)

                if FLAGS.save_path:
                    print("Saving model to %s." % FLAGS.save_path)
                    sv.saver.save(session, 'jointRnn', global_step=i)



if __name__ == "__main__":

    tf.app.run()
    
