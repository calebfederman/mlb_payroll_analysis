import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

start_time = datetime.now()

#-------------------------------------------------------------------------------------------------#
# Create teams dictionary with url substring and team names
#   url: used in web scraping
#   full-name: used as field in data
#-------------------------------------------------------------------------------------------------#

teams = {
    'ARI' : {'url':'arizona-diamondbacks',  'full-name':'Arizona Diamondbacks'},
    'ATL' : {'url':'atlanta-braves',        'full-name':'Atlanta Braves'},
    'BAL' : {'url':'baltimore-orioles',     'full-name':'Baltimore Orioles'},
    'BOS' : {'url':'boston-red-sox',        'full-name':'Boston Red Sox'},
    'CHC' : {'url':'chicago-cubs',          'full-name':'Chicago Cubs'},
    'CHW' : {'url':'chicago-white-sox',     'full-name':'Chicago White Sox'},
    'CIN' : {'url':'cincinnati-reds',       'full-name':'Cincinnati Reds'},
    'CLE' : {'url':'cleveland-guardians',   'full-name':'Cleveland Guardians'},
    'COL' : {'url':'colorado-rockies',      'full-name':'Colorado Rockies'},
    'DET' : {'url':'detroit-tigers',        'full-name':'Detroit Tigers'},
    'HOU' : {'url':'houston-astros',        'full-name':'Houston Astros'},
    'KCR' : {'url':'kansas-city-royals',    'full-name':'Kansas City Royals'},
    'LAA' : {'url':'los-angeles-angels',    'full-name':'Los Angeles Angels'},
    'LAD' : {'url':'los-angeles-dodgers',   'full-name':'Los Angeles Dodgers'},
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
    'STL' : {'url':'st-louis-cardinals',    'full-name':'St. Louis Cardinals'},
    'TBR' : {'url':'tampa-bay-rays',        'full-name':'Tampa Bay Rays'},
    'TEX' : {'url':'texas-rangers',         'full-name':'Texas Rangers'},
    'TOR' : {'url':'toronto-blue-jays',     'full-name':'Toronto Blue Jays'},
    'WSN' : {'url':'washington-nationals',  'full-name':'Washington Nationals'}
}

#-------------------------------------------------------------------------------------------------#
# Find player salary data from Spotrac
#-------------------------------------------------------------------------------------------------#

df_player_salaries = pd.DataFrame()

# Data is only since 2020 since Spotrac has paywall for rest
for yr in range(2020,2024):

    # Iterate through each team in dict
    for t in teams.items():

        # Switch guardians to indians for 2021 and prior
        if yr<=2021 and t[0]=='CLE':
            url= f"https://www.spotrac.com/mlb/cleveland-indians/payroll/{yr}/"
        else:
            url = f"https://www.spotrac.com/mlb/{t[1]['url']}/payroll/{yr}/"

        # Read html data and find payroll table
        
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"}
        response = requests.get(url,headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        table_active = soup.find_all("table")[0]
        table_il = soup.find_all("table")[1]


        # Create dataframe for active table
        df_active_players = pd.read_html(str(table_active))[0]
        df_active_players['Team'] = t[0]
        df_active_players['Tm'] = t[1]['full-name']
        df_active_players['Year'] = yr

        # Create dataframe for injured list table
        df_injured_players = pd.read_html(str(table_il))[0]
        df_injured_players['Team'] = t[0]
        df_injured_players['Tm'] = t[1]['full-name']
        df_injured_players['Year'] = yr

        # Add team dataframe to total dataframe
        df_player_salaries = pd.concat([df_active_players,df_player_salaries], ignore_index=True)
        df_player_salaries = pd.concat([df_injured_players,df_player_salaries], ignore_index=True)

        


# Merge all player name columns into one unifying "Player" column
player_columns = [col for col in df_player_salaries.columns if "Player" in col]
df_player_names = df_player_salaries[player_columns]
df_player_salaries = df_player_salaries.drop(player_columns, axis=1)
df_player_salaries['Player'] = [str(x[pd.notna(x)][0]).split(' (')[0] for x in df_player_names.values]

# Merge Total Salary and Payroll Salary columns into unifying "Salary" column
df_player_salaries['Salary'] = [x[pd.notna(x)][0] for x in df_player_salaries[['Total Salary','Payroll Salary']].values]
df_player_salaries = df_player_salaries.drop(['Total Salary','Payroll Salary'], axis=1)
df_player_salaries = df_player_salaries[df_player_salaries['Salary']!='-']
df_player_salaries['Salary'] = df_player_salaries['Salary'].str.replace('$','')
df_player_salaries['Salary'] = df_player_salaries['Salary'].str.replace(',','').astype(int)


# Export dataframe to csv
df_player_salaries.to_csv('./data/player_salaries.csv', index=False)

#-------------------------------------------------------------------------------------------------#
# Add team abbr and year to standings
#-------------------------------------------------------------------------------------------------#

df_standings = pd.read_csv('./data/mlb_standings.csv')

df_standings['Year'] = [2020]*30 + [2021]*30 +[2022]*30 + [2023]*30

df_standings = df_standings.sort_values('Tm')
abbr = list(teams.keys()) * 4
abbr.sort()
df_standings['Team'] = abbr

df_standings.to_csv('./data/mlb_standings.csv', index=False)


#-------------------------------------------------------------------------------------------------#
# Create Team Yearly Salaries dataframe
#-------------------------------------------------------------------------------------------------#

#df_player_salaries = pd.read_csv('./data/player_salaries.csv')

df_team_salaries = df_player_salaries.groupby(['Team','Year','Pos.'])['Salary'].sum()

df_team_salaries.to_csv('./data/team_salaries.csv')
df_team_salaries = pd.read_csv('./data/team_salaries.csv')

df_team_salaries = pd.pivot(df_team_salaries,index=['Team','Year'],columns='Pos.',values='Salary')

df_team_salaries.to_csv('./data/team_salaries.csv')


#-------------------------------------------------------------------------------------------------#
# Create Excel spreadsheets from dataframes
#-------------------------------------------------------------------------------------------------#

with pd.ExcelWriter('./data/mlb_payroll_data.xlsx', 'openpyxl', mode='a', if_sheet_exists='replace') as f:            
    df_player_salaries.to_excel(f, sheet_name='Player Salaries', index=False)
    df_team_salaries.to_excel(f,sheet_name='Team Salaries')
    df_standings.to_excel(f,sheet_name='MLB Standings', index=False)

#-------------------------------------------------------------------------------------------------#

# Display time of completion
print('\nCompleted at', datetime.now())
print('Ran for', (datetime.now()-start_time), '\n')
