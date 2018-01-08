from config import Config
import pickle
import oncotext.utils.preprocess as preprocess
import oncotext.logger as logger


SUCCES_STR = "Made following DB {} complaint"
OGPATH = 'LOGS'
LOGNAME = 'oncotext'
logger = logger.get_logger(LOGNAME, LOGPATH)


'''
Run preprocessing on all db's inside train and unlabeled
'''
if __name__ == "__main__":
    ## Load dbs

    ## Run preprocess on each db

    db_base = picke.load(open(Config.DB_BASE_PATH, 'rb'))
    db_base = preprocess.apply_rules(db_base,
                                     Config.RAW_REPORT_TEXT_KEY,
                                     Config.PREPROCESSED_REPORT_TEXT_KEY,
                                     Config.REPORT_TIME_KEY,
                                     logger)
    pickle.dump(db_base, open(Config.DB_BASE_PATH, 'wb'))
    logger.info(SUCCES_STR.format(Config.DB_BASE_PATH))

    db_paths = [
                ## have users
                Config.DB_TRAIN_PATH,
                Config.DB_UNLABLED_PATH,
                Config.DB_NON_BREAST_PATH]
    for path in db_paths:
        db = pickle.load(open(path,'rb'))
        for name in db:
            db[name] = preprocess.apply_rules(
                                    db[name],
                                    Config.RAW_REPORT_TEXT_KEY,
                                    Config.PREPROCESSED_REPORT_TEXT_KEY,
                                    Config.REPORT_TIME_KEY,
                                    logger)
        pickle.dump(db, open(path,'wb'))
        logger.info(SUCCES_STR.format(path))
