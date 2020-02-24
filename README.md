# easyA

A web platform that will allow Purdue students to learn about what other
students think about classes they consider taking. The web application will help students decide
between electives and course choices that might be required for their majors. It will stand out
from similar websites because of the inherited credibility in the website since only active Purdue
students can sign up. This website will allow students to search for classes and these search
results can be filtered using professors and/or tags defined by the developers. Everyone can read
reviews but only logged-in users can write them, upvote, downvote and report them.

## Installation

This web application is implemented using `Python 3.7.*`
```
pip install Flask
pip install pyrebase
pip install google-cloud-firestore
```

## Getting Started

To host a flask web server, go to 'src/' directory and run:
### Linux/MacOS
```
export FLASK_APP=easyA
export FLASK_ENV=development
flask run
```
### Windows Command Prompt
```
set FLASK_APP=easyA
set FLASK_ENV=development
flask run
```

### Hosted on
`localhost:5000`

# Pages (In-development)
```
localhost:5000                - Homepage
localhost:5000/login          - Log In Page
localhost:5000/signup         - Sign up Page
localhost:5000/course/CS18000 - A Test Course Page
localhost:5000/course/CS25200 - A Test Course page
localhost:5000/contact        - Contact Us Page
localhost:5000/report         - Post Review Page
```
