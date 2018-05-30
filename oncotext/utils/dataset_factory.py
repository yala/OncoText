import random
import oncotext.datasets.pathology_dataset_classifier
import oncotext.datasets.pathology_dataset_tagger
import pickle

def get_oncotext_dataset_train(all_reports, label_maps, args, text_key):
    reports = [r for r in all_reports if args.aspect in r ]
    random.shuffle(reports)
    if len(reports) == 0:
        raise Exception("No data found for {}".format(args.aspect))
    split_indx = int(len(reports)* args.train_split)
    train_reports = reports[: split_indx]
    dev_reports = reports[split_indx:]

    if label_maps[args.aspect][0] == "NUM":
        dataset_obj = oncotext.datasets.pathology_dataset_tagger.PathologyDatasetTagger
    else:
        dataset_obj = oncotext.datasets.pathology_dataset_classifier.PathologyDatasetClassifier
        
    train_data = dataset_obj(args, train_reports, label_maps, text_key, 'train')
    dev_data = dataset_obj(args, dev_reports, label_maps, text_key, 'dev')
    
    return train_data, dev_data


def get_oncotext_dataset_test(reports, label_maps, args, text_key):
    if label_maps[args.aspect][0] == "NUM":
        dataset_obj = oncotext.datasets.pathology_dataset_tagger.PathologyDatasetTagger
    else:
        dataset_obj = oncotext.datasets.pathology_dataset_classifier.PathologyDatasetClassifier
        
    test_data = dataset_obj(args, reports, label_maps, text_key, 'test')        
    return test_data


def get_embedding_tensor(config, args):
    embeddings =  pickle.load(open(config['EMBEDDING_PATH'],'rb'))
    args.embedding_dim = embeddings.shape[1]
    return embeddings
