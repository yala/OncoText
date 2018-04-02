import random
import oncotext.datasets.patholgy_dataset
import oncotext.datasets.patholgy_dataset_tagging
import pickle

def get_oncotext_dataset_train(all_reports, label_maps, args, text_key, vocab_size):
    reports = [r for r in all_reports if args.aspect in r ]
    random.shuffle(reports)
    if len(reports) == 0:
        raise Exception("No data found for {}".format(args.aspect))
    split_indx = int(len(reports)* args.train_split)
    train_reports = reports[: split_indx]
    dev_reports = reports[split_indx:]

    if label_maps[args.aspect][0] == "NUM":
        train_data = oncotext.datasets.patholgy_dataset_tagging.PathologyDatasetTagging(
                                                args,
                                                train_reports,
                                                label_maps,
                                                text_key,
                                                'train',
                                                vocab_size=vocab_size)
        dev_data = oncotext.datasets.patholgy_dataset_tagging.PathologyDatasetTagging(
                                                args,
                                                dev_reports,
                                                label_maps,
                                                text_key,
                                                'dev',
                                                vocab_size=vocab_size)
    else:
        train_data = oncotext.datasets.patholgy_dataset.PathologyDataset(
                                                args,
                                                train_reports,
                                                label_maps,
                                                text_key,
                                                'train',
                                                vocab_size=vocab_size)
        dev_data = oncotext.datasets.patholgy_dataset.PathologyDataset(
                                                args,
                                                dev_reports,
                                                label_maps,
                                                text_key,
                                                'dev',
                                                vocab_size=vocab_size)
    return train_data, dev_data


def get_oncotext_dataset_test(reports, label_maps, args, text_key, vocab_size):
    if label_maps[args.aspect][0] == "NUM":
        test_data = oncotext.datasets.patholgy_dataset_tagging.PathologyDatasetTagging(args, reports, label_maps, text_key, 'test', vocab_size=vocab_size)
    else:
        test_data = oncotext.datasets.patholgy_dataset.PathologyDataset(args, reports, label_maps, text_key, 'test', vocab_size=vocab_size)        
    return test_data


def get_embedding_tensor(config, args):
    embeddings =  pickle.load(open(config['EMBEDDING_PATH'],'rb'))
    args.embedding_dim = embeddings.shape[1]
    return embeddings
