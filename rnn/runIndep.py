from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import cPickle as p
import tensorflow as tf
import time
import numpy as np
from ICNN import *
import sys
sys.path.append("..")
from constants import *
from evalHelper import *

flags = tf.flags
logging = tf.logging
embeddings = p.load(open('embeddings.p','rb'))

flags.DEFINE_string("save_path", "logs", "Model output directory")

FLAGS = flags.FLAGS

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

class TestInput(object):

    def __init__(self, path, config):
        self.data = p.load(open(path,'rb'))
        self.batch_size = Config.batch_size
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
        for diag in diagnoses:
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
    bucket_lengths = [2600]
    num_filters = 32
    diagnoses = diagnoses

def run_epoch(session, models, train_input, config, verbose = True):
    epoch_size = 500
    start_time = time.time()

    costs = 0.0
    preds, golds = [], []
    for i in range(epoch_size):
        batch, bucket = train_input.get_batch()


        fetch = {
            'joint_loss':models[bucket].joint_loss,
            'trainOp': models[bucket].trainOp,
            'predAndGold':models[bucket].predAndGold
        }

        feed_dict= {
            models[bucket].keep_prob: .50
        }
        for d in diagnoses:
            diag = diagName(d)
            feed_dict[ models[bucket].inps[diag] ] = batch[d][0]
            feed_dict[ models[bucket].tars[diag] ] = batch[d][1]

        vals = session.run(fetch, feed_dict=feed_dict)
        pred, gold = vals['predAndGold']
        preds.append(pred)
        golds.append(gold)
        cost = vals['joint_loss']

        costs += cost

        if i % 100 == 0 and i > 0:
            print("%.3f cost: %.3f speed: %.0f ms" %
            ( i  / epoch_size , costs / (i+1),
              (time.time() - start_time) )
            )

    allVars = session.run(tf.trainable_variables())
    norm = np.linalg.norm(np.array([np.linalg.norm(v) for v in allVars]))
    print("Param norm", norm)
    print("TRAIN MINIBATCH STATS")
    evaluate(preds, golds)


    return costs/epoch_size
            

def run_eval_epoch(session, models, dev_input, config, verbose = True):
    epoch_size = dev_input.length // config.batch_size
    start_time = time.time()

    costs = 0.0
    preds = []
    golds = []
    allVars = session.run(tf.trainable_variables())
    norm = np.linalg.norm(np.array([np.linalg.norm(v) for v in allVars]))
    print("Param norm", norm)
    for i in range(epoch_size):
        batch, bucket = dev_input.get_batch()


        fetch = {
            'joint_loss':models[bucket].joint_loss,
            'predAndGold':models[bucket].predAndGold
        }

        feed_dict= {
            models[bucket].keep_prob:  1.0
        }
        for d in diagnoses:
            diag = diagName(d)
            feed_dict[ models[bucket].inps[diag] ] = batch[d][0]
            feed_dict[ models[bucket].tars[diag] ] = batch[d][1]

        vals = session.run(fetch, feed_dict=feed_dict)
        pred, gold = vals['predAndGold']
        preds.append(pred)
        golds.append(gold)

        cost = vals['joint_loss']

        costs += cost

    costs /= epoch_size
    print("Dev cost", costs)
    evaluate(preds, golds)
    return 0




def main(_):
    trainPath = 'diagDictTrain.p'
    devPath = 'devReps.p'

    print("save_path", FLAGS.save_path)

    config = Config()
    train_input  = PathInput(trainPath, config)
    dev_input = TestInput(devPath, config)
    with tf.Graph().as_default():
        initializer = tf.random_uniform_initializer(-1*config.init_scale, config.init_scale)
        models = {}
        for i, bucket in enumerate(config.bucket_lengths):
            with tf.variable_scope("JCNN", reuse= (None if i == 0 else True), initializer = initializer) :
                models[bucket] = TextCNN(max_length=bucket, config=config, embeddingMatrix=embeddings)
        

        for d in diagnoses:
            diag = diagName(d)      
            diagLoss = tf.reduce_sum(tf.pack([models[b].costs[diag] for b in config.bucket_lengths]))

            tf.scalar_summary(diag+" Loss", diagLoss)

        jointLoss = tf.reduce_sum(tf.pack([models[b].joint_loss for b in config.bucket_lengths]))
        tf.scalar_summary("Joint Loss", jointLoss )

        sessConf = tf.ConfigProto(
            allow_soft_placement=False,
            log_device_placement=True) 

        
        sv = tf.train.Supervisor(logdir=FLAGS.save_path, summary_op=None)
        with sv.managed_session(config=sessConf) as session:
            ### run regular adversarial training
            for i in range(config.max_epoch):

                print("Epoch: %d " % (i + 1))

                print("EVAL")
                run_eval_epoch(session, models, dev_input, config)
                
                print("TRAIN")
                train_cost  = run_epoch(session, models, train_input, config)
                print("Epoch: %d Train Error: %.3f" % (i + 1, train_cost))

                if FLAGS.save_path:
                    print("Saving model to %s." % FLAGS.save_path)
                    sv.saver.save(session, 'jointRnn', global_step=i)



if __name__ == "__main__":
    tf.app.run()
    
