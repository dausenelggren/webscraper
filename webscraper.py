import requests
from bs4 import BeautifulSoup
from rich.console import Console
from rich.table import Table
import sys


CONST_WEIGHTED_AVERAGE_KEYS = {"rating":1, "average_employee_rating":1.1, "number_of_employee_ratings":1.1, "average_optional_review":1.3, "num_of_optional_reviews":1.3, "review_length":1.3}
CONST_RETRY_MAX = 5
CONST_BASE_URL = "https://www.dealerrater.com/dealer/McKaig-Chevrolet-Buick-A-Dealer-For-The-People-dealer-reviews-23685/page"
CONST_FILTER = "/?filter=#link"


def main():
    console = Console()
    
    page = 1
    numOfRetries = 0
    reviewArr = []    

    while(page <= 5):
        success = False
        while(numOfRetries < CONST_RETRY_MAX and success is False):
            try:
                response = requests.get(f'{CONST_BASE_URL}{page}{CONST_FILTER}', timeout=5)
                if response.ok:
                    content = BeautifulSoup(response.content, "html.parser")
                    success = True
            except Exception as e:
                print(f"Failed to get successful response from {CONST_BASE_URL}{page}{CONST_FILTER}. Try # {numOfRetries} of maximum of {CONST_RETRY_MAX} tries")
            
        if success is False:
            console.print(f"Request to scrape {CONST_BASE_URL}{page}{CONST_FILTER} failed {CONST_RETRY_MAX} times", style="bold red")
            sys.exit()

        
        for review in content.findAll('div', attrs={"class": "review-entry"}):
            # get important base information

            # get table with rows of employee review information
            employeeReviewTable = review.find("div", attrs={"class": "table"})
            tableRows = employeeReviewTable.findAll("div", attrs={"class": "tr"})
            employee_ratings = review.findAll('div', attrs={"class": "relative employee-rating-badge-sm"})

            # optional review table information
            optionalReviewsTable = review.find('div', attrs={"class": "review-ratings-all"}).find('div', attrs={"class": "table"})
            optionalReviewsTableRows = optionalReviewsTable.findAll("div", attrs={"class": "tr"})

            reviewObject = {
                "rating": getBaseRating(review.find('div', attrs={"class": "rating-static"})),
                "author": review.find('span', attrs={"class": "notranslate"}).text.split(' ')[-1],
                "would_recommend": tableRows[len(tableRows)-1].text.split()[-1],
                "average_employee_rating": calcEmployeeReviews(employee_ratings)["average_employee_rating"],
                "number_of_employee_ratings": calcEmployeeReviews(employee_ratings)["number_of_employee_ratings"],
                "average_optional_review": calcOptionalReviews(optionalReviewsTableRows)['average_optional_review'],
                "num_of_optional_reviews": calcOptionalReviews(optionalReviewsTableRows)['num_of_optional_reviews'],
                "review_length": calcReviewLength(review.find('p', attrs={"class": "review-content"}).get_text()),
                "review_body": review.find('p', attrs={"class": "review-content"}).get_text(),
                "date_of_review": getDateOfReview(review.find('div', attrs={"class": "review-date"})),
                "weighted_average": ""
            }
            reviewArr.append(reviewObject)
        
        page += 1

    calculateWeightedAverages(reviewArr)    

    perpetrators = findPerpetrators(reviewArr)


    # Build table that displays the criteria 
    criteriaTable = Table(show_header=True, header_style="bold magenta", title="чрезмерно положительные критерии - Criteria for overly positive review")
    criteriaTable.add_column("Criteria", style="dim", width=30)
    criteriaTable.add_column("Weight", style="dim", width=15, no_wrap=True)
    
    criteriaTable.add_row("Rating", '1.0')
    criteriaTable.add_row("Average Employee Rating", '1.1')
    criteriaTable.add_row("Number of Employee Ratings", "1.1")
    criteriaTable.add_row("Average Optional Review", "1.3")
    criteriaTable.add_row("Number of Optional Reviews", "1.3")
    criteriaTable.add_row("Review Length", "1.3")

    # Build table to display weighted average formula
    formulaTable = Table(show_header=True, header_style="bold magenta", title="Weighted average formula")
    formulaTable.add_column("Definition")
    formulaTable.add_row("A weighted average is calculated for each review based on the above criteria \n weighted average = (criteria1*weight)+(criteria2*weight) +...+ (criteria(n)*weight) / criteria1 + criteria2 +...+ criteriaN")


    # Build the table that contains the worst perpetrators
    perpTable = Table(show_header=True, header_style="bold magenta", title="ОТЧЕТ КГБ - KGB REPORT")
    perpTable.add_column("Date", style="dim", width=12)
    perpTable.add_column("Author", style="dim", width=20, no_wrap=True)
    perpTable.add_column("Review Text", style="dim", width=65, no_wrap=True)
    perpTable.add_column("Weighted Average", style="dim", width=15, no_wrap=True)

    index = 0
    for perp in perpetrators:
        perpTable.add_row(
            perp["date_of_review"], perp["author"], perp["review_body"], str(perp['weighted_average'])
        )
        index += 1

    console.print(criteriaTable)
    console.print(formulaTable)
    console.print(perpTable) 

# creates a list of the top 3 most overly positive review objects. Output: arr of reviewObjects
def findPerpetrators(reviewArr):
    count = 1
    perpetratorsList = []
    cachePerpNames = []
    while(count <=3):
        max = 0
        index = 0
        popIndex = 0
        if(len(reviewArr) > 0):
            for review in reviewArr:
                if review['author'] == "" or review['author'] in cachePerpNames:
                    index += 1
                    continue
                if review['weighted_average'] > max:
                    max = review['weighted_average']
                    popIndex = index
                index += 1
            cachePerpNames.append(reviewArr[popIndex]['author'])
            perpetratorsList.append(reviewArr.pop(popIndex))
            count += 1
    return perpetratorsList

# takes in arr of review objects and calculates the weighted average for each of them and saves it in the 'weighted_average' key
def calculateWeightedAverages(reviewArr):
    for review in reviewArr:
        runningTotalWeighted = 0
        runningTotalUnweighted = 0
        for key in review:
            if key in CONST_WEIGHTED_AVERAGE_KEYS:
                runningTotalWeighted += review[key] * CONST_WEIGHTED_AVERAGE_KEYS[key]
                runningTotalUnweighted += review[key]
        review["weighted_average"] = round(runningTotalWeighted/runningTotalUnweighted, 4)

# takes in a web element and does further scraping and parsing to get the review date
def getDateOfReview(element):
    date = element.text.replace('\n\n\n\n', ' ').strip('\n').split()
    fullDate = f'{date[0]} {date[1]} {date[2]}'
    return fullDate


# calculate the length of the body of the review. i.e. number of words. Output: int
def calcReviewLength(reviewBody):
    return len(reviewBody.split())

# calculate the "number_of_employee_ratings" and "average_employee_rating". Output map
def calcEmployeeReviews(employee_ratings):
    totalRating = 0
    numOfEmployeeRatings = 0
    for employee in employee_ratings:
        totalRating += float(employee.find('span').text)
        numOfEmployeeRatings += 1
            
    averageEmployeeRating = round(totalRating/len(employee_ratings), 4)
    return {"average_employee_rating":averageEmployeeRating, "number_of_employee_ratings": numOfEmployeeRatings}

# get the main rating out of 5. This is a hack for sure. I spread it into multiple lines so that it somewhat readable
def getBaseRating(baseRating):
    # split the tag itself into an array of strings get the 5th index which will always contain a class name that includes the rating
    rating = str(baseRating).split()[5]
    # get the rating piece from the rating class name
    rating = rating.split('-')[-1]
    # convert he string to a float and divide by 10 to move the decimal place one to the left. Like I said, a hack
    rating = float(rating)/10
    return rating

# Calculated the "num_of_optional_reviews" and "average_optional_review". This is a hack since there is no text anywhere
# to give us the number, only a class name that contains the rating
def calcOptionalReviews(tableRows):
    totalRatings = 0
    # loop over the rows in the tableRows object
    for row in tableRows:
        # get the rating-static-indv object from the row object and then put into string array
        ratingElementArr = str(row.find('div', attrs={"class": "rating-static-indv"})).split()
        # make sure the object actually has more than just an object of 'None'
        if len(ratingElementArr) > 1:
            # get the class name containg the rating number
            rating = ratingElementArr[2].split('-')[-1]
            # convert to float and divide by 10 to move decimal one place to the left
            totalRatings += float(rating)/10
    
    averageRating = totalRatings/len(tableRows)

    return {"num_of_optional_reviews": len(tableRows), "average_optional_review": averageRating}


if __name__ == '__main__':
    main()


