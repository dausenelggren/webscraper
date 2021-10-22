import unittest
import webscraper

class TestWebScraper(unittest.TestCase):
   
    def setUp(self):
        self.reviewObject1 = {
            'rating': 5.0,
            'author': 'name1',
            'would_recommend': 'Yes',
            'average_employee_rating': 4.9,
            'number_of_employee_ratings': 1,
            'average_optional_review': 4.0,
            'num_of_optional_reviews': 5,
            'review_length': 13,
            'review_body': 'There once was a greeat dealership and everything was awesome. Whooooo. Great Test',
            'date_of_review': 'October, 1, 2021',
            'weighted_average': ''
        }

        self.reviewObject2 = {
            'rating': 5.0,
            'author': 'name2',
            'would_recommend': 'Yes',
            'average_employee_rating': 5.0,
            'number_of_employee_ratings': 1,
            'average_optional_review': 4.0,
            'num_of_optional_reviews': 5,
            'review_length': 28,
            'review_body': 'There once was a greeat dealership and everything was awesome. Whooooo. Great Test. Cool There once was a greeat dealership and everything was awesome. Whooooo. Great Test. Cool',
            'date_of_review': 'October, 3, 2021',
            'weighted_average': ''
        }
        self.reviewObject3 = {
            'rating': 5.0,
            'author': 'name3',
            'would_recommend': 'Yes',
            'average_employee_rating': 5.0,
            'number_of_employee_ratings': 1,
            'average_optional_review': 5.0,
            'num_of_optional_reviews': 1,
            'review_length': 30,
            'review_body': 'There once was a greeat dealership and everything was awesome. Whooooo. Great Test. cool. awesome. There once was a greeat dealership and everything was awesome. Whooooo. Great Test. cool. awesome',
            'date_of_review': 'September, 22, 2021',
            'weighted_average': ''
        }

        self.reviewObject4 = {
            'rating': 5.0,
            'author': '',
            'would_recommend': 'Yes',
            'average_employee_rating': 5.0,
            'number_of_employee_ratings': 1,
            'average_optional_review': 4.9,
            'num_of_optional_reviews': 2,
            'review_length': 12,
            'review_body': 'There once was a greeat dealership and everything was awesome. Whooooo. Great',
            'date_of_review': 'September, 22, 2021',
            'weighted_average': ''
        }

        self.reviewObject5 = {
            'rating': 5.0,
            'author': 'name1',
            'would_recommend': 'Yes',
            'average_employee_rating': 5.0,
            'number_of_employee_ratings': 1,
            'average_optional_review': 4.9,
            'num_of_optional_reviews': 2,
            'review_length': 12,
            'review_body': 'There once was a greeat dealership and everything was awesome. Whooooo. Great',
            'date_of_review': 'September, 22, 2021',
            'weighted_average': ''
        }
        self.reviewArr = [self.reviewObject1, self.reviewObject2, self.reviewObject3, self.reviewObject4, self.reviewObject5]

    def tearDown(self) -> None:
        return super().tearDown()

    def test_calculate_review_length(self):
        testStr = "This is a test to see if the reveiw length calculator is working correctly"
        self.assertEqual(webscraper.calcReviewLength(testStr), 14)

    def test_calculate_weighted_averages(self):
        
        webscraper.calculateWeightedAverages(self.reviewArr)
        for review in self.reviewArr:
            self.assertIsNotNone(review['weighted_average'])
        self.assertEqual(self.reviewArr[0]['weighted_average'], 1.2185)
        self.assertEqual(self.reviewArr[1]['weighted_average'], 1.2438)

    def test_find_perpetrators(self):
        webscraper.calculateWeightedAverages(self.reviewArr)
        perpetratorList = webscraper.findPerpetrators(self.reviewArr)
        self.assertEqual(len(perpetratorList), 3)
        self.assertTrue(int(perpetratorList[2]['weighted_average']) <= int(perpetratorList[1]['weighted_average']) <= int(perpetratorList[0]['weighted_average']))

if __name__ == '__main__':
    unittest.main()