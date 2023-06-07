
# Blog Analysis

I completed the assignment given on 5th Feb from Black Coffer regarding text analysis of blogs and articles from different websites.


#### Folder contains the following


| Elements || Description  |
| :-------- | :------- | :---------------------- |
| data | files given for the task |
| texts | *.txt* files containing blogs from different link |
| output | *.csv* and *.xlsx* files containing features and processed text |
| logs.txt | error logs during the process of scanning links |
| main.py | main python file |

## Instructions

Created a **texts** folder to save all the *.txt* files containing blogs from different links after iterating through the column **'URL'**.

Loaded **StopWords** and **Negative / Positive** *.txt* files into **separate list variables**.

**Removed** stopwords from the text of every link, including the base **NLTK** version *stopwords* **set**. Also, **replaced numbers with text alternatives**, and **preprocessed** the text.

Created **functions** for each feature given in the **Objective** *.docx* file. For finding **syllables**, I used *syllables* library in Python. I **appended** all numerical values in separate lists and **added in dataframe**


## Authors

- [@subhashishansda4](https://github.com/subhashishansda4)

