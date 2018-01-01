def init_db(config, logger):
    rawPath = CURR_PATH + "reportDB+red+clean.p"
    additPath = CURR_PATH + "additionalTrainRepsMar10.p"
    raws = p.load(open(rawPath, 'rb')) + p.load(open(additPath, 'rb'))


    limDefault = True
    base = []
    for r in raws:
        r['Owner'] = 'default'
        if isAnnotation(r) and limDefault:
            base.append(r)
    print "Len base", len(base)

    try:
        db_train = p.load(open(DB_TRAIN_PATH, 'rb'))
        db_unlabeled = p.load(open(DB_UNLABLED_PATH, 'rb'))
    except Exception, e:
        # Data doesn't exist so init base and preprocess neural min
        print "Init db_train"
        db_train = {'default': base}
        db_unlabeled = {'default': base[ :10]}
        neuralTrain = preprocessTrain.main(base)
        p.dump(neuralTrain, open(CURR_PATH + 'rnn/diagDictTrain.p', 'wb'))
        p.dump(db_train, open(DB_TRAIN_PATH, 'wb'))
        p.dump(db_unlabeled, open(DB_UNLABLED_PATH, 'wb'))
