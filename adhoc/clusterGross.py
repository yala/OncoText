from __future__ import print_function

import cPickle as p
import sys
sys.path.append('..')
from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn.feature_extraction.text import TfidfVectorizer


reps = p.load(open('../reportDB+new.p','rb'))

def strLen(s):
    return len(s['Report_Text'].split())

gross = [ r['Report_Text'].lower() for r in reps if 'gross' in r['Report_Text'].lower()]

ddocs = [g[ g.index('gross'): ] for g in gross]
docs = []
for d in ddocs:
    docs.extend([z for z in d.split('.') if len(z.split()) > 4])

stopWords = ['removed_accesion_id', 'removed_accession_id', 'removed_date', 'removed_case_id', 'in', 'the', 'of', 'off', 'and', 'to','by']
vectorizer = TfidfVectorizer( max_features=10000,
                                 min_df=2, stop_words=stopWords)
X = vectorizer.fit_transform(docs)


k = 5
km = KMeans(n_clusters=k, init='k-means++', max_iter=100, n_init=1,
                verbose=True)
km.fit(X)

order_centroids = km.cluster_centers_.argsort()[:, ::-1]
    
terms = vectorizer.get_feature_names()
for i in range(k):
    print("Cluster %d:" % i, end='')
    for ind in order_centroids[i, :10]:
        print(' %s' % terms[ind], end='')
        print()

