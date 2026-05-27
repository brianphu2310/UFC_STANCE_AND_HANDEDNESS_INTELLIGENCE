import pandas as pd
import os

print("="*50)
print("UFC EXCEL TO POSTGRES CONVERTER")
print("="*50)


excel_file = 'UFC_FINAL_DATASET.xlsx'

if not os.path.exists(excel_file):
    print(f"ERROR: {excel_file} not found!")
    print("Make sure the file is in the current directory.")
    exit()

print(f"Reading {excel_file}...")

# IMPORTANT: Sheet name has an emoji icon
df_raw = pd.read_excel(excel_file, sheet_name='🥊 Fighters Database', header=2)

# Rename columns
df_raw.columns = ['Number', 'Fighter Name', 'Country', 'Continent', 'Stance', 'Hand', 
                  'Wins', 'Losses', 'Total Fights', 'Win Rate']


df = df_raw[['Fighter Name', 'Country', 'Continent', 'Stance', 'Hand', 
             'Wins', 'Losses', 'Win Rate']].copy()


df['Wins'] = pd.to_numeric(df['Wins'], errors='coerce')
df['Losses'] = pd.to_numeric(df['Losses'], errors='coerce')
df['Win Rate'] = pd.to_numeric(df['Win Rate'], errors='coerce')


df = df.dropna(subset=['Fighter Name', 'Wins', 'Losses'])
df = df[df['Fighter Name'] != 'Fighter Name']
df = df[df['Fighter Name'] != '#']

print(f"Total fighters before filter: {len(df)}")


female_fighters = [
    'Ronda Rousey', 'Rose Namajunas', 'Holly Holm', 'Miesha Tate', 
    'Carla Esparza', 'Tatiana Suarez', 'Amanda Nunes', 'Cris Cyborg',
    'Joanna Jedrzejczyk', 'Alexa Grasso', 'Zhang Weili', 'Yan Xiaonan',
    'Valentina Shevchenko'
]

df = df[~df['Fighter Name'].isin(female_fighters)]
print(f"Male fighters only: {len(df)}")


weight_map = {
    'Flyweight': ['Henry Cejudo', 'Deiveson Figueiredo', 'Brandon Moreno'],
    'Bantamweight': ['Sean O\'Malley', 'TJ Dillashaw', 'Cory Sandhagen', 'Petr Yan', 
                     'Aljamain Sterling', 'Marlon Vera', 'Cody Garbrandt', 'Dominick Cruz', 
                     'Jose Aldo'],
    'Featherweight': ['Alexander Volkanovski', 'Max Holloway', 'Ilia Topuria', 'Yair Rodriguez', 
                      'Brian Ortega', 'Chan Sung Jung'],
    'Lightweight': ['Conor McGregor', 'Dustin Poirier', 'Khabib Nurmagomedov', 'Islam Makhachev', 
                    'Charles Oliveira', 'Justin Gaethje', 'Tony Ferguson', 'Nate Diaz', 
                    'Michael Chandler', 'Paddy Pimblett', 'Dan Hooker'],
    'Welterweight': ['Kamaru Usman', 'Leon Edwards', 'Colby Covington', 'Jorge Masvidal', 
                     'Robbie Lawler', 'Nick Diaz', 'Carlos Condit', 'Gilbert Burns', 
                     'Stephen Thompson'],
    'Middleweight': ['Israel Adesanya', 'Robert Whittaker', 'Alex Pereira', 'Anderson Silva', 
                     'Georges St-Pierre', 'Michael Bisping', 'Darren Till', 'Nassourdine Imavov'],
    'Light Heavyweight': ['Jon Jones', 'Jamahal Hill', 'Jiri Prochazka', 'Magomed Ankalaev', 
                          'Jan Blachowicz', 'Glover Teixeira', 'Mauricio Rua', 'Chuck Liddell', 
                          'Daniel Cormier'],
    'Heavyweight': ['Francis Ngannou', 'Stipe Miocic', 'Ciryl Gane', 'Tom Aspinall', 
                    'Curtis Blaydes', 'Derrick Lewis', 'Alistair Overeem']
}

def get_weight_class(name):
    for wc, fighters in weight_map.items():
        if name in fighters:
            return wc
    return 'Lightweight'

df['weight_class'] = df['Fighter Name'].apply(get_weight_class)
df['handedness'] = df['Hand'] + '-handed'


def get_tip(name):
    tips = {
        'Conor McGregor': 'Study left cross, footwork, distance management',
        'Dustin Poirier': 'Study boxing combinations, body punching',
        'Khabib Nurmagomedov': 'Study wrestling, ground control, pressure',
        'Islam Makhachev': 'Study wrestling, ground game',
        'Israel Adesanya': 'Study calf kicks, feints, distance management',
        'Jon Jones': 'Study creativity, fight IQ, adaptability',
        'Alex Pereira': 'Study left hook, striking power',
        'Charles Oliveira': 'Study submission game, creativity',
        'Georges St-Pierre': 'Study wrestling, fight IQ',
        'Anderson Silva': 'Study head movement, timing',
    }
    for fighter, tip in tips.items():
        if fighter in name:
            return tip
    return 'Study fundamentals and signature techniques'

df['learning_tip'] = df['Fighter Name'].apply(get_tip)
df['total_fights'] = df['Wins'] + df['Losses']


result = df[['Fighter Name', 'Country', 'Continent', 'Stance', 'handedness', 
             'weight_class', 'Wins', 'Losses', 'total_fights', 'Win Rate', 'learning_tip']]

result.columns = ['fighter_name', 'country', 'continent', 'stance', 'handedness', 
                  'weight_class', 'wins', 'losses', 'total_fights', 'win_rate', 'learning_tip']

result['win_rate'] = result['win_rate'].round(2)


result.to_csv('ufc_data.csv', index=False, encoding='utf-8')
print(f"✅ Exported {len(result)} fighters to ufc_data.csv")


with open('insert_data.sql', 'w', encoding='utf-8') as f:
    for _, row in result.iterrows():
        name = row['fighter_name'].replace("'", "''")
        country = row['country'] if pd.notna(row['country']) else 'NULL'
        continent = row['continent'] if pd.notna(row['continent']) else 'NULL'
        tip = row['learning_tip'].replace("'", "''")
        
        f.write(f"INSERT INTO fighters_male (fighter_name, country, continent, stance, handedness, weight_class, wins, losses, total_fights, win_rate, learning_tip) VALUES ('{name}', '{country}', '{continent}', '{row['stance']}', '{row['handedness']}', '{row['weight_class']}', {int(row['wins'])}, {int(row['losses'])}, {int(row['total_fights'])}, {row['win_rate']}, '{tip}');\n")

print(f"✅ Generated insert_data.sql with {len(result)} INSERT statements")


print("\n📊 First 10 fighters:")
print(result[['fighter_name', 'stance', 'handedness', 'weight_class', 'win_rate']].head(10).to_string())
print("\n✅ CONVERSION COMPLETE!")
