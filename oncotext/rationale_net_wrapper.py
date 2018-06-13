import logging
import torch
import torch.autograd as autograd
import rationale_net.utils.generic as generic
import rationale_net.utils.parsing as parsing
import rationale_net.utils.model as model_utils
import rationale_net.train.train as train_utils
import oncotext.utils.dataset_factory as dataset_factory
import copy
import numpy as np
import pdb
import os
from csv import DictWriter
import datetime


def parse_epoch_stats_for_dev_results(diagnosis, epoch_stats, logger):
    aspect_result = { 'NAME' : diagnosis}

    best_epoch_indx = epoch_stats['best_epoch']
    aspect_result['ACCURACY'] = epoch_stats['dev_metric'][best_epoch_indx]
    logger.info("RN Wrapper. {} Accuracy={}".format(
                diagnosis, aspect_result['ACCURACY']))
    logger.info("RN Wrapper. {} Confusion_Matrix={}".format(
                diagnosis, epoch_stats['dev_confusion_matrix'][best_epoch_indx]))

    return aspect_result

def train(name, organ, reports, config, logger):
    args = config['RATIONALE_NET_ARGS']
    diagnoses = config['DIAGNOSES'][organ]
    label_maps = config['POST_DIAGNOSES'][organ]
    text_key = config['PREPROCESSED_REPORT_TEXT_KEY']

    embeddings = dataset_factory.get_embedding_tensor(config, args)
    logger.info("RN Wrapper: Succesffuly got embeddings")

    results = []

    for diagnosis in diagnoses:
        logger.info("RN Wrapper: Training model for {}".format(diagnosis))
        args.aspect = diagnosis
        args.snapshot = None

        try:
            if label_maps[args.aspect][0] == "NUM":
                args.class_balance = False
                args.use_as_tagger = True
            else:
                args.class_balance = True
                args.use_as_tagger = False
            
            args.vocab_size = len(embeddings)

            train_data, dev_data = dataset_factory.get_oncotext_dataset_train(
                 reports, label_maps, args, text_key)

            args.epochs = min(args.max_epochs, int(args.steps / (len(train_data) / args.batch_size)))
            
            if not os.path.isdir(args.model_dir.format(name)):
                os.makedirs(args.model_dir.format(name))
            args.model_path = os.path.join( args.model_dir.format(name),
                                        args.model_file.format(diagnosis))
            gen, model = model_utils.get_model(args, embeddings, train_data)

            epoch_stats, model, gen = train_utils.train_model(train_data, dev_data, model, gen, args)
            logger.info("RN Wrapper. {} model finished to training! Train class balance: {}. Dev class balance: {}".format(diagnosis, train_data.class_balance, dev_data.class_balance))

            aspect_result = parse_epoch_stats_for_dev_results(diagnosis, epoch_stats, logger)

        except Exception as e:
            logger.warn("RN Wrapper. {} model failed to train! Exception {}".format(diagnosis, e))
            aspect_result = {'NAME' : diagnosis,
                            'ACCURACY': 'NA Training Failed'}

        results.append(aspect_result)

    return results



def label_reports(name, organ, un_reports, config, logger):
    args = config['RATIONALE_NET_ARGS']
    diagnoses = config['DIAGNOSES'][organ]
    label_maps = config['POST_DIAGNOSES'][organ]
    default_user = config['DEFAULT_USERNAME']
    text_key = config['PREPROCESSED_REPORT_TEXT_KEY']
    embeddings = dataset_factory.get_embedding_tensor(config, args)

    for indx, diagnosis in enumerate(diagnoses):
        args.aspect = diagnosis
        
        if label_maps[args.aspect][0] == "NUM":
            args.class_balance = False
            args.use_as_tagger = True
            args.num_class = args.num_tags
        else:
            args.class_balance = True
            args.use_as_tagger = False
            args.num_class = len(label_maps[diagnosis])

        args.vocab_size = len(embeddings)
        if indx == 0:
            test_data = dataset_factory.get_oncotext_dataset_test(un_reports, label_maps, args, text_key)
        else:
            test_data = dataset_factory.get_oncotext_dataset_test(test_data.dataset, label_maps, args, text_key)

        logger.info("RN Wrapper: Start labeling reports for {}".format(diagnosis))

        snapshot_path = os.path.join( args.model_dir.format(name),
                                        args.model_file.format(diagnosis))
        if not os.path.exists(snapshot_path):
            default_user_snapshot_path = os.path.join(
                                        args.model_dir.format(default_user),
                                        args.model_file.format(diagnosis))
            logger.warn("RN Wrapper: {} model files dont exit! Using default user {} instead".format(name, default_user))
            args.snapshot = default_user_snapshot_path
        else:
            args.snapshot = snapshot_path

        try:
            if not os.path.exists(args.snapshot):
                raise Exception("No trained model exists at {}".format(args.snapshot))
            gen, model = model_utils.get_model(args, embeddings, None)
            test_stats  = train_utils.test_model(test_data, model, gen, args)
            preds = test_stats['preds']
            
        except Exception as e:
            logger.warn("RN Wrapper. {} model failed to label reports! Following Exception({}). Populating all reports with 0 label".format(diagnosis, e))
            preds = np.zeros(len(test_data), dtype=int)

        test_data.dataset = dataset_factory.get_labels_from_predictions(preds, copy.deepcopy(test_data), label_maps, diagnosis, args, text_key, logger)
        
    return test_data.dataset
