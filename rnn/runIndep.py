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
from inputClasses import *
flags = tf.flags
logging = tf.logging
embeddings = p.load(open('embeddings.p','rb'))

flags.DEFINE_string("save_path", "logs", "Model output directory")

FLAGS = flags.FLAGS

def data_type():
  return tf.float32


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
    nn_diagnoses = nn_diagnoses

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
        for d in nn_diagnoses:
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
    inputStrs = []
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
        for d in nn_diagnoses:
            diag = diagName(d)
            feed_dict[ models[bucket].inps[diag] ] = batch[d][0]
            feed_dict[ models[bucket].tars[diag] ] = batch[d][1]

        vals = session.run(fetch, feed_dict=feed_dict)
        pred, gold = vals['predAndGold']
        preds.append(pred)
        golds.append(gold)
        inputStrs.append(batch[nn_diagnoses[0]][0])

        cost = vals['joint_loss']

        costs += cost

    costs /= epoch_size
    print("Dev cost", costs)
    evaluate(preds, golds, inputStrs)
    return 0

def label_dataset(session, models, unlabled_input, config, verbose=True):

    costs = 0.0
    
    print("Param norm", norm)
    lenData = len(dev_input.data)
    allReps = []
    for i in range(lenData):
        batch, reports, bucket = dev_input.get_batch()

        fetch = {
            'predAndGold':models[bucket].predAndGold
        }

        feed_dict= {
            models[bucket].keep_prob:  1.0
        }

        reports = {}
        for d in nn_diagnoses:
            diag = diagName(d)
            feed_dict[ models[bucket].inps[diag] ] = batch[d][0]
            feed_dict[ models[bucket].tars[diag] ] = batch[d][1]
            reports[ diag] = batch[d][2]



        vals = session.run(fetch, feed_dict=feed_dict)
        pred, gold = vals['predAndGold']

        for k,r in enumerate(reports):
            for d in pred:
                r[d] = constantValidLabelDict[ preds[d][i][0]]

        allReps.extend(reports)

        if i %(lenData/10) == 0:
            print(i*1./ lenData)
    p.dump(allReps, open('labeledReps.p','wb'))
    return allReps


def main(_):
    trainPath = 'diagDictTrain.p'
    devPath = 'devReps.p'
    config = Config()
    unlabled_mode= True
    if unlabled_mode:
        devPath = 'unlabledReps.p'
        dev_input = UnlabledInput(devPath, config)
    else:
        devPath = 'devReps.p'
        dev_input = TestInput(devPath, config)

    print("save_path", FLAGS.save_path)

    train_input  = PathInput(trainPath, config)
    with tf.Graph().as_default():
        initializer = tf.random_uniform_initializer(-1*config.init_scale, config.init_scale)
        models = {}
        for i, bucket in enumerate(config.bucket_lengths):
            with tf.variable_scope("JCNN", reuse= (None if i == 0 else True), initializer = initializer) :
                models[bucket] = TextCNN(max_length=bucket, config=config, embeddingMatrix=embeddings)
        

        for d in nn_diagnoses:
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
            if unlabled_mode:
                label_dataset(session, models, dev_input, config, verbose=True)
            else:
                for i in range(config.max_epoch):
                    varDump =  session.run([{var.name: var} for var in tf.trainable_variables()])
                    p.dump(varDump, open('variableDict.p','wb'))
                    print( "Dumped vars")
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
    
