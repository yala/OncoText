import logging
import torch
import torch.autograd as autograd
import rationale_net.utils.generic as generic
import rationale_net.utils.parsing as parsing
import rationale_net.utils.model as model
import rationale_net.utils.dataset as dataset_utils
import oncotext.utils.dataset_factory as dataset_factory
import pdb


def train(reports, config, logger):

    args = generic.parse_args()
    diagnoses = config['diagnoses']
    label_maps = config['post_diagnoses']

    embeddings, word_to_indx = dataset_utils.get_embedding_tensor(args)
    logger.info("RN Wrapper: Succesffuly got embeddings")
    model_paths = []


    for diagnosis in diagnoses:
        logger.info("RN Wrapper: Training model for {}".format(diagnosis))
        args.aspect = diagnosis
        train_data, dev_data = datasets_factory.get_oncotext_dataset_train(reports, label_maps, args, word_to_indx)

        args.model_path = args.results_path.format(diagnosis)
        model_paths.append( args.model_path)

        gen, model = model.get_model(args, embeddings, train_data)


        epoch_stats, model, gen = train.train_model(train_data, dev_data, model, gen, args)

    ## TODO Save logs somewhere
    return model_paths



def label_reports(un_reports, config, logger):
    args = config['rationale_net_args']
    diagnoses = config['diagnoses']
    label_maps = config['post_diagnoses']

    embeddings, word_to_indx = dataset_utils.get_embedding_tensor(args)

    test_data = datasets_factory.get_oncotext_dataset_test(un_reports, label_maps, args, word_to_indx)

    for indx, diagnosis in diagnoses:
        logger.info("RN Wrapper: Start labeling reports for {}".format(diagnosis))
        args.aspect = diagnosis

        snapshot_path = args.results_path.format(diagnosis)

        args.snapshot = snapshot_path
        gen, model = model.get_model(args, embeddings, None)

        _, _, _, _, preds, _  = train.test_model(test_data, train_model, model, gen, optimizer, step, args)
        #flatten
        preds = preds
        pdb.set_trace()
        for i in range(len(test_data)):
            prediction = label_maps[diagnosis][preds[i]] # Wrap with label map
            test_data.dataset[i][diagnosis] = prediction

    return test_data.dataset
