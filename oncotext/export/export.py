import oncotext.export.sql as sql
import oncotext.export.atypias as atypias
import copy

def apply_rules(reportDB, config, logger):
    logger.info("Export - Call SQL export ")
    sql.export(copy.deepcopy(reportDB), config, logger)
    logger.info("Export - Call atypia set export")
    atypias.export(copy.deepcopy(reportDB), config, logger)