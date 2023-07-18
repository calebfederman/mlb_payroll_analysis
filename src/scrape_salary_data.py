import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re
import os

#-------------------------------------------------------------------------------------------------#
# Create teams dictionary with url and team names
#   url: used in web scraping
#   full-name: used as field in data
#-------------------------------------------------------------------------------------------------#

teams = {
    'ARI' : {'url':'arizona-diamondbacks',  'full-name':'Arizona Diamondbacks'},
    'ATL' : {'url':'atlanta-braves',        'full-name':'Atlanta Braves'},
    'BAL' : {'url':'baltimore-orioles',     'full-name':'Baltimore Orioles'},
    'BOS' : {'url':'boston-red-sox',        'full-name':'Boston Red Sox'},
    'CHC' : {'url':'chicago-cubs',          'full-name':'Chicago Cubs'},
    'CWS' : {'url':'chicago-white-sox',     'full-name':'Chicago White Sox'},
    'CIN' : {'url':'cincinnati-reds',       'full-name':'Cincinnati Reds'},
    'CLE' : {'url':'cleveland-guardians',   'full-name':'Cleveland Guardians',  'former-url':'cleveland-indians'},
    'COL' : {'url':'colorado-rockies',      'full-name':'Colorado Rockies'},
    'DET' : {'url':'detroit-tigers',        'full-name':'Detroit Tigers'},
    'HOU' : {'url':'houston-astros',        'full-name':'Houston Astros'},
    'KCR' : {'url':'kansas-city-royals',    'full-name':'Kansas City Royals'},
    'LAD' : {'url':'los-angeles-dodgers',   'full-name':'Los Angeles Dodgers'},
    'LAA' : {'url':'los-angeles-angels',    'full-name':'Los Angeles Angels'},
    'MIA' : {'url':'miami-marlins',         'full-name':'Miami Marlins'},
    'MIL' : {'url':'milwaukee-brewers',     'full-name':'Milwaukee Brewers'},
    'MIN' : {'url':'minnesota-twins',       'full-name':'Minnesota Twins'},
    'NYM' : {'url':'new-york-mets',         'full-name':'New York Mets'},
    'NYY' : {'url':'new-york-yankees',      'full-name':'New York Yankees'},
    'OAK' : {'url':'oakland-athletics',     'full-name':'Oakland Athletics'},
    'PHI' : {'url':'philadelphia-phillies', 'full-name':'Philadelphia Phillies'},
    'PIT' : {'url':'pittsburgh-pirates',    'full-name':'Pittsburgh Pirates'},
    'SDP' : {'url':'san-diego-padres',      'full-name':'San Diego Padres'},
    'SFG' : {'url':'san-francisco-giants',  'full-name':'San Francisco Giants'},
    'SEA' : {'url':'seattle-mariners',      'full-name':'Seattle Mariners'},
    'STL' : {'url':'st-louis-cardinals',    'full-name':'St Louis Cardinals'},
    'TAM' : {'url':'tampa-bay-rays',        'full-name':'Tampa Bay Rays'},
    'TEX' : {'url':'texas-rangers',         'full-name':'Texas Rangers'},
    'TOR' : {'url':'toronto-blue-jays',     'full-name':'Toronto Blue Jays'},
    'WAS' : {'url':'washington-nationals',  'full-name':'Washington Nationals'}
}

#-------------------------------------------------------------------------------------------------#
# Find player salary data from Spotrac
#-------------------------------------------------------------------------------------------------#

# Data is only since 2020 since Spotrac has paywall for rest
for yr in range(2020,2024):

    # Iterate through each team in dict
    # (TODO: need to switch guardians to indians for 2021 and prior)
    for t in teams.items():

        # Read html data and find payroll table
        url = f"https://www.spotrac.com/mlb/{t[1]['url']}/payroll/{yr}/"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"}
        response = requests.get(url,headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find_all("table")[0]

        # Create dataframe and export to csv
        df = pd.read_html(str(table))[0]
        df['Team'] = t[0]
        df['Year'] = yr

        # TODO: instead export to xlsx with a sheet for each table
        df.to_csv('salaries.csv', mode='a', header=(t[0]=='ARI' and yr==2020), index=False)

# TODO: Get player data for players that were on the injured list
# So far the only data is from players that were on the active roster to end the season

#-------------------------------------------------------------------------------------------------#

# Display time of completion
print('\nCompleted at', datetime.now(),'\n')
