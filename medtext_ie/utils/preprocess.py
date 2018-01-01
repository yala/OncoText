
# Given a list of dicts, where  each dict represent a report:
# If the report text covers a single breast, we assign it an id and nothing happens
# If the report contains 2 breasts, automatically parse it into two reports, assign them
# both ids.
# @return: the preprocessed reports
def preprocessReports(reports):
    # Can assume reports all ready preprocessed into left/right
    # Some annotations per report
    # gen boostexer files, and continue training. add to existing files
    for r in reversed(reports):
        if 'Report_Text' in r and 'Report_Text_Segmented' in r:
            pass
        elif 'Report_Text' not in r and 'Report_Text_Segmented' in r:
            r['Report_Text'] = r['Report_Text_Segmented']
        elif 'Report_Text_Segmented' not in r and 'Report_Text' in r:
            r['Report_Text_Segmented'] = r['Report_Text']
        else:
            print ("report only has keys", r.keys())
            reports.remove(r)
    # assert 'Report_Text' in r or 'Report_Text_Segmented' in r

    results = preprocessRawDb.main(reports)
    return results

def preprocessText(text):
    cleanText = re.sub(r"\W", " ", text)
    cleanText = ' '.join(cleanText.split('\n'))
    cleanText = re.sub(r"(----)+", "", cleanText)
    cleanText = re.sub(r"(====)+", "", cleanText)
    cleanText = cleanText.lower()
    return cleanText
