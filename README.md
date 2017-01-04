#photo-log-generator
## A Simple django project that does the following:
1. Allows user to input a zip file of photos.
2. User can preview the photos, add caption on each photo, change the photo order and save.
3. After saving project, user can generate photo log report.
4. User can also choose to download tempfile to resume the project later.

##Installation
1. Clone the repo.
3. pip install -r requirements.txt
4. create mysql database photoreport & update mysql credentials in photoreport/settings.py line 80.
5. python manage.py migrate
6. python manage.py runserver 
    optional   python manage.py runserver 0.0.0.0:8000      (allows computers external to access) 
7. View 127.0.0.1:8000 on the local computer or use the ipaddress of the computer to access externally.

##git instructions:
git add files 
git commit -am 'what i changed'
git push
