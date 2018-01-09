import logging
import torch
import torch.autograd as autograd
import rationale_net.utils.generic as generic
import rationale_net.utils.parsing as parsing
import rationale_net.utils.model as model_utils
import rationale_net.utils.dataset as dataset_utils
import rationale_net.train.train as train_utils
import oncotext.utils.dataset_factory as dataset_factory
import numpy as np
import pdb
import os

def train(name, reports, config, logger):
    args = config['RATIONALE_NET_ARGS']
    diagnoses = config['DIAGNOSES']
    label_maps = config['POST_DIAGNOSES']
    text_key = config['PREPROCESSED_REPORT_TEXT_KEY']
    torch.set_num_threads(config['NUM_TORCH_THREADS'])

    embeddings, word_to_indx = dataset_utils.get_embedding_tensor(args)
    logger.info("RN Wrapper: Succesffuly got embeddings")
    model_paths = []

    for diagnosis in diagnoses:
        logger.info("RN Wrapper: Training model for {}".format(diagnosis))
        args.aspect = diagnosis
        args.snapshot = None
        train_data, dev_data = dataset_factory.get_oncotext_dataset_train(
                reports, label_maps, args, word_to_indx, text_key)

        if not os.path.isdir(args.model_dir.format(name)):
            os.makedirs(args.model_dir.format(name))
        args.model_path = os.path.join( args.model_dir.format(name),
                                        args.model_file.format(diagnosis))
        model_paths.append( args.model_path)
        gen, model = model_utils.get_model(args, embeddings, train_data)

        try:
            epoch_stats, model, gen = train_utils.train_model(train_data, dev_data, model, gen, args)
            logger.info("RN Wrapper. {} model finished to training! Train class balance: {}. Dev class balance: {}".format(diagnosis, train_data.class_balance, dev_data.class_balance))
        except Exception as e:
            logger.warn("RN Wrapper. {} model failed to train! Train class balance: {}. Dev class balance: {} \n Exception {}".format(diagnosis, train_data.class_balance, dev_data.class_balance, e))

    return model_paths



def label_reports(name, un_reports, config, logger):
    args = config['RATIONALE_NET_ARGS']
    diagnoses = config['DIAGNOSES']
    label_maps = config['POST_DIAGNOSES']
    default_user = config['DEFAULT_USERNAME']
    text_key = config['PREPROCESSED_REPORT_TEXT_KEY']
    args.aspect = "ALL"
    embeddings, word_to_indx = dataset_utils.get_embedding_tensor(args)
    test_data = dataset_factory.get_oncotext_dataset_test(un_reports, label_maps, args, word_to_indx, text_key)

    for indx, diagnosis in enumerate(diagnoses):
        args.num_class = len(label_maps[diagnosis])
        logger.info("RN Wrapper: Start labeling reports for {}".format(diagnosis))

        snapshot_path = os.path.join( args.model_dir.format(name),
                                        args.model_file.format(diagnosis))
        if not os.path.exists(snapshot_path):
            default_user_snapshot_path = os.path.join(
                                        args.model_dir.format(default_user),
                                        args.model_file.format(diagnosis))
            logger.warn("RN Wrapper: {} model files dont exit! Using default user {} instead".format(name, default_user))
            args.snapshot_path = default_user_snapshot_path
        else:
            args.snapshot = snapshot_path

        try:
            gen, model = model_utils.get_model(args, embeddings, None)
            test_stats  = train_utils.test_model(test_data, model, gen, args)
            preds = test_stats['preds']
        except Exception as e:
            logger.warn("RN Wrapper. {} model failed to label reports! Following Exception({}). Populating all reports with 0 label".format(diagnosis, e))
            preds = np.zeros(len(test_data))

        for i in range(len(test_data)):

            prediction = label_maps[diagnosis][preds[i]]
            test_data.dataset[i][diagnosis] = prediction

    return test_data.dataset
