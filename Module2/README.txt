Ritwik Salunke  rsalunk1

Module 2 Web Scraping due 5/31/2026

Approach: First robots.txt was checked on gradcafe and a screenshot was taken. Then the files from requirments.txt were installed locally from both this module and from the llm hosting folder.
Then scraper.py was written which used the imports urllib, selenium, requests, BeautifulSoup to read from the gradcafe website and pull data from the survey page and from the details page.
Then a json file was saved with this raw data called applicant_data.json. 
From there clean.py was written which formatted and structured the data pulled from the json into a more readable file called llm_extend_applicant_data.json. From there everything was pushed onto github. 

Known Bugs: The given json files don't have 30000+ entries but running the code will provide you with that amount there was just not enough time to run it.