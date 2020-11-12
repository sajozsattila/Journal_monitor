# μr² open-access sciencific journal monitor

This project aims to build up an Article database for high quality open-access Academic journals.  

## Browse of the data
The generated dataset is freely accessible in the [μr² project](https://mur2.co.uk/). The project tries to inform the scientist with the up to date researching results.   

# The included Journals
The monitored Journal should be listed in the Directory of Open Access Journals in the [Web of Science Expanded Science Citation Index ](https://en.wikipedia.org/wiki/Science_Citation_Index).  You can search for Journals in the Web of Science [Search engine](https://mjl.clarivate.com/search-results) 

# The workbooks
Each workbook is monitoring a certain publisher open-access journal and save the result in a CSV. 

## Generated output

The result of CSV separated by the pipe (|) character, and has the bellow columns:
  + url -- the URL of the Article
  + journal_title -- the name of the Journal
  + journal_eissn -- eISSN of the Journal
  + category -- the scientific category of the Article, if there is multiple separated by hash (#)
  + title -- the title of the Article
  + doi -- the DOI of the Article
  + abstract -- the abstract of the Article
  + writer -- the writers of the Article. If there are multiple writers, they separated by hash (#) character. The workplace and the writer [ORCID ID](https://orcid.org/) also can be recorded.  The workplace separated by double (--), the IRCID ID by three (---) from the writer name.
  + publishdate -- ISO 8601 format online publishing time of the Article
  + keyword -- the keywords of the Article, if there is multiple separated by hash (#)

There is an example CSV (journal_Annals_of_Glaciology) file in the data folder. 

## Enrich CSV with ORCI id

The data on the Journals webpage do not always contain the up to data ORCID id for the writers.  To update the datasets we can enrich the CSV by the "journal_orcid_enrichment" workbook. 


