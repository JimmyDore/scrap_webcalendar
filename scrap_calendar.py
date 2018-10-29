# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, date

import requests
import os, os.path, csv

import config

from icalendar import Calendar, Event

import ftplib



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

    return calendar

def getICS(calendar_hbcn):
    """ 
    """
    def getStartEndDate(date):
        """
            Possible date format input :
            11/11/2018 – 18h00
            21-22/11/2018
            20/12/2018
            #TODO : REFACTO THIS PART, it's not really beautiful(soup)
        """
        #date_v2 = date.encode('utf-8').split('–')
        date_v2 = date.split('–')
        if len(date_v2) >= 2: #Date type : 11/11/2018 – 18h00
            date_v3 = date_v2[0].split('/')
            date_v4 = date_v2[1].split('h')
            #if['20', '10', '2018 '] == date_v3:
            #    import ipdb; ipdb.set_trace()
            start_date = datetime(int(date_v3[2]),int(date_v3[1]),int(date_v3[0]),int(date_v4[0].replace("\xc2\xa0", "")),int(date_v4[1]),0)
            end_date = start_date + timedelta(hours=1.5)
        else:
            date_v2 = date.split('-')
            if len(date_v2) >= 2: #Date type : 21-22/11/2018                    
                date_v3 = date_v2[1].split('/')
                start_date = datetime(int(date_v3[2]),int(date_v3[1]),int(date_v3[0])-1,0,0,1)
                end_date = start_date + timedelta(hours=23)
            else: #Date type : 20/12/2018
                date_v3 = date_v2[0].split('/')
                start_date = datetime(int(date_v3[2]),int(date_v3[1]),int(date_v3[0]),0,0,1)
                end_date = start_date + timedelta(hours=23)

        return start_date,end_date

    cal = Calendar()

    for game in calendar_hbcn:
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
        event = Event()
        
        #--Title event
        summary = 'D1 Hand : ' + game[2] + '-' + game[4]
        event.add('summary', summary)

        #--Dates event
        start_date, end_date = getStartEndDate(game[1])
        event.add('dtstart', start_date)
        event.add('dtend', end_date)

        #Description event
        description = summary + '\n' + game[0] + '\n' + game[5] + '\n'
        if len(game[3]) > 0:
            description += "Score du match : game[3]"

        event.add('description', description)

        #--Location event
        #event.add('location', location)

        cal.add_component(event)

    f = open('ics/hbcn_calendar.ics', 'wb')
    f.write(cal.to_ical())
    f.close()



def getIcalCSVFile(csvfile):

    #TODO : Recup csv file birthday
    # 
    birthdays = []
    with open(csvfile, 'r') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        i = 0
        for row in spamreader:
            if i != 0:
                birthdays.append({'name':row[0],'date':row[1]})
            i += 1

    cal = Calendar()

    # FIXME : Don't know how to repeat events using icalendar for python
    # so i add the event for the next 100 years (not optimal)
    # a solution could be to directly update the ics generated to add a repeat rule
    year = 2018
    years = []
    for i in range(100):
        years.append(year)
        year += 1

    for y in years:
        for birthday in birthdays:
            event = Event()
            
            #--Title event
            summary = 'Birthday : ' + birthday['name']
            event.add('summary', summary)

            #--Dates event
            #import ipdb; ipdb.set_trace()
            date_values = birthday['date'].split('/')

            start_date = date(y,int(date_values[1]),int(date_values[0]))
            
            event.add('dtstart', start_date)
            event.add('dtend', start_date)

            #Description event
            event.add('description', summary)

            cal.add_component(event)

    f = open('ics/birthdays.ics', 'wb')
    f.write(cal.to_ical())
    f.close()



def sendFileToFTPServer(file_name,folder_localfile_path ='',folder_ftp_path='/'):
    session = ftplib.FTP(config.HOST_FTP,config.USERNAME_FTP,config.PASSWORD_FTP)
    session.cwd(folder_ftp_path)
    file = open(folder_localfile_path+file_name,'rb')                  # file to send
    session.storbinary('STOR '+file_name, file)     # send the file
    file.close()                                                    # close file and FTP
    session.quit()


if __name__ == '__main__':
    #TODO : Pour anniv essentiellmeent, refaire ics si borthdays.csv a été modifié récemment

    #HBCN
    datas_calendar = getDatas()
    getICS(datas_calendar)
    sendFileToFTPServer('hbcn_calendar.ics','ics/','/ics_ffhb')

    #BIRTHDAYS
    getIcalCSVFile('birthdays.csv')
    sendFileToFTPServer('birthdays.ics','ics/')

