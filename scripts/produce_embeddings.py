import pickle
import os, shutil
from os.path import dirname, realpath
import sys
sys.path.append(dirname(dirname(realpath(__file__))))
import argparse
from config import Config
import gensim.models.word2vec as word2vec
import oncotext.utils.preprocess as preprocess
import tqdm

parser = argparse.ArgumentParser(description='Embeddings Producer with Gensim Word2Vec')

parser.add_argument('--reports_path',  type=str, default='pickle_files/reportDBAPI_test.p', help="Place where reports are stored ")
parser.add_argument('--embedding_path',  type=str, default='pickle_files/embeddings.p', help="Place where embeddings are stored ")
parser.add_argument('--word2indx_path',  type=str, default='pickle_files/vocabIndxDict.p', help="Place where word2indx are stored ")
parser.add_argument('--user',  type=str, default='mghMar', help="user who's reports to use")
parser.add_argument('--dim',  type=int, default=200, help="Dimension for embedding")
parser.add_argument('--num_workers',  type=int, default=8, help="Num workers to use")
parser.add_argument('--window',  type=int, default=5, help="Window size for CBOW")
parser.add_argument('--min_count',  type=int, default=5, help="Min count of term to appear in word embedding")

args = parser.parse_args()


if __name__ == "__main__":

    report_db = pickle.load( open(args.reports_path,'rb'), encoding='bytes')
    reports = report_db[args.user]

    sentences = []
    for r in tqdm.tqdm(reports):
        text = r[Config.RAW_REPORT_TEXT_KEY]
        report_sentences = [ preprocess.preprocess_text(sentence) for sentence in text.split('\n')]
        sentences.extend(sentences)

    print("From {} reports, collected {} sentences".format(len(reports),len(sentences)))
    model = Word2Vec(
                    sentences,
                    size=args.dim,
                    window=args.window,
                    min_count=args.min_count,
                    workers=args.num_workers)

    embeddings = model.vectors
    vocab_to_indx = {v: i for i, v in enumerate(model.vocab)}
    pickle.dump(embeddings, open(args.embedding_path,'wb'))
    pickle.dump(vocab_to_indx, open(args.word2indx_path,'wb'))





