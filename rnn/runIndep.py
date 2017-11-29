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
import warnings
from tqdm import tqdm
import pdb

warnings.filterwarnings("ignore")


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
    max_epoch = 25
    keep_prob = 1.0
    batch_size = 1
    vocab_size = 17082
    epoch_size = 1000
    filter_sizes = [1,3,5,7,9]
    bucket_lengths = [2700]
    num_filters = 32
    nn_diags = p.load(open('/home/nlp/pathology/rnn/diagDictTrain_mghMar.p'))
    nn_diags = [k for k in nn_diags if len(nn_diags[k][0])>0]

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
        for d in config.nn_diags:
            diag = diagName(d)
            feed_dict[ models[bucket].inps[diag] ] = batch[d][0]
            assert batch[d][0].shape[-1] == bucket
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
        for d in config.nn_diags:
            diag = diagName(d)
            feed_dict[ models[bucket].inps[diag] ] = batch[d][0]
            feed_dict[ models[bucket].tars[diag] ] = batch[d][1]
        
        try:
          vals = session.run(fetch, feed_dict=feed_dict)
        except ValueError:
          continue
        pred, gold = vals['predAndGold']
        preds.append(pred)
        golds.append(gold)
        inputStrs.append(batch[config.nn_diags[0]][0])

        cost = vals['joint_loss']

        costs += cost

    costs /= epoch_size
    print("Dev cost", costs)
    avg_accur = evaluate(preds, golds, inputStrs)
    return avg_accur

def label_dataset(session, models, dev_input, config, outPath='labeledReps.p', verbose=True):

    costs = 0.0
    lenData = len(dev_input.data)
    allReps = []
    for i in tqdm(range(lenData)):
        batch, reports, bucket = dev_input.get_batch()

        fetch = {
            'predAndGold':models[bucket].predAndGold
        }

        feed_dict= {
            models[bucket].keep_prob:  1.0
        }

        for d in config.nn_diags:
            diag = diagName(d)
            feed_dict[ models[bucket].inps[diag] ] = batch[d][0]
            feed_dict[ models[bucket].tars[diag] ] = batch[d][1]



        vals = session.run(fetch, feed_dict=feed_dict)
        pred, gold = vals['predAndGold']

        for k,r in enumerate(reports):
            for d in config.nn_diags:
		diag = diagName(d)
		labelInd = pred[diag][k]
                r[d] = post_diagnoses[d][labelInd]

        allReps.extend(reports)

        if i %(lenData/100) == 0:
            print(i*1./ lenData)
    p.dump(allReps, open(outPath,'wb'))
    return allReps


def main(_):
    
    n_flags = p.load(open('flags.p','rb'))
    devPath = 'devReps.p'
    config = Config()
    unlabled_mode =  n_flags['unlabled_mode']
    outPath =  n_flags['outPath'] if unlabled_mode else None
    print("flags:", n_flags)
    if unlabled_mode:
        devPath = n_flags['unlabeledPath']
        dev_input = UnlabledInput(devPath, config)
    else:
        devPath = 'devReps.p'
        dev_input = TestInput(devPath, config)
   	trainPath =  n_flags['trainPath']  
        train_input  = PathInput(trainPath, config)
    
    print("save_path", FLAGS.save_path)

    sessConf = tf.ConfigProto(allow_soft_placement=True)
    sessConf.gpu_options.allow_growth=True

    with tf.Session(config=sessConf) as session:
        initializer = tf.random_uniform_initializer(-1*config.init_scale, config.init_scale)
        models = {}
        for i, bucket in enumerate(config.bucket_lengths):
            with tf.variable_scope("JCNN", reuse= (None if i == 0 else True), initializer = initializer) :
                models[bucket] = TextCNN(max_length=bucket, config=config, embeddingMatrix=embeddings)
        

        for d in config.nn_diags:
            diag = diagName(d)      
            diagLoss = tf.reduce_sum(tf.pack([models[b].costs[diag] for b in config.bucket_lengths]))


        jointLoss = tf.reduce_sum(tf.pack([models[b].joint_loss for b in config.bucket_lengths]))

        saver = tf.train.Saver( tf.get_collection( tf.GraphKeys.TRAINABLE_VARIABLES  ) )
        if True: #temp debug statement    
            ### run regular adversarial training
            if unlabled_mode:
	        saver.restore( session,   tf.train.latest_checkpoint( FLAGS.save_path  ))	
       		eval_input = TestInput('devReps.p', config)
		run_eval_epoch(session, models, eval_input, config)
                label_dataset(session, models, dev_input, config, outPath = outPath, verbose=True)
		print("Done labeling")
            else:
                session.run( tf.global_variables_initializer() )
                max_accur = 0
                num_less = 0
                for i in range(config.max_epoch):
                    varDump =  session.run([{var.name: var} for var in tf.trainable_variables()])
                    p.dump(varDump, open('variableDict.p','wb'))
                    print( "Dumped vars")
                    print("Epoch: %d " % (i + 1))

                    print("EVAL")
                    epoch_acur = run_eval_epoch(session, models, dev_input, config)
                    
                    print("TRAIN")
                    train_cost  = run_epoch(session, models, train_input, config)
                    print("Epoch: %d Train Error: %.3f" % (i + 1, train_cost))

                    if epoch_acur >= max_accur:
                        print("Saving model to %s." % (FLAGS.save_path+'/jmodel') )
			saver.save(session, './'+FLAGS.save_path+'/jmodel' , global_step=i)
			max_accur = epoch_acur

                        num_less = 0

                    if epoch_acur < max_accur:
                        num_less += 1
                        print("num epochs without improve on dev", num_less)
                   
                    if num_less >= 3:
                         break



if __name__ == "__main__":
    runSolo = False
    if runSolo:
        neuralFlags = { 'unlabled_mode':False, 'trainPath':'diagDictTrain_mghMar.p'}
        p.dump( neuralFlags, open('flags.p','wb'))
    tf.app.run()
    
