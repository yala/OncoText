import logging
import torch
import torch.autograd as autograd
import rationale_net.utils.generic as generic
import rationale_net.utils.parsing as parsing
import rationale_net.utils.model as model
import pdb


INIT_MESSAGE = "OncoNet- Initializing OncoNet Wrapper..."
TRANSF_MESSAGE = "OncoNet- Transfomers succesfully composed"
MODEL_MESSAGE = "OncoNet- Model successfully loaded from : {}"
AGGREGATOR_MESSAGE = "OncoNet- Aggregator [{}] succesfully loaded"
IMG_CLASSIF_MESSAGE = "OncoNet- Image classification produced {}"
EXAM_CLASSIF_MESSAGE = "OncoNet- Exam classification complete!"



def train(reports, config, logger):

    args = generic.parse_args()
    diagnoses = config['diagnoses']

    embeddings, word_to_indx = utils.dataset.get_embedding_tensor(args)
    model_paths = []


    for diagnosis in diagnoses:
        args.aspect = diagnosis
        train_data, dev_data = datasets.factory.get_oncotext_dataset_train(reports, args, word_to_indx)

        args.model_path = args.results_path.format(diagnosis)
        model_paths.append( args.model_path)

        gen, model = model.get_model(args, embeddings, train_data)


        epoch_stats, model, gen = train.train_model(train_data, dev_data, model, gen, args)

    ## TODO Save logs somewhere
    return model_paths



def label_reports(un_reports, config, logger):
    args = config['rationale_net_args']
    diagnoses = config['diagnoses']

    embeddings, word_to_indx = utils.dataset.get_embedding_tensor(args)

    test_data = datasets.factory.get_oncotext_dataset_test(un_reports, args, word_to_indx)

    for indx, diagnosis in diagnoses:

        args.aspect = diagnosis

        snapshot_path = args.results_path.format(diagnosis)

        args.snapshot = snapshot_path
        gen, model = model.get_model(args, embeddings, None)

        _, _, _, _, preds, _  = train.test_model(test_data, train_model, model, gen, optimizer, step, args)
        #flatten
        preds = preds
        pdb.set_trace()
        for i in range(len(test_data)):
            prediction = preds[i] # Wrap with label map
            test_data.dataset[i][diagnosis] = prediction

    return test_data.dataset
