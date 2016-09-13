import pickle as p
import sys
sys.path.append("..")

diagsToAlign = MixedAnotations

hTest = p.load(open('genBoostexaTestReportDump.p', 'rb'))
rTests = p.load(open('buildTaghianClassifierTestSets.p', 'rb'))


rTest = [rTests[d] for d in diagsToAlign]]



