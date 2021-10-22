# webscraper

README:

The following formula is used to calculate a weighted average for each review. The authors of the top three highest reviews are considered to be the main perpetrators. 

Weighted average calculation = (criteria1*weight)+(criteria2*weight) +...+ (criteria(n)*weight) / criteria1 + criteria2 +...+ criteriaN

Criteria and weights respectively:
•	Rating (out of 5) - 1
•	Number of employee ratings given -1.1
•	Average employee rating given -1.1
•	Length of Review given – 1.3
•	Number of Optional reviews filled out -1.3
•	Average optional review (out of 5) -1.3

Instructions for running the script:

Install git if not yet installed

Clone from github public repository: 

Download and install python (3.9.7 or higher is recommended though older versions 2.x will probably work)

Add python to environment path

Install pip: Instructions are found here: https://pip.pypa.io/en/stable/installation/

Navigate to the WebScraper folder on the command line (terminal)

pip install -r /path/to/requirements.txt

  The requirements txt file will install the necessary dependencies.
  requests==2.25.1
  beautifulsoup4==4.10.0
  rich==10.12.0

Run main application: python WebScraper.py

Run test class: python -m unittest test_webscraper.py
