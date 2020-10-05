# Product Comparison Web Application
A web application that takes in two product names provided by the user, compares the sentiment of their product reviews, and returns the better of the two products. The frontend makes requests of the backend which is powered by an AWS Lambda Function.
## frontend
This folder contains the HTML, CSS, and JavaScript code that make up the frontend. The front end takes user input, makes asynchronous calls to the AWS Lambda function, compares the results, and returns the sentiment of each item and the item that has a greater average sentiment score.
## lambda_folder
This folder contains the Python code and all necessary dependencies that are deployed within the AWS Lambda function. The Python code will search for product review webpages, scrape all the paragraphs from each review, and run sentiment analysis on those paragraphs by sending them in batches to the AWS Comprehend API. The code then returns the average sentiment score to be compared by the frontend.
