1. Web scraping, data extraction of a static website
	•	Scrape a static website.
	•	Check for a manufacturer, then look into the categories, then the models and the result-set where you find the part number before ‘ - ‘ and the part category.
	•	Scrape the whole catalog from the website and load it into a database.
	•	Containerize the scraper and database.
2. Develop an API
	•	Implement the API as a web service using the FastAPI framework.
	•	Write one or multiple endpoints to expose the data.
	•	Add query-parameters to the endpoint(s), e.g. ?manufacturer=Ammann .
	•	Enable and configure Swagger in FastAPI.
	•	Containerize the web service.
3. Important to us
	•	Scraped data is structured well in the database.
	•	Code is structured clearly, separated by concerns and production ready.
	•	Use docker-compose. We should be able to start the whole project with docker-compose up.
	•	Provide a README for the project.
	•	If you want to describe your decisions, please put them into a separate file.
	•	Scraper should run as fast as possible through the whole page.
