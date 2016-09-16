import pickle as p

mistakes = p.load(open('mistake.p','rb'))
reports = p.load(open('genBoostexaFullTestReportDump.p', 'rb'))
reportsSeg = p.load(open('genBoostexaTestReportDump.p', 'rb'))

print mistakes.keys()

dcisMistakes = mistakes['Red_ALH']

for mist in dcisMistakes:
    print '----------------------------'
    print mist['row']
    print reports[ mist['row'] ]
    print '*********************************'
    print reportsSeg[ mist['row'] ]

    print 'gold', mist['gold'], 'vs guessed', mist['pred']
    print "**************************"
    raw_input()

## Gold was wrong on row 67 on DCIS
## Gold was wrong on row  7 on FlatEpithelial
## Gold was wrong on row 467 on ILC
## Gold was wrong on row 434 on ALH

