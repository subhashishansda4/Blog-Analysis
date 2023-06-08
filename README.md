
## Blog Analysis
Feature Engineering and Text Cleaning of different blogs\
It is the process of gathering, reviewing, and interpreting data from blogs

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

## Why?
This data can be used to understand the following:
* Audience - Who are the blog's readers? What are their interests? What do they want ot learn about?
* Content - What topics are covered in the blog? What is the quality of the content? Is the content original or plagiarized?
* Conversion Rate - Identifying what content is most effective at converting readers into leads or customers
* SEO - How well does the blog rank in search engine results pages (SERPs)? What keywords and phrases are useed in the blog's content?