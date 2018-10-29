#!/bin/bash

cd /home/jimmydore/Projets/scrap_webcalendar
myvenv/bin/python scrap_calendar.py
cp -r ics/ ../personal_website
