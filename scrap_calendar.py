# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, date

import requests
import os, os.path, csv

import config

from icalendar import Calendar, Event

import ftplib


import gspread
from oauth2client.service_account import ServiceAccountCredentials

#I KNOW THIS CODE IS MESSY, BUT IT'S FOR A PERSONAL USE, SO IT'S MY MESS
#FIXME: Refacto later

#-----------------------
#------SCRAP HBCN
#-----------------------

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
    def getStartEndDate(date_game):
        """
            Possible date format input :
            11/11/2018 – 18h00
            21-22/11/2018
            20/12/2018
            #TODO : REFACTO THIS PART, it's not really beautiful(soup)
        """
        #date_v2 = date.encode('utf-8').split('–')
        date_v2 = date_game.split('–')
        if len(date_v2) >= 2: #Date type : 11/11/2018 – 18h00
            date_v3 = date_v2[0].split('/')
            date_v4 = date_v2[1].split('h')
            start_date = datetime(int(date_v3[2]),int(date_v3[1]),int(date_v3[0]),int(date_v4[0].replace("\xc2\xa0", "")),int(date_v4[1]),0)
            end_date = start_date + timedelta(hours=1.5)
        else:
            date_v2 = date_game.split('-')
            if len(date_v2) >= 2: #Date type : 21-22/11/2018                    
                date_v3 = date_v2[1].split('/')
                start_date = date(int(date_v3[2]),int(date_v3[1]),int(date_v3[0])-1)
                end_date = start_date
            else: #Date type : 20/12/2018
                date_v3 = date_v2[0].split('/')
                start_date = date(int(date_v3[2]),int(date_v3[1]),int(date_v3[0]))
                end_date = start_date

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
            description += "Score du match " + game[3]

        event.add('description', description)

        #--Location event
        #event.add('location', location)

        cal.add_component(event)

    f = open('ics/hbcn_calendar.ics', 'wb')
    f.write(cal.to_ical())
    f.close()


#-----------------------
#------GET BIRTHDAYS AND BUILD ICS
#-----------------------

def getBirthdayIcalCSVFile():

    #TODO : Recup csv file birthday
    # 
    birthdays = []
    #with open('birthdays.csv', 'r') as csvfile:
    #    spamreader = csv.reader(csvfile, delimiter=',')
    #    i = 0
    #    for row in spamreader:
    #        if i != 0:
    #            birthdays.append({'name':row[0],'date':row[1]})
    #        i += 1

    scope = ['https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive']

    credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)

    gc = gspread.authorize(credentials)

    birthdays_sheets = gc.open("Birthdays").worksheet("annivs").get_all_values()
    i = 0
    for b in birthdays_sheets:
        if i != 0:
            birthdays.append({
                'name':b[0],
                'date':b[1]
            })
        i+=1


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

#--------------------------------------
#------GET EDT PERSO FROM GOOGLE SHEETS
#-----------------------

def getPersonalCalendarICS():
    
    #Lien du fichier edt utilisé : https://docs.google.com/spreadsheets/d/1-c3zJ_76plOdyz37-_McaBqHHV3zoWnvOAs6zChiDdE/edit?usp=sharing 
    scope = ['https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive']

    credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)

    gc = gspread.authorize(credentials)

    edt = gc.open("Calendar_projects").worksheet("edt")
    types_occupation = gc.open("Calendar_projects").worksheet("types_occupation").range('A2:A50')

    #Liste of types of occupations
    liste_types_occupations = []
    for occupation in types_occupation:
        if occupation.value != '':
            liste_types_occupations.append(occupation.value)

    timetable = edt.get_all_values()

    hour_list=[]
    for h in timetable[0]:
        hour_list.append(h)
        
    cal = Calendar()
    LAST_HOUR_IN_LINE = 23 #Last hour in edt


    #We get the days
    for day in timetable[1:]:
        for i in range(len(day)):
            value = day[i]
            #3 conditions :
            # une valeur pas vide
            # une valeur appartenant à la liste des occupations possibles
            # une valeur différente de la précédente (si plusieurs valeurs apparaissent plusieurs fois d'affilée, on va traiter ça comme une longue période)           
            if value != '' and value in liste_types_occupations and value != day[i-1]:
                event = Event()

                event.add('summary', value)

                #--Dates event

                day_date = int(day[1].split('/')[0])
                month = int(day[1].split('/')[1])
                year = int(day[1].split('/')[2])
                hour = int(hour_list[i].split(':')[0])
                minutes = int(hour_list[i].split(':')[1])

                start_date = datetime(year,month,day_date,hour,minutes,0)

                #FIXME : An event on mutiple days is broken in multiple events (not expected behaviour) 
                j = i
                end_minutes = 0
                end_hour = hour
                while day[j] == value:#Go in it at least once
                    if end_hour != LAST_HOUR_IN_LINE:
                        j+=1
                        end_hour = int(hour_list[j].split(':')[0])
                        if end_hour == 0:
                            end_hour = 23
                            end_minutes = 59
                            break
                    else:
                        end_hour = 23
                        end_minutes = 59
                        break                
                end_date = datetime(year,month,day_date,end_hour,end_minutes,0)
                
                event.add('dtstart', start_date)
                event.add('dtend', end_date)

                #Description event
                event.add('description', value)

                cal.add_component(event)

    f = open('ics/edt_perso.ics', 'wb')
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
    #TODO : Pour anniv et edt essentiellmeent, refaire ics si birthdays.csv a été modifié récemment

    #HBCN
    datas_calendar = getDatas()
    getICS(datas_calendar)
    #sendFileToFTPServer('hbcn_calendar.ics','ics/','/ics_ffhb')

    #BIRTHDAYS
    getBirthdayIcalCSVFile()
    #sendFileToFTPServer('birthdays.ics','ics/')

    #CalendarPerso project
    getPersonalCalendarICS()
    #sendFileToFTPServer('edt_perso.ics','ics/')

