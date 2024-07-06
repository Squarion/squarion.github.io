import glob
import pandas as pd
import datetime
import warnings
import json
import colorsys
import random
from tqdm import tqdm
warnings.filterwarnings("ignore") #TODO

def parse(t):
    ret = []
    for ts in t:
        try:
            string = str(ts)
            tsdt = datetime.date(int(string[:4]), int(string[4:6]), int(string[6:]))
        except TypeError:
            tsdt = datetime.date(1900,1,1)
        ret.append(tsdt)
    return ret

def read_players():
    players = pd.read_csv('matches/atp_players.csv')
    return players

def read_rankings():
    rankings = pd.read_csv('matches/atp_rankings_current.csv')
    return rankings


def load_matches(dirname):
    """Reads ATP matches and parses time into datetime object"""
    allFiles = glob.glob(dirname + "/atp_matches_" + "20??.csv")
    matches = pd.DataFrame()
    container = list()
    for filen in allFiles:
        df = pd.read_csv(filen,
                         index_col=None,
                         header=0,
                         parse_dates=[5],
                         encoding = "ISO-8859-1",
                         date_parser=lambda t:parse(t))
        container.append(df)

    matches = pd.concat(container)
    return matches

def slugify(name):
    return name.replace(' ', '-').lower()

class Title:

    def __init__(self, name, level, date, score, runner_up, runner_up_slug, surface):
        self.name = name.replace('\'', '')
        self.level = level
        if 'Olympics' in self.name:
            self.level = 'O'
        if 'NextGen' in self.name:
            self.level = 'F'
        self.date = date[0:4]
        self.score = score
        self.runner_up = runner_up
        self.runner_up_slug = runner_up_slug
        self.abbr = self.name[:2].upper()
        self.surface = surface.lower()


def titles(matches, players, rankings):
    '''Calculate titles per player'''

    # Clean up and drop all matches that are not a final
    matches = matches.reset_index(drop=True)
    matches = matches[(matches['round'] == 'F')]
    matches['tourney_level_count'] = matches.groupby(['winner_name', 'tourney_level'])['winner_name'].transform('count')
    matches['titles_count'] = matches.groupby('winner_name')['winner_name'].transform('count')

    # Create a dataframe with following columns, sorted by date
    result = matches[['winner_id', 'tourney_id', 'tourney_date', 'tourney_name', 'tourney_level', 'tourney_level_count', 'titles_count', 'loser_id', 'loser_name', 'score', 'surface']].drop_duplicates().sort_values('tourney_date')

    #print(result)

    data = {}
    tourney_levels = ['G', 'M', 'A', 'F', 'D']


    #f = open("_data/colors.json", "r")
    #colors = json.loads(f.read())

    title_winners = result.drop_duplicates(subset='winner_id', keep='first')

    for index, row in tqdm(title_winners.iterrows()):
        #print('\nPLAYER -------------')
        #print(result[(matches['winner_name'] == x)].to_string(index=False, header=False))


        player_id = row['winner_id']
        player = players.loc[players['player_id'] == player_id]

        slug = slugify(player['name_first'].to_string(index=False) + ' ' + player['name_last'].to_string(index=False))

        data[slug] = {}

        latest = rankings.iloc[-1].ranking_date


        data[slug]['first_name'] = player['name_first'].to_string(index=False)
        last_name = player['name_last'].to_string(index=False)
        data[slug]['last_name'] = last_name[0].capitalize() + last_name[1:]
        data[slug]['ioc'] = player['ioc'].to_string(index=False)
        data[slug]['dob'] = pd.to_datetime(player['dob'],format='%Y%m%d').dt.strftime('%d-%m-%Y').to_string(index=False)
        data[slug]['height'] = player['height'].to_string(index=False)
        data[slug]['hand'] = player['hand'].to_string(index=False)
        ranking_query = rankings.loc[(rankings['player'] == player_id) & (rankings['ranking_date'] == latest)]['rank']
        if len(ranking_query != 0):
            data[slug]['rank'] = ranking_query.to_string(index=False)
        else:
            data[slug]['rank'] = '0'

        #print(player['name_first'])
        #print(result[(matches['winner_id'] == player_id)])

        wins = []



        for index, row in result[(matches['winner_id'] == player_id)].iterrows():
            #print(row.tourney_id)
            wins.append(Title(row.tourney_name, row.tourney_level, str(row.tourney_date), row.score, row.loser_name, slugify(row.loser_name), row.surface).__dict__)



        #print(json.dumps(wins))

        data[slug]['titles'] = wins
        data[slug]['no_titles'] = len(wins)


        '''for t in tourney_levels:
            data[slug][t] = {}

            if(result[(matches['winner_id'] == player_id) & (matches['tourney_level'] == t)].any().any()):
                data[slug][t]['count'] = result[(matches['winner_id'] == player_id) & (matches['tourney_level'] == t)]['tourney_level_count'].drop_duplicates().to_string(index=False, header=False)
                data[slug][t]['tourneys'] = []
                for tourney in result[(matches['winner_id'] == player_id) & (matches['tourney_level'] == t)]['tourney_id']:
                    tourney_info = result[(matches['winner_id'] == player_id) & (matches['tourney_level'] == t) & (matches['tourney_id'] == tourney)]
                    #print(tourney_info['tourney_name'])
                    tourney_name = tourney_info['tourney_name'].to_string(index=False, header=False).replace(' Masters', '')

                    #print(colors)
                    #print(tourney_name)
                    #if tourney_name.lower() in colors:
                        tourney_abbr = colors[tourney_name.lower()]['abbr']
                        tourney_color = colors[tourney_name.lower()]['color']
                    else:
                        tourney_abbr = ''
                        tourney_color = "%06x" % random.randint(0, 0xFFFFFF)
                        colors[tourney_name.lower()] = {}
                        colors[tourney_name.lower()]['color'] = tourney_color
                        tourney_abbr = tourney_name[:2].upper()
                        colors[tourney_name.lower()]['abbr'] = tourney_name[:2].upper()

                    #print(tourney_color)
                    r, g, b = tuple(int(tourney_color[i:i+2], 16) for i in (0, 2, 4))

                    import math

                    luminance = math.sqrt(0.299 * (r * r) + 0.587 * (g * g) + 0.114 * (b * b))
                    hls = colorsys.rgb_to_hls(r/255, g/255, b/255)

                    darker = hls[1] * 0.8
                    rgb = colorsys.hls_to_rgb(hls[0], darker, hls[2])
                    shadow = tuple(round(i*255) for i in rgb)
                    tourney_shadow = f'rgb({shadow[0]}, {shadow[1]}, {shadow[2]})'

                    hsv = colorsys.rgb_to_hsv(r, g, b)

                    #print(luminance)
                    font = 'text-light'
                    if (luminance > 110):
                        font = 'text-dark'

                    #fc = colorsys.hsv_to_rgb(round((hsv[0] + 0.5) % 1), hsv[1], hsv[2])
                    #font = f'rgb({fc[0]}, {fc[1]}, {fc[2]})'
                    #font = '191919'

                    tourney_abbr = tourney_name[:2].upper()

                    data[slug][t]['tourneys'].append({
                        'name': tourney_name,
                        'abbr': tourney_abbr,
                        'date': tourney_info['tourney_date'].to_string(index=False, header=False),
                        'score': tourney_info['score'].to_string(index=False, header=False),
                        'runner_up': tourney_info['loser_name'].to_string(index=False, header=False),
                        'runner_up_slug': slugify(tourney_info['loser_name'].to_string(index=False, header=False))
                        })


            else:
                data[slug][t]['count'] = 0
        '''


    #print(data)
    #print(colors)



    #print(type(data))

    players = []

    # For each player
    for slug, values in data.items():

        player_data = {}
        #print('vvvvv', values)
        player_data['slug'] = slug
        player_data['first_name'] = values['first_name']
        player_data['last_name'] = values['last_name']
        player_data['rank'] = values['rank']




        players.append(player_data)

        output = ''

        for key, value in values.items():
            output += f'{key}: {value}\n'

        output += 'layout: player\n'
        output += f'slug: {slug}\n'

        f = open(f"_players/{slug}.md", "w")

        f.write(f'---\n{output}\n---')

    #print(players)
    players = sorted(players, key=lambda x: x['last_name'], reverse=False)
    f = open("_data/players.json", "w")
    f.write(json.dumps(players))
    f.close()
    #print(data)


    #matches['tourneyz'] = matches.groupby('tourney_level')['tourney_level'].transform('count')
    #matches = matches[(matches['winner_name'] == 'Jannik Sinner')]
    #matches = matches.sort(['titles'], ascending=False)
    #print(matches[['winner_name', 'titles', 'tourney_id', 'tourney_name', 'tourney_level', 'tourneyz']].drop_duplicates().sort_values('tourney_level'))
    #print(matches[['winner_name', 'titles']].drop_duplicates().to_csv(sys.stdout,index=False))


pd.set_option('display.max_rows', None)

# Returns a list of all ATP players in history
players = read_players()
rankings = read_rankings()

matches = load_matches('matches')



titles(matches, players, rankings)
