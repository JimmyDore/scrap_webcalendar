# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

import requests
import os, os.path, csv


from icalendar import Calendar, Event

def getDatas():
    listingurl = "http://hbcnantes.com/equipe-professionnelle/equipe-pro-calendrier/"
    response = requests.get(listingurl)
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find('table', attrs={'class':'classement'})
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')

    calendar = []

    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        calendar.append([ele for ele in cols])

def getICS(calendar_hbcn):
    """ 
    Structure de la table
    <th class="classement-journee">Journée</th>
    <th class="classement-date">Date</th>
    <th class="classement-equipe-domicile">Équipe à domicile</th>
    <td class="classement-separateur" style="text-align: center;"> &#8211;</td>
    <th class="classement-equipe-exterieur">Équipe extérieur</th>
    <th class="classement-competition">Compétition</th>
    <th class="classement-tele">Passage télé</th>
    """
    cal = Calendar()

    for game in calendar_hbcn:
        event = Event()
        summary = game[2] + '-' + game [4]
        start_date = game[1]
        #end_date = start_date + timedelta(hours=1.5)
        event.add()

        event.add('summary', summary)
        event.add('dtstart', start_date)
        event.add('dtend', end_date)
        event.add('description', description)
        event.add('location', location)
        cal.add_component(event)

    f = open('course_schedule.ics', 'wb')
    f.write(cal.to_ical())
    f.close()

if __name__ == '__main__':
    datas_calendar = getDatas()
    getICS(datas_calendar)
