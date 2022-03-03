# Indeed Job offer website scrapping project


![image](https://user-images.githubusercontent.com/93139204/156459023-a6cfaa74-d43d-4c27-992a-9f21f1e40ab3.png)



## Project purpose 
---
In this project we tried to extract as much data as possible from the website [Indeed](https://www.indeed.com/jobs?q=Data%20Scientist&l=United%20States&vjk=92ecfcf3e426868a), in which one can find a big amount of job offers, including lots of information regarding the job.

## Results
---
For now, the scrapper is gathering information regarding:
-	Job: 		Data Scientist
-	Location: 	USA
The Results are stored in a csv file that one can check in the csv file job-time.csv (‘time’ is the time the scrapper was executed in format YYMMDD-HHMM)
Information gathered in the csv file for each job offer:
-	Title
-	Company
-	Rating of the company
-	Location
-	Salary (in dollar per year - if provided by the company)
-	Job Type (Full-Time, part-time, etc… - if provided by the company)
-	Summary: Job Description Summary
-	Link: Link of the detailed description of the Job Offer
If a data is not available it is represented as ‘NaN’ in the csv file.
Note: we intend to add more information about the job offer that we will gather from the link that's already in the csv file.



## Instructions 
---
The repository contains a requirements.txt file in which one can find the required packages to be able to pu to work the scrapping. 
Once the repository cloned, running the ```indeed_scrapping_checkpoint_1.py```, the user is required to provide a minimum number of job offers to scrape, once done the program displays the first five rows of the created dataset. 
*If the number of jobs specified is more than the avaiòable job offers the maximum available will be returned*

Example of use: 
```bash
 python indeed_scrapping_checkpoint_1.py
 Please enter the minimum number of job offer you want to scrap: 
500
```

 *Roadmap*
This is the first of four checkpoints in total. 

*Authors and acknowledgement* 
The authors of this web scraper are Dov Chriqui and Samuel Nataf.
It is part of the Israel Tech Challenge first project.



![N|Solid](https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQypgIpsSV7mTbOAPAwGwxJ3o0n5lZTelnfeQ&usqp=CAU)


