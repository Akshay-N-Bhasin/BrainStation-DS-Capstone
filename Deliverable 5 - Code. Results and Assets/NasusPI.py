import streamlit as st
import numpy as np 
import pandas as pd 
import joblib
import requests
import json
import time
from io import StringIO
import matplotlib.pyplot as plt

'''
# Welcome to LoLValu8!
'''
# This key expires every 24 hours
Developer_API_Key='RGAPI-9c29815b-b5a2-4eaa-870d-9e8a392a8c20' 

# Set pandas to show max columns and max rows
pd.set_option("display.max_rows", None, "display.max_columns", None)

# Define a function to load model
@st.cache(allow_output_mutation=True)
def load_model(path):
    model = joblib.load(path)
    return model

### WIP
# Define a function to retrieve account ids
#def retrieve_game_ID(name):
#     r = requests.get('https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/' + Summoner_name + '?api_key=' + Developer_API_Key)
#    time.sleep(1)
#    try:
#        account_id = pd.json_normalize(r.json())['accountId'][0]
        
        # GameId is a float, this needs to by an integer, convert...
#        gameIDs_df["gameId"] = pd.to_numeric(gameIDs_df["gameId"], downcast='integer')
#        game_IDs = gameIDs_df["gameId"].tolist()
        
        # the items in the list need to be strings, convert them to strings
#        game_ids_str = [str(i) for i in game_IDs]
        
#    except:
#        "Your ID doesn't seem to exist on the NA Server..."

# Define a function to 
### WIP 
    
# Load the optimized model
model = load_model('Optimized Random Forest Classifier Model.pkl')

st.image('Nasus.jpg', width=None)


# Enter your name
Summoner_name = st.text_input('Please Enter Your Summoner Name', 'mmmscruffy')

# send a get request and find the encrypted account ids
print("Retrieving your encrypted Account ID")
r = requests.get('https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/' + Summoner_name + '?api_key=' + Developer_API_Key)
time.sleep(0.87)
try:
    account_id = pd.json_normalize(r.json())['accountId'][0]
except:
    "Your ID doesn't seem to exist on the NA Server..."

# send a get request and find game IDs
"Retrieving your Nasus match list..."
try:
    r = requests.get('https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/' + account_id + '?champion=75&api_key=' + Developer_API_Key)
    gameIDs_df = pd.json_normalize(r.json(), 'matches')
    time.sleep(0.87)
except:
    "WHAT? YOU HAVE NEVER PLAYED NASUS???"
# GameId is a float, this needs to by an integer, convert...
gameIDs_df["gameId"] = pd.to_numeric(gameIDs_df["gameId"], downcast='integer')
game_IDs = gameIDs_df["gameId"].tolist()

# the items in the list need to be strings, convert them to strings
game_ids_str = [str(i) for i in game_IDs]


# Put game IDs in a drop down list
option = st.selectbox("Please select Match ID", game_ids_str)

# click this to start
if st.button('Start'):
    

    # Send another get request to get the match data
    r = requests.get('https://na1.api.riotgames.com/lol/match/v4/matches/' + option + '?api_key=' + Developer_API_Key)

    # Create the dataframes (Participant and Bans)
    part_matchdat_df=pd.json_normalize(data=r.json(), record_path='participants', meta=['gameId', 'seasonId', 'gameDuration'])
    bans_matchdat_df=pd.json_normalize(data=r.json(), record_path=['teams', 'bans'])

    # Rename bans_matchdat_df columns
    bans_matchdat_df.columns = ['Banned Champion Id', 'pickTurn']

    # Define a function for the pictTurn column value for the part_matchdat_df
    def f(x):
        if x['participantId'] == 1: return 1
        elif x['participantId'] == 2: return 4
        elif x['participantId'] == 3: return 5
        elif x['participantId'] == 4: return 8
        elif x['participantId'] == 5: return 9
        elif x['participantId'] == 6: return 2
        elif x['participantId'] == 7: return 3
        elif x['participantId'] == 8: return 6
        elif x['participantId'] == 9: return 7
        elif x['participantId'] == 10: return 10

    # Create pickTurn column for part_matchdat_df
    part_matchdat_df['pickTurn'] = part_matchdat_df.apply(f, axis=1)


    # Merge the two dataframes together on pickTurn
    match_data_df = pd.merge(part_matchdat_df, bans_matchdat_df, on= 'pickTurn')

    # Drop all rows not containing Nasus
    indexNames = match_data_df[match_data_df['championId'] != 75].index
    match_data_df.drop(indexNames, axis=0, inplace=True)


    'Your Match Data is below:'
    st.dataframe(match_data_df)
    time.sleep(1)

    '### Hang in there, cleaning your Data and Feature Engineering!'
    time.sleep(1)

    # Fill NaNs if exist for following columns
    try:
        match_data_df[['stats.firstBloodAssist']].fillna('False', inplace=True)
    except:
        pass
    try:
        match_data_df[['stats.firstTowerKill']].fillna('False', inplace=True)
    except:
        pass
    try:
        match_data_df[['stats.firstTowerAssist']].fillna('False', inplace=True)
    except:
        pass
    try:
        match_data_df[['stats.firstInhibitorKill']].fillna('False', inplace=True)
    except:
        pass
    try:    
        match_data_df[['stats.firstInhibitorAssist']].fillna('False', inplace=True)
    except:
        pass
    
    if match_data_df['stats.win'].iloc[0] == 1:
        '### Your team won this match!'
    else:
        '### Your team lost this match...'
    
    '### Your KDA is...'
    
    "Kills:" 
    match_data_df['stats.kills'].iloc[0]
    'Deaths:' 
    match_data_df['stats.deaths'].iloc[0]
    'Assists:' 
    match_data_df['stats.assists'].iloc[0]
    
    'Looking at your summoner spells...'
    time.sleep(1)

    #### Spell Id columns
    # Create two function to map the spell codes
    def Summ_Spell_Names_ID1(Dataframe):
        if Dataframe['spell1Id']==21: return "Barrier"
        elif Dataframe['spell1Id']==1: return "Cleanse"
        elif Dataframe['spell1Id']==14: return "Ignite"
        elif Dataframe['spell1Id']==3: return "Exhaust"
        elif Dataframe['spell1Id'] == 4: return "Flash"
        elif Dataframe['spell1Id'] == 6: return "Ghost"
        elif Dataframe['spell1Id'] == 7: return "Heal"
        elif Dataframe['spell1Id'] == 11: return "Smite"
        elif Dataframe['spell1Id'] == 12: return "Teleport"

    def Summ_Spell_Names_ID2(Dataframe):
        if Dataframe['spell2Id']==21: return "Barrier"
        elif Dataframe['spell2Id']==1: return "Cleanse"
        elif Dataframe['spell2Id']==14: return "Ignite"
        elif Dataframe['spell2Id']==3: return "Exhaust"
        elif Dataframe['spell2Id'] == 4: return "Flash"
        elif Dataframe['spell2Id'] == 6: return "Ghost"
        elif Dataframe['spell2Id'] == 7: return "Heal"
        elif Dataframe['spell2Id'] == 11: return "Smite"
        elif Dataframe['spell2Id'] == 12: return "Teleport"


    # Create a column for Spell1Name and apply the function
    match_data_df['Spell1Name'] = match_data_df.apply(Summ_Spell_Names_ID1, axis=1)


    # Create a column for Spell2Name and apply the function
    match_data_df['Spell2Name'] = match_data_df.apply(Summ_Spell_Names_ID2, axis=1)


    # Create a summoner spells column which is a list of both spell1name and spell2name
    match_data_df['Summoner Spells'] = match_data_df[['Spell1Name','Spell2Name']].values.tolist()   

    # Pull out summoner spells
    spell_1 = match_data_df.iloc[0]['Spell1Name']
    spell_2 = match_data_df.iloc[0]['Spell2Name']

    'Your Summoner spells are:\n'
    spell_1
    st.image(('Summoner Spells/'+spell_1+'.png'), width=None)

    spell_2
    st.image(('Summoner Spells/'+spell_2+'.png'), width=None)


    # Import MLB
    from sklearn.preprocessing import MultiLabelBinarizer

    # Instantiate
    mlb = MultiLabelBinarizer(sparse_output=True)

    # Binarizes the 'Sorted Summoner Spells' column and joins it to the original dataframe, while also dropping the original column
    match_data_df = match_data_df.join(
                pd.DataFrame.sparse.from_spmatrix(
                    mlb.fit_transform(match_data_df.pop('Summoner Spells')),
                    index=match_data_df.index,
                    columns=mlb.classes_))

    # Convert 'stats.win' dtype to binary integer
    match_data_df['stats.win'] = match_data_df['stats.win'].astype(int)
    

    'Checking out your items...'
    ### Dealing with stat.item column
    # Import item.json file to create a dictionary for the item files
    with open('item.json') as f:
        items_data = json.load(f)
    key_dictionary = {}
    for key in items_data['data']:
        key_dictionary.update({key:items_data['data'][key]['name']})

    # add a value for none
    key_dictionary.update({'0':'None'})

    # Convert the item column to str
    match_data_df['stats.item0'] = match_data_df['stats.item0'].astype(str)
    match_data_df['stats.item1'] = match_data_df['stats.item1'].astype(str)
    match_data_df['stats.item2'] = match_data_df['stats.item2'].astype(str)
    match_data_df['stats.item3'] = match_data_df['stats.item3'].astype(str)
    match_data_df['stats.item4'] = match_data_df['stats.item4'].astype(str)
    match_data_df['stats.item5'] = match_data_df['stats.item5'].astype(str)
    match_data_df['stats.item6'] = match_data_df['stats.item6'].astype(str)

    # map the names using the dictionary
    match_data_df = match_data_df.replace({"stats.item0": key_dictionary, "stats.item1": key_dictionary, "stats.item2": key_dictionary, "stats.item3": key_dictionary, "stats.item4": key_dictionary, "stats.item5": key_dictionary, "stats.item6": key_dictionary})

    # Create an items list
    match_data_df['Item List'] = match_data_df[['stats.item0', 'stats.item1', 'stats.item2', 'stats.item3', 'stats.item4', 'stats.item5', 'stats.item6']].values.tolist()

    st.dataframe(match_data_df['Item List'].values)

    mlb = MultiLabelBinarizer(sparse_output=True)

    # Binarizes the 'Item List' column and joins it to the original dataframe, while also dropping the original column
    match_data_df = match_data_df.join(
                pd.DataFrame.sparse.from_spmatrix(
                    mlb.fit_transform(match_data_df.pop('Item List')),
                    index=match_data_df.index,
                    columns=mlb.classes_))


    "Whats your damage?"

    ### Dealing with Kills, Deaths and Assists


    # Create fraction of magic damage done to champions
    try:
        match_data_df['Fraction Magic Damage Delt to Champions'] = match_data_df['stats.magicDamageDealtToChampions']/match_data_df['stats.magicDamageDealt']
    except:
        match_data_df['Fraction Magic Damage Delt to Champions'] == 0
    
    # Create fraction of Physical damage done to champions
    try:
        match_data_df['Fraction Physical Damage Delt to Champions'] = match_data_df['stats.physicalDamageDealtToChampions']/match_data_df['stats.physicalDamageDealt']
    except:
        match_data_df['Fraction Physical Damage Delt to Champions'] == 0
    
    # Create fraction of true damage done to champions
    try:
        match_data_df['Fraction True Damage Delt to Champions'] = match_data_df['stats.trueDamageDealtToChampions']/match_data_df['stats.trueDamageDealt']
    except:
        match_data_df['Fraction True Damage Delt to Champions'] == 0
        
    # Create fractional column for damage dealt to turrets
    try:
        match_data_df['Fraction of damage dealt to turrets'] = match_data_df['stats.damageDealtToTurrets']/match_data_df['stats.damageDealtToObjectives']
    except:
        match_data_df['Fraction of damage dealt to turrets'] == 0
        
    # Create Physical damage dealt pie chart
    try:
        labels1 = 'Physical Damage Dealt to Champions', 'Physical Damage Dealt to Other'
        sizes1 = [match_data_df['Fraction Physical Damage Delt to Champions'].iloc[0], (1-match_data_df['Fraction Physical Damage Delt to Champions'].iloc[0])]
        explode = (0.1, 0)  # only "explode" the 1st slice
        plt.figure(figsize=(10,10))
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes1, explode=explode, labels=labels1, autopct='%1.1f%%',
            shadow=True, startangle=90)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.title('Physical Damage Dealt')
        plt.show()
        st.pyplot()
    except:
        'No Physical damage dealt'
    
    # Create Magic damage dealt pie chart
    try:
        labels1 = 'Magic Damage Dealt to Champions', 'Magic Damage Dealt to Other'
        sizes1 = [match_data_df['Fraction Magic Damage Delt to Champions'].iloc[0], (1-match_data_df['Fraction Magic Damage Delt to Champions'].iloc[0])]
        explode = (0.1, 0)  # only "explode" the 1st slice
        plt.figure(figsize=(10,10))
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes1, explode=explode, labels=labels1, autopct='%1.1f%%',
            shadow=True, startangle=90)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.title('Magic Damage Dealt')
        plt.show()
        st.pyplot()
    except:
        'No Magic damage dealt'
    
    # Create True damage dealt pie chart
    try:
        labels1 = 'True Damage Dealt to Champions', 'True Damage Dealt to Other'
        sizes1 = [match_data_df['Fraction True Damage Delt to Champions'].iloc[0], (1-match_data_df['Fraction True Damage Delt to Champions'].iloc[0])]
        explode = (0.1, 0)  # only "explode" the 1st slice
        plt.figure(figsize=(10,10))
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes1, explode=explode, labels=labels1, autopct='%1.1f%%',
            shadow=True, startangle=90)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.title('True Damage Dealt')
        plt.show()
        st.pyplot()
    except:
        'No True damage dealt'
    
    # Create Magic damage dealt pie chart
    try:
        labels1 = 'Damage Dealt to Turrets', 'Damage Dealt to Other Objectives'
        sizes1 = [match_data_df['Fraction of damage dealt to turrets'].iloc[0], (1-match_data_df['Fraction of damage dealt to turrets'].iloc[0])]
        explode = (0.1, 0)  # only "explode" the 1st slice
        plt.figure(figsize=(10,10))
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes1, explode=explode, labels=labels1, autopct='%1.1f%%',
            shadow=True, startangle=90)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.title('Damage Dealt to Objectives')
        plt.show()
        st.pyplot()
    except:
        'No damage dealt to objectives'

    'What mystical runes you have!'
    time.sleep(1)
    ### Dealing with the runes and masteries

    # Import runesReforged.json file in order to create a dictionary to map the runes
    with open('runesReforged.json') as f:
        rune_data = json.load(f)

    # Create a key dictionary for runes
    rune_key_dictionary = {}
    for key1 in range(0,len(rune_data)):
        for key2 in range(0,len(rune_data[key1]['slots'])):
            for key3 in range(0,len(rune_data[key1]['slots'][key2]['runes'])):
                rune_key_dictionary.update({rune_data[key1]['slots'][key2]['runes'][key3]['id']:rune_data[key1]['slots'][key2]['runes'][key3]['key']})

    # map the names using the dictionary
    match_data_df = match_data_df.replace({"stats.perk0": rune_key_dictionary, "stats.perk1": rune_key_dictionary, 
                                               "stats.perk2": rune_key_dictionary, "stats.perk3": rune_key_dictionary, 
                                               "stats.perk4": rune_key_dictionary, "stats.perk5": rune_key_dictionary})            

    # Convert perks to string just incase
    match_data_df[['stats.perk0', 'stats.perk1', 'stats.perk2', 'stats.perk3', 'stats.perk4', 'stats.perk5']] = match_data_df[['stats.perk0', 'stats.perk1', 'stats.perk2', 'stats.perk3', 'stats.perk4', 'stats.perk5']].astype(str)


    # Combine runes into a list column
    match_data_df['Rune List'] = match_data_df[['stats.perk0', 'stats.perk1', 'stats.perk2', 'stats.perk3', 'stats.perk4', 'stats.perk5']].values.tolist()
    
    match_data_df['Rune List'].values
    st.dataframe(match_data_df['Rune List'].values)

    # Use the Multilabel binerizer to binerize the rune lsit column

    # Instantiate
    mlb = MultiLabelBinarizer(sparse_output=True)

    # Binarizes the 'Item List' column and joins it to the original dataframe, while also dropping the original column
    match_data_df = match_data_df.join(
                pd.DataFrame.sparse.from_spmatrix(
                    mlb.fit_transform(match_data_df.pop('Rune List')),
                    index=match_data_df.index,
                    columns=mlb.classes_))

    'Coverting the Booleans...'
    time.sleep(1)

    # Convert boolean columns to integers
    try:
        match_data_df['stats.firstBloodKill'] = match_data_df['stats.firstBloodKill'].astype(int)
    except:
        match_data_df['stats.firstBloodKill'] == 0
        match_data_df['stats.firstBloodKill'] = match_data_df['stats.firstBloodKill'].astype(int)
    
    try:
        match_data_df['stats.firstBloodAssist'] = match_data_df['stats.firstBloodAssist'].astype(int)
    except:
        match_data_df['stats.firstBloodAssist'] == 0
        match_data_df['stats.firstBloodAssist'] = match_data_df['stats.firstBloodAssist'].astype(int)
    
    try:    
        match_data_df['stats.firstTowerKill'] = match_data_df['stats.firstTowerKill'].astype(int)
    except:
        match_data_df['stats.firstBloodAssist'] == 0
        match_data_df['stats.firstTowerKill'] = match_data_df['stats.firstTowerKill'].astype(int)
    
    try:
        match_data_df['stats.firstTowerAssist'] = match_data_df['stats.firstTowerAssist'].astype(int)
    except:
        match_data_df['stats.firstTowerAssist'] == 0
        match_data_df['stats.firstTowerAssist'] = match_data_df['stats.firstTowerAssist'].astype(int)
    
    try:
        match_data_df['stats.firstInhibitorKill'] = match_data_df['stats.firstInhibitorKill'].astype(int)
    except:
        match_data_df['stats.firstInhibitorKill'] == 0
        match_data_df['stats.firstInhibitorKill'] = match_data_df['stats.firstInhibitorKill'].astype(int)
        
    try:
        match_data_df['stats.firstInhibitorKill'] = match_data_df['stats.firstInhibitorAssist'].astype(int)
    except:
        match_data_df['stats.firstInhibitorAssist'] == 0
        match_data_df['stats.firstInhibitorKill'] = match_data_df['stats.firstInhibitorAssist'].astype(int)
    
    # For debugging
    #st.dataframe(match_data_df)

    ### Scoring your performance

    'Calculating your performance...'

    time.sleep(1)

    # Set up the right feature columns
    model_col = ['stats.kills','stats.deaths','stats.assists','stats.largestKillingSpree','stats.largestMultiKill','stats.killingSprees',
    'stats.longestTimeSpentLiving','stats.doubleKills','stats.tripleKills','stats.quadraKills','stats.pentaKills','stats.magicDamageDealt',
    'stats.physicalDamageDealt','stats.trueDamageDealt','stats.largestCriticalStrike','stats.totalHeal','stats.totalUnitsHealed',
    'stats.damageSelfMitigated','stats.damageDealtToObjectives','stats.visionScore','stats.timeCCingOthers','stats.totalDamageTaken',
    'stats.goldEarned','stats.turretKills','stats.inhibitorKills','stats.totalMinionsKilled','stats.neutralMinionsKilled',
    'stats.neutralMinionsKilledTeamJungle','stats.neutralMinionsKilledEnemyJungle','stats.totalTimeCrowdControlDealt','stats.visionWardsBoughtInGame',
    'stats.wardsPlaced','stats.wardsKilled','stats.firstBloodKill','stats.firstBloodAssist','stats.firstTowerKill','stats.firstTowerAssist',
    'stats.firstInhibitorKill','stats.firstInhibitorAssist','gameDuration', 'Cleanse','Exhaust','Flash','Ghost','Heal','Ignite','Smite','Teleport',"'Your Cut'",
    'Abyssal Mask','Adaptive Helm','Aegis of the Legion','Aether Wisp','Amplifying Tome',"Archangel's Staff",'Ardent Censer','B. F. Sword',"Bami's Cinder",
    "Banshee's Veil","Berserker's Greaves",'Bilgewater Cutlass','Black Cleaver','Blade of the Ruined King','Blasting Wand','Bloodthirster','Boots of Mobility',
    'Boots of Speed','Boots of Swiftness','Bramble Vest','Broken Stopwatch','Bulwark of the Mountain','Catalyst of Aeons',"Caulfield's Warhammer",'Chain Vest',
    'Cloak of Agility','Cloth Armor','Commencing Stopwatch','Control Ward','Corrupting Potion','Crystalline Bracer','Cull','Dagger','Dark Seal',
    "Dead Man's Plate","Death's Dance","Doran's Blade","Doran's Ring","Doran's Shield",'Duskblade of Draktharr','Edge of Night','Elixir of Iron',
    'Elixir of Wrath','Enchantment: Bloodrazor','Enchantment: Cinderhulk','Enchantment: Runic Echoes','Enchantment: Warrior','Essence Reaver',
    "Executioner's Calling",'Eye of the Herald','Faerie Charm','Farsight Alteration','Fiendish Codex','Forbidden Idol','Frostfang','Frozen Fist','Frozen Heart',
    'Frozen Mallet','Gargoyle Stoneplate',"Giant's Belt",'Glacial Shroud','Guardian Angel',"Guinsoo's Rageblade",'Haunting Guise','Health Potion','Hexdrinker',
    'Hextech GLP-800','Hextech Gunblade','Hextech Protobelt-01','Hextech Revolver',"Hunter's Machete","Hunter's Talisman",'Iceborn Gauntlet','Infinity Edge',
    'Ionian Boots of Lucidity',"Jaurim's Fist",'Kindlegem','Kircheis Shard',"Knight's Vow",'Last Whisper',"Liandry's Torment",'Lich Bane',
    'Locket of the Iron Solari','Long Sword',"Lord Dominik's Regards",'Lost Chapter',"Luden's Echo","Luden's Pulse",'Manamune','Maw of Malmortius',
    "Mejai's Soulstealer",'Mercurial Scimitar',"Mercury's Treads",'Minion Dematerializer','Morellonomicon','Mortal Reminder','Muramana',"Nashor's Tooth",
    'Needlessly Large Rod','Negatron Cloak','Ninja Tabi','Null-Magic Mantle','Oblivion Orb','Oracle Lens','Pauldrons of Whiterock','Perfectly Timed Stopwatch',
    'Phage','Phantom Dancer','Pickaxe','Quicksilver Sash',"Rabadon's Deathcap","Randuin's Omen",'Rapid Firecannon','Ravenous Hydra','Recurve Bow','Redemption',
    'Refillable Potion','Rejuvenation Bead','Righteous Glory','Rod of Ages','Ruby Crystal','Runesteel Spaulders',"Rylai's Crystal Scepter",'Sanguine Blade',
    'Sapphire Crystal',"Seeker's Armguard","Seraph's Embrace",'Serrated Dirk','Shard of True Ice','Sheen',"Shurelya's Reverie","Skirmisher's Sabre",
    'Slightly Magical Boots',"Sorcerer's Shoes",'Spear of Shojin',"Spectre's Cowl",'Spellbinder','Spirit Visage',"Stalker's Blade",'Statikk Shiv',
    "Sterak's Gage",'Stinger','Stopwatch','Stormrazor','Sunfire Cape','Tear of the Goddess','Thornmail','Tiamat','Titanic Hydra',
    'Total Biscuit of Everlasting Will','Trinity Force','Trinity Fusion','Twin Shadows','Vampiric Scepter','Void Staff',"Warden's Mail",
    'Warding Totem (Trinket)',"Warmog's Armor","Wit's End","Youmuu's Ghostblade",'Zeal',"Zeke's Convergence","Zhonya's Hourglass",
    'Fraction Magic Damage Delt to Champions','Fraction Physical Damage Delt to Champions','Fraction True Damage Delt to Champions',
    'Fraction of damage dealt to turrets','AbsoluteFocus','ApproachVelocity','ArcaneComet','BiscuitDelivery','BonePlating','Celerity','CheapShot',
    'Conditioning','Conqueror','CosmicInsight','CoupDeGrace','CutDown','DarkHarvest','Demolish','Electrocute','EyeballCollection','FleetFootwork','FontOfLife',
    'FuturesMarket','GatheringStorm','GhostPoro','GlacialAugment','GraspOfTheUndying','Guardian','HailOfBlades','HextechFlashtraption','IngeniousHunter',
    'LastStand','LegendAlacrity','LegendBloodline','LegendTenacity','LethalTempo','MagicalFootwear','ManaflowBand','MasterKey','MinionDematerializer',
    'NimbusCloak','NullifyingOrb','Overgrowth','Overheal','PerfectTiming','PhaseRush','Predator','PresenceOfMind','PressTheAttack','RavenousHunter',
    'RelentlessHunter','Revitalize','Scorch','SecondWind','ShieldBash','SuddenImpact','SummonAery','TasteOfBlood','TimeWarpTonic','Transcendence','Triumph',
    'UltimateHunter','Unflinching','UnsealedSpellbook','Waterwalking','ZombieWard']

    # We need to create columns with 0s for features that were not captured in the current datafrane, but were captured in the models trainning dataframe
    # Create an empty dictionary to turn into a dataframe later
    missing_features = {}
    for feature in model_col:
        if feature in match_data_df.columns:
            pass # Don't need to do anything if the feature exists
        else:
            # Update the dictionary
            missing_features.update({feature:[0]})
            # create a column out of that feature and input 0

    #Turn the dictionary into a dataframe
    missing_df = pd.DataFrame.from_dict(missing_features)

    # Stick dataframes together
    result_df = pd.concat([match_data_df, missing_df.reindex(match_data_df.index)], axis=1).fillna(0)

    # Set up variable to feed into model
    X = result_df[model_col].reset_index(drop=True)

    performance_score = round((model.predict_proba(X)[0][1]*100),2)

    f'Your performance score for the selected match is: {performance_score}'
