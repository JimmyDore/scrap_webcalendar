# scrap_webcalendar

after cloning the project, create virtual env 
- virtualenv scrap_webcalendar

activer le virtual env
- source scrap_webcalendar/bin/activate

installer les dépendances
- pip install -r requirements.txt

lancer le script
- python scrap_calendar.py

setup cron : https://awc.com.my/uploadnew/5ffbd639c5e6eccea359cb1453a02bed_Setting%20Up%20Cron%20Job%20Using%20crontab.pdf

setup google api : https://www.twilio.com/blog/2017/02/an-easy-way-to-read-and-write-to-a-google-spreadsheet-in-python.html

copier script install dans cron.daily : sudo cp -R /home/jimmydore/Projets/scrap_webcalendar/start.sh /etc/cron.daily/update_ics.sh