import cPickle as p
import tensorflow as tf
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import time
import numpy as np
import reader

flags = tf.flags
logging = tf.logging

def data_type():
  return tf.float32

def class pathInput(object):
 	def __init__(self, path, Config):
 		self.data = p.load(open(path,'rb'))

 	def get_batch():
 		return 0

class Config(object):
	init_scale = 0.1
	learning_rate = 1.0
	num_layers = 1
	max_grad_norm = 5
	hidden_size = 100
	max_epoch = 12
	keep_prob = 1.0
	batch_size = 100

def run_epoch():
	return 0

def run_eval_epoch():
	return 0

def main(_):
	trainPath = '../ReportDB+train.p'
	validPath = '../ReportDB+test.p'

	config = Config()

	with tf.Graph().as_default():
		initializer = tf.random_uniform_initializer(-config.init_scale,
                                                config.init_scale)
		dataLoader  = pathInput(dataPath, config)
		validLoader = pathInput(dataPath, config)



	    inp, tar = train_input.get_batch()
	    input_h = tf.convert_to_tensor(inp)
	    targets_h =tf.convert_to_tensor(tar)

	    with tf.variable_scope("JGRU", reuse=None, initializer = initializer):
		    model = JGRU(is_training=True, config=config)
	
	    tf.scalar_summary("Train Loss", model.cost)
	    tf.scalar_summary("Train Accuracy", model.accuracy)
	    tf.scalar_summary("Train F1", model.f1)

	    sessConf = tf.ConfigProto(
	        allow_soft_placement=False,
	        log_device_placement=True) 

	    sv = tf.train.Supervisor(logdir='logs')
	    with sv.managed_session(config=sessConf) as session:     

	      ### run regular adversarial training
	      for i in range(config.max_epoch):

	        print("Epoch: %d " % (i + 1))
	        train_cost  = run_epoch(session, model, train_input)
	        print("Epoch: %d Train Perplexity: %.3f" % (i + 1, train_perplexity))
	        valid_cost  = run_eval_epoch(session, model, valid_input, train_input.epoch_size)
	        print("Epoch: %d Valid Perplexity: %.3f" % (i + 1, valid_perplexity) ) 

	      if FLAGS.save_path:
	        print("Saving model to %s." % FLAGS.save_path)
	        sv.saver.save(session, FLAGS.save_path, global_step=sv.global_step)



if __name__ == "__main__":

	tf.app.run()
	
