EDGAR Project – Sentiment Analysis on Financial Statements
Kubrick, DE32, Elephant and Castle

Background: In the US, the Securities and Exchange Commission (SEC) requires public companies to file 10-K report 
            annually. The 10-K form gives detailed report on the financial position of the company and contains a 
            summary of relevant topics such as business activities, risk factors and legal proceedings.

Aim of project:  To create a package called edgar which determines whether negative sentiment 10-K filings can be used to predict short term                    movements in share prices.
 
Note:   For word classifications, the Loughran-McDonald dictionary for word classifications designed 
        specifically for financial documents is used. 


Modules that need to be installed beforehand:
   
   -yahoofinancials
   -pandas
   -numpy
   -sklearn

Outline of Process:
1. Empty folders created to hold raw HTML and text data
2. The downloader function is called which downloads all the 10-k files and places them in the empty folder.
3. The cleaner function is called which removes any unwanted symbols and returns the 10-k files as cleaned text.
4. The yahoo finance function pulls the yahoo finance information and places it into a csv document.
5. The sentiment analysis function takes all the clean text 10-k files, counts the number of words in the 
document belonging to a particular sentiment and outputs the results to an output csv file.
6. The yahoo finacial data and sentiment data is combined using the sentiment analyis prep functions.
7. Once combined the data is split into test and train for input into different machine learning models.
