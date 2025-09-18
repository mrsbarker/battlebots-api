### Intro
Battlebots is such an entertaining and intriguing show! Teams of engineers and designers build robots with the express purpose of surviving ~2 minute matches. A robot can win via knockout or judge decision based on points earned in the match.

### Purpose
Display familiarity with extract-transform-load method and various data analysis skills with interesting engineering-related data that spanned a number of years and existed on multiple webpages.

### Technology
Python is the language used in this project's associated files. Data was extracted from the battlebots website using Python web-scraping libraries: Requests and BeautifulSoup4. In addition to the expected data cleaning, special consideration had to be made as each season had a unique roster of robots and some robots have been competing since 2015. I wanted teams with long histories to be cataloged together (under one key) to track their growth and changes over a season. After the initial data cleaning and organizing, tables were uploaded to PostgresSQL database where a Flask app used as an API accesses + returns the data.

Feel free to view the code for additional details on how I extracted and transformed the data to suit this project! Use the bts folder for forking to create the base json files locally.

### Results
API (web-app) <br>
[POSTman](https://britdesignedit-895777.postman.co/workspace/Mrs-Britt's-Workspace~2850cd02-ef87-4895-85ff-34830443260f/collection/48125527-1b0e8379-d416-499c-8d13-11f6f1e2df5a?action=share&creator=48125527)
<br>
[Render Link](https://battlebots-api-xbx1.onrender.com)
