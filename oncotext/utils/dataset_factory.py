import random
import oncotext.datasets.patholgy_dataset

def get_oncotext_dataset_train(all_reports, label_maps, args, word_to_indx, get_train, logger):
    reports = [r for r in all_reports if args.aspect in r]
    random.shuffle(reports)
    split_indx = int(len(reports)* args.train_split)
    train_reports = reports[: split_indx]
    dev_reports = reports[split_indx:]

    train_data = oncotext.datasets.patholgy_dataset.PathologyDataset(
                                                args,
                                                train_reports,
                                                label_maps,
                                                word_to_indx,
                                                'train')
    dev_data = oncotext.datasets.patholgy_dataset.PathologyDataset(
                                                args,
                                                dev_reports,
                                                label_maps,
                                                word_to_indx,
                                                'dev')
    return train_data, dev_data




def get_oncotext_dataset_test(reports, label_maps, args, word_to_indx, get_train, logger):
    test_data = oncotext.datasets.patholgy_dataset.PathologyDataset(args,reports, label_maps, word_to_indx, 'test')
    return test_data
