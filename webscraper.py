import requests
from bs4 import BeautifulSoup


weightedAverageKeys = {"rating":1, "average_employee_rating":1.1, "number_of_employee_ratings":1.1, "average_optional_review":1.3, "num_of_optional_reviews":1.3, "review_length":1.3}

def main():
    
    baseUrl = "https://www.dealerrater.com/dealer/McKaig-Chevrolet-Buick-A-Dealer-For-The-People-dealer-reviews-23685/page"
    page = 1
    filter = "/?filter=#link"
    reviewArr = []

    while(page <= 5):
        response = requests.get(f'{baseUrl}{page}{filter}', timeout=5)
        content = BeautifulSoup(response.content, "html.parser")
        
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
                # "would_recommend": tableRows[len(tableRows)-1].text.encode('utf-8').split('b')[-1],
                "would_recommend": tableRows[len(tableRows)-1].text.split()[-1],
                "average_employee_rating": calcEmployeeReviews(employee_ratings)["average_employee_rating"],
                "number_of_employee_ratings": calcEmployeeReviews(employee_ratings)["number_of_employee_ratings"],#figure out what to pass to this. Either the result of find or the review object 
                "average_optional_review": calcOptionalReviews(optionalReviewsTableRows)['average_optional_review'],
                "num_of_optional_reviews": calcOptionalReviews(optionalReviewsTableRows)['num_of_optional_reviews'],
                "review_length": calcReviewLength(review.find('p', attrs={"class": "review-content"}).get_text()),
                "review_body": review.find('p', attrs={"class": "review-content"}).get_text(),
                "date_of_review": getDateOfReview(review.find('div', attrs={"class": "review-date"})),
                "weightedAverage": ""
            }
            reviewArr.append(reviewObject)
        
        page += 1

    calculateWeightedAverages(reviewArr)

    for review in reviewArr:
        print(review)

    perpetrators = findPerpetrators(reviewArr)

    for perp in perpetrators:
        print(perp)


def findPerpetrators(reviewArr):
    count = 1
    perpetratorsList = []
    while(count <=3):
        max = 0
        index = 0
        popIndex = None
        for review in reviewArr:
            if review['weightedAverage'] > max:
                max = review['weightedAverage']
                tmpBiggest = review
                popIndex = index
            index += 1
        perpetratorsList.append(reviewArr.pop(popIndex))
        count += 1
    return perpetratorsList

def calculateWeightedAverages(reviewArr):
    for review in reviewArr:
        runningTotalWeighted = 0
        runningTotalUnweighted = 0
        for key in review:
            if key in weightedAverageKeys:
                runningTotalWeighted += review[key] * weightedAverageKeys[key]
                runningTotalUnweighted += review[key]
        review["weightedAverage"] = round(runningTotalWeighted/runningTotalUnweighted, 4)


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
            
    averageEmployeeRating = totalRating/len(employee_ratings)
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

def calcNumberOfReviews(baseRating):
    return 

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


