# DBMS-project

This is a simple backend for a song providing services like spotify

## HOW TO INSTALL AND RUN
I JUST HOPE YOU HAVE MYSQL-8.0.4 OR ABOVE INSTALLED IN YOUR SYSTEM AND YOU ARE ON UNIX

### RUN THIS
FIRST MAKE A DATABASE "OHO" IN YOUR MYSQL
```
git clone https://github.com/me-is-mukul/DBMS-project.git
cd DBMS-project
```

```
mysql -u root -p oho < backup.sql
```
ENTER THE PASSWORD AND THEN IT WILL TAKE TIME
AFTER THAT CLOSE MYSQL
NOW IN THE REPO DIRECTORY RUN
```
touch .env
```
NOW OPEN THIS .ENV FILE IN A TEXT EDITOR AND WRITE 
```
PASSWORD = "<YOUR MYSQL PASSWORD>"
```
#### PYTHON DEPENDENCY INSTALLATION
```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
### YOU ARE ALL SET
```
python main.py
```



