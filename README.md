# receipt-reader
A web app that takes receipt images and returns tables for your own organization. 

Receipt reader is a tool to scan your receipts and find important information, such as the total amount, issuer and time of the purchase. The receipt reader can be used for situtations in which you need to keep track of expenditure. Exmaple use cases are a business trip in which you need to get a retroactive refund from the company, or a shared house where costs are split and you need to record purchases.
The relevant data from the receipt is stored in a database, together with an image of the receipt. With receipt reader you can export that data to a pre-formated spreadsheet file with direct links to the images online.

The web application is currently hosted at http://18.184.255.203/

To run the applicaiton in your own system, you will need [Tesseract-OCR](https://github.com/tesseract-ocr/tesseract), a program that retrieves text from your images.
