from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import cPickle as p
import tensorflow as tf
import time
import numpy as np
from JGRU import *
import sys
sys.path.append("..")
from constants import *

flags = tf.flags
logging = tf.logging
embeddings = p.load(open('embeddings.p','rb'))

def data_type():
  return tf.float32

class PathInput(object):

    def __init__(self, path, Config):
        self.data = p.load(open(path,'rb'))
        self.batch_size = Config.batch_size

    def get_batch(self):
        batch = {}
        for diag in self.data.keys():

            batch_data = np.random.choice(len(self.data[diag][0]), self.batch_size)
            inp = np.array([ self.data[diag][0][i] for i in batch_data], dtype=np.int32)
            tar = np.array([ self.data[diag][1][i] for i in batch_data], dtype=np.int32)
            batch[diag] = inp, tar
        return batch

class Config(object):
    init_scale = 0.1
    learning_rate = 1.0
    num_layers = 1
    max_grad_norm = 5
    embed_size = 100
    hidden_size = 100
    max_epoch = 100
    keep_prob = 1.0
    batch_size = 20
    vocab_size = 17082
    epoch_size = 1000
    diagnoses = diagnoses

def run_epoch(session, model, train_input, verbose = True):
    epoch_size = 1000
    start_time = time.time()

    costs = 0.0

    for i in range(epoch_size):
        batch = train_input.get_batch()

        fetch = {
            'joint_loss':model.joint_loss,
            'trainOp': model.trainOp
        }

        feed_dict= {
            model.embeddings : embeddings
        }
        for d in diagnoses:
            diag = diagName(d)
            feed_dict[ model.inps[diag] ] = batch[d][0]
            feed_dict[ model.tars[diag] ] = batch[d][1]

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
    
    with tf.Graph().as_default():
        initializer = tf.random_uniform_initializer(-1*config.init_scale, config.init_scale)
    
        with tf.variable_scope("JGRU", reuse=None, initializer = initializer) :
            model = JGRU(is_training=True, config=config)
        
        for d in diagnoses:
            diag = diagName(d)      
            tf.scalar_summary(diag+" Loss", model.costs[diag])

        tf.scalar_summary("Joint Loss", model.joint_loss)

        sessConf = tf.ConfigProto(
            allow_soft_placement=False,
            log_device_placement=True) 

        sv = tf.train.Supervisor(logdir='logs')
        with sv.managed_session(config=sessConf) as session:     

          ### run regular adversarial training
          for i in range(config.max_epoch):

            print("Epoch: %d " % (i + 1))
            train_cost  = run_epoch(session, model, train_input)
            print("Epoch: %d Train Error: %.3f" % (i + 1, train_cost))
            # valid_cost  = run_eval_epoch(session, model, valid_input, train_input.epoch_size)
            # print("Epoch: %d Valid Perplexity: %.3f" % (i + 1, valid_perplexity) ) 

          if FLAGS.save_path:
            print("Saving model to %s." % FLAGS.save_path)
            sv.saver.save(session, FLAGS.save_path, global_step=sv.global_step)



if __name__ == "__main__":

    tf.app.run()
    
