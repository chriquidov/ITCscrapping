# Indeed Job offer website scrapping project


![image](https://user-images.githubusercontent.com/93139204/156459023-a6cfaa74-d43d-4c27-992a-9f21f1e40ab3.png)



## Project purpose 
---
In this project we tried to extract as much data as possible from the website [Indeed](https://www.indeed.com/jobs?q=Data%20Scientist&l=United%20States&vjk=92ecfcf3e426868a), in which one can find a big amount of job offers, including lots of information regarding the job.

## Results
---
The Scrapper is now able to be work from the command line, scrapping:
- Job offers corresponding to a specific title entered by the user, scrapping the number of job offers required by the user

 ### 1. Information gathered for each job offer:
-	Title
-	Company
-	Location
-	Salary (in dollar per year - if provided by the company)
-	Job Type (Full-Time, part-time, etc… - if provided by the company)
-	Summary: Job Description Summary
-	Indeed company link: the link to the company's indeed page
-	If a data is not available it is represented as a Null value

### 2. Information gathered for each company:
- Company name
- Indeed company link
- Rating of the company, according to the reviews 
- Number of reviews on the comapany 
- Number of salaries published 
- Number of job offer for the comapny
- Number of questions and answers on the comapny's page
- Number of photos published of the company's different places
- Work Happiness score: Global score of the employees satisfaction
- CEO name
- Approval score of the CEO
- Year when the comapny was founded 
- Company's number of employees 
- Company's revenues 
- Industry
- Link to company's official website

### 3. MYSQL Database
These informations are stocked into a Mysql database, in different tables as shown in the schema below
![N|Solid](https://github.com/chriquidov/ITCscrapping/blob/main/ERM_DB.png?raw=true)

## Instructions 
---
#### 1. Running the program 
The repository contains a requirements.txt file in which one can find the required packages to be able to put to work the scrapping. 
Once the repository cloned, running the ```indeed_scrapping_checkpoint_1.py``` from the command line where the user is required to provide a job title and a minimum number of job offers to scrape, the user can also add a location, so that the scrapper will look for job offers in a specific location, if a location is not given, the default location is 'United States' once done the program displays a summary of the number of job offers 6 companies data scrapped as well as a log of the events that occured during the creation/update of the database. 
*If the number of jobs specified is more than the avaiòable job offers the maximum available will be returned*

Example of use: 
```bash
 python indeed_scrapping_checkpoint_1.py "data scientist" 50 
```
*In this case the program will scrape the data for at least 50 data scientist job offers in the US* 

#### 2. Creation of the MYSQL database
In order to get the data stored in a proper database, the user needs to install mysql, create a user name and a password, by default the program does only require the user to enter it's password the first time in order to create the 'indeed_db' that contains all the discussed data. If the user made special configurations, he's invited to modify the ```db_parameters.py``` file in order to make sure the connection with Mysql is made and the DB can be created.

 ## Roadmap
This is the second of four checkpoints in total. 

## Authors and acknowledgement 
The authors of this web scraper are Dov Chriqui and Samuel Nataf (le frère).
It is part of the Israel Tech Challenge first project.



![N|Solid](https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQypgIpsSV7mTbOAPAwGwxJ3o0n5lZTelnfeQ&usqp=CAU) ![N|Solid](https://i.pinimg.com/originals/8a/c6/6b/8ac66b8b69031605b3c8fad50fdaf4cc.jpg)


