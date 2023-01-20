import streamlit as st
import pandas as pd
from PIL import Image
import requests

countries = {"All":"All", "Finland":"FIN", "Sweden":"SWE", "Canada":"CAN", "USA":"USA"}
show_player = False
player_to_show = []

st.set_page_config(layout="wide")

def header(url):
     st.markdown(f'<p style="background-color: transparent;color:#FF0000;font-size:35px;font-weight:bold;border-radius:2%;">{url}</p>', unsafe_allow_html=True)



#NHL logo - centered on the sidebar
st.markdown(
    """
    <style>
        [data-testid=stSidebar] [data-testid=stImage]{
            text-align: center;
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 100%;
        }
    </style>
    """, unsafe_allow_html=True
)

with st.sidebar:
    st.image("assets/nhl_logo.png", width=200)



#Loading dataframe
df = pd.read_csv('assets/player_info.csv')
#df = df[['firstName', 'lastName', 'nationality', 'primaryPosition']]
df = df.iloc[:,0:11]

skaters_teams = pd.read_csv('assets/game_skater_stats.csv')
skaters_teams = skaters_teams.drop_duplicates(subset='player_id', keep="first")
goalies_teams = pd.read_csv('assets/game_goalie_stats.csv')
goalies_teams = goalies_teams.drop_duplicates(subset='team_id', keep="first")
team_info = pd.read_csv('assets/team_info.csv')

#Let's get all unique team names
teams = team_info['teamName']
teams = teams.drop_duplicates(keep="first")
teams = teams.append(pd.Series("All"))
teams = teams.sort_values(ascending=True)


#Selection boxes
add_selectbox = st.sidebar.selectbox(
    "Select country",
    (countries)
)

add_selectbox2 = st.sidebar.selectbox(
    "Select team",
    (teams)
)


df = pd.merge(df, skaters_teams[['player_id','team_id']], left_on='player_id', right_on='player_id', how='left')
df = pd.merge(df, team_info[['team_id','teamName']], left_on='team_id', right_on='team_id', how='left')


df = df.iloc[:,1:13]
#st.write('# Avocado Prices dashboard')
st.title('NHL players database')



if add_selectbox == 'All':
    df_selected = df
else:
    df_selected = df.loc[df['nationality'] == countries.get(add_selectbox)]

df_selected.columns = ['First Name','Last Name', 'Country', 'Birth City', 'Position', 'Birth Year', 'Province', 'Height', 'Height_cm', 'Weight', 'Team ID', 'Team']
df_selected = df_selected.drop(['Height', 'Team ID'], axis=1)
df_selected['Birth Year'] = df_selected['Birth Year'].str[0:4]




# if specific team was selected
if add_selectbox2 != "All":
    df_specific_team = df_selected.loc[df_selected['Team'] == add_selectbox2]
    st.dataframe(df_specific_team)
    if df_specific_team.shape[0] > 0:
        selected_players = df_specific_team['First Name']
        selected_players2 = df_specific_team['Last Name']
        selected_players = selected_players.str.cat(selected_players2, sep=' ')

        #selected_players = selected_players.append(pd.Series("All"))
        selected_players = selected_players.sort_values(ascending=True)
        selected_players = pd.concat([pd.Series(["All"]), selected_players])
        players_selection_box = st.sidebar.selectbox(
        "Select player",
        (selected_players)
        )

        if players_selection_box != "All":
            player_to_show = df_specific_team.loc[df_specific_team['First Name'] + " " + df_specific_team['Last Name'] == players_selection_box]
            show_player = True

            # HTTP request
            Url = "https://en.wikipedia.org/w/api.php?action=query&titles="
            Url_tail = "&prop=pageimages&format=json&pithumbsize=300"
            fullURL = Url + player_to_show['First Name'].iloc[0] + "_" + player_to_show['Last Name'].iloc[0] + Url_tail
            
            # sending get request and saving the response as response object
            r = requests.get(url = fullURL)
            
            # extracting data in json format
            data = r.json()

            data_test = {"batchcomplete":"","query":{"normalized":[{"from":"Kimmo_Timonen","to":"Kimmo Timonen"}],"pages":{"1097667":{"pageid":1097667,"ns":0,"title":"Kimmo Timonen","thumbnail":{"source":"https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Kimmo_Timonen_cropped.jpg/300px-Kimmo_Timonen_cropped.jpg","width":300,"height":287},"pageimage":"Kimmo_Timonen_cropped.jpg"}}}}
            jsonData = data["query"]["pages"]
            for x in jsonData:
                try:
                    pic_link = jsonData[x]["thumbnail"]["source"]
                except:
                    pic_link = "assets/no_image.png"


            # display selected player's info

            left, mid, right = st.columns([2, 1, 1])
            with left: 
                st.metric(label="Full Name", value=player_to_show['First Name'].iloc[0] + " " + player_to_show['Last Name'].iloc[0])
            with mid: 
                st.metric(label="Country", value=player_to_show['Country'].iloc[0])
            with right: 
                st.metric(label="Team", value=player_to_show['Team'].iloc[0])


            left, mid, right = st.columns([2, 1, 1])
            with left: 
                st.image(
                pic_link,
                width=300, # Manually Adjust the width of the image as per requirement
                )
            with mid: 
                st.metric(label="Year of birth", value=player_to_show['Birth Year'].iloc[0])
            with right:
                st.metric(label="Position", value=player_to_show['Position'].iloc[0])

            

else:
    st.dataframe(df_selected)






