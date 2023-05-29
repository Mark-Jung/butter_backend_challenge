# Backend Challenge for Butter
## Intro
This was a sample challenge given by Butter to simulate a simple banking service.
I used Flask for the server framework and Heroku to deploy this.
As personal preference, an edited version of MVC pattern was used for folder structure. 
MMVC, but just think of it as having another abstraction layer between view and controller called manager.
### Setup
#### 1. Setup virtual env and activate
cd to the repo after cloning. 
##### 1.a create virtual env
Feel free to change the virtual env name. 
```
virtualenv env --python=python3.10.1
```
##### 1.b activate virtual env
_
```
source env/bin/activate
```
#### 2. Install necessary packages
```
pip install -r requirements.txt
```
#### 3. Run tests
```
nose2
```
#### 4. Run server locally
```
python3 app.py
```
