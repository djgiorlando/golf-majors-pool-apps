import streamlit as st
import random
import pandas as pd
import os
from PIL import Image

# Load logo
logo = Image.open("masters_logo.png")
st.image(logo, width=300)

st.title("The Masters Tournament Team Selector")

tiers = {
    "Tier 1": ["Scottie Scheffler", "Rory McIlroy", "Xander Schauffele", "Collin Morikawa", "Ludvig Aberg", "Hideki Matsuyama", "Russell Henley", "Viktor Hovland", "Justin Thomas", "Wyndham Clark"],
    "Tier 2": ["Tommy Fleetwood", "Shane Lowry", "Sepp Straka", "Keegan Bradley", "Patrick Cantlay", "Maverick McNealy", "Robert McIntyre", "Tyrrell Hatton", "Bryson DeChambeau", "Billy Horshel", "Corey Connors", "Min Woo Lee", "Ashkay Bhatia", "Sungjae Im", "Sahith Theegala", "Thomas Detry", "Aaron Ral", "JJ Spaun", "Lucas Glover", "Nick Taylor", "Tom Kim", "Adam Scott],
    "Tier 3": ["Jason Day", "Harris English", "Justin Rose", "Taylor Pendrith", "Denny McCarthy", "Nick Dunlap", "Stephan Jaeger", "Max Greyserman", "Daniel Berger", "JT Piston", "Nico Echavarria", "Davis Thompson", "Laurie Canter", "Brian Harman", "Michael Kim", "Matthieu Pavon", "Tom Hoge", "Austin Eckroat", "Rasmus Hojgaard", "Christiaan Bezuldenhout", "Matt McCarty, "Cam Davis", "Cameron Young", "Joe Highsmith", "Will Zalatoris", "Jhonattan Vegas", "Jordan Spieth", "Thriston Lawrence", "Matt Fitzpatrick", "Kevin Yu"],
    "Tier 4": ["Chris Kirk", "Jon Rahm", "Max Homa", "Nicolai Hojgaard", "Joaquin Niemann", "Davis Riley", "Brian Campbell", "Patrick Reed", "Cameron Smith", "Patton Kizzire", "Adam Schenk", "`Rafael Campos", "Brooks Koepka", "Zach Johnson", "Danny Willett", "Sergio Garcia", "Charl Schwartzel", "Dustin Johnson", "Phil Mickelson", "Angel Cabrera", "Fred Couples", "Bernhard Langer", "Jose Maria Olazabal", "Vijay Singh", "Bubba Watson", "Mike Weir", "Jose Luis Ballester (A)", "Evan Beck (A)", "Justin Hastings (A)", "Noah Kent (A), "Hiroshi Tal (A)"]
}

prize_money = {
    1: 4200000, 2: 2268000, 3: 1428000, 4: 1008000, 5: 840000, 6: 756000, 7: 703500,
    8: 651000, 9: 609000, 10: 567000, 11: 525000, 12: 483000, 13: 441000, 14: 399000
    15: 378000, 16: 357000, 17: 336000, 18: 315000, 19: 294000, 20: 273000, 21: 252000,
    22: 235200, 23: 218400, 24: 201600, 25: 184800, 26: 168000, 27: 161700, 28: 155400,
    29: 149100, 30: 142800, 31: 136500, 32: 130200, 33: 123900, 34: 118650, 35: 113400,
    36: 108150, 37: 102900, 38: 98700, 39: 94500, 40: 90300, 41: 86100, 42: 81900,
    43: 77700, 44: 73500, 45: 69300, 46: 65100, 47: 60900, 48: 57540, 49: 54600,
    50: 52920
}

def simulate_scores(players):
    scores = {}
    for player in players:
        rounds = [random.randint(68, 75) for _ in range(4)]
        total = sum(rounds)
        par = total - 288
        scores[player] = {
            "RD 1": rounds[0],
            "RD 2": rounds[1],
            "RD 3": rounds[2],
            "RD 4": rounds[3],
            "TOTAL": total,
            "PAR": par
        }
    return scores

def assign_positions_and_prizes(scores):
    sorted_scores = sorted(scores.items(), key=lambda x: x[1]["TOTAL"])
    final_scores = {}
    current_position = 1
    tie_group = []

    for i, (player, data) in enumerate(sorted_scores):
        if i > 0 and data["TOTAL"] == sorted_scores[i - 1][1]["TOTAL"]:
            tie_group.append((player, data))
        else:
            if tie_group:
                tie_group.append((player, data))
                pos = current_position
                next_pos = pos + len(tie_group)
                total_prize = sum(prize_money.get(p, 0) for p in range(pos, next_pos))
                prize_split = total_prize // len(tie_group)
                for name, pdata in tie_group:
                    pdata["POSITION"] = f"T{pos}"
                    pdata["PRIZE"] = prize_split
                    final_scores[name] = pdata
                current_position += len(tie_group)
                tie_group = []
            else:
                data["POSITION"] = current_position
                data["PRIZE"] = prize_money.get(current_position, 0)
                final_scores[player] = data
                current_position += 1

    if tie_group:
        pos = current_position
        next_pos = pos + len(tie_group)
        total_prize = sum(prize_money.get(p, 0) for p in range(pos, next_pos))
        prize_split = total_prize // len(tie_group)
        for name, pdata in tie_group:
            pdata["POSITION"] = f"T{pos}"
            pdata["PRIZE"] = prize_split
            final_scores[name] = pdata

    return final_scores

st.subheader("Enter Your Name")
username = st.text_input("Your name (for leaderboard tracking):")

st.sidebar.header("Select Your Team")
team = []

selections = {
    "Tier 1": st.sidebar.multiselect("Choose 2 players from Tier 1", tiers["Tier 1"], max_selections=2),
    "Tier 2": st.sidebar.multiselect("Choose 3 players from Tier 2", tiers["Tier 2"], max_selections=3),
    "Tier 3": st.sidebar.multiselect("Choose 3 players from Tier 3", tiers["Tier 3"], max_selections=3),
    "Tier 4": st.sidebar.multiselect("Choose 2 players from Tier 4", tiers["Tier 4"], max_selections=2)
}

for players in selections.values():
    team.extend(players)

if len(team) == 10:
    st.success("Team selection complete. Click below to simulate rounds and view leaderboard.")

    if st.button("Simulate Tournament & Show Leaderboard"):
        if username:
            all_players = sum(tiers.values(), [])
            scores = simulate_scores(all_players)
            final_scores = assign_positions_and_prizes(scores)

            team_scores = {player: final_scores[player] for player in team}
            df = pd.DataFrame.from_dict(team_scores, orient='index')
            df.index.name = "Player"
            df = df.reset_index()
            df["PAR"] = df["PAR"].apply(lambda x: f"+{x}" if x > 0 else str(x))
            df["PRIZE"] = df["PRIZE"].apply(lambda x: f"${x:,}")

            st.subheader("Leaderboard")
            st.dataframe(df, use_container_width=True)

            team_data = {"Name": username}
            for i, player in enumerate(team):
                team_data[f"Player {i+1}"] = player
            df_saved = pd.DataFrame([team_data])
            df_saved.to_csv("saved_teams.csv", mode="a", header=not os.path.exists("saved_teams.csv"), index=False)
            st.success(f"{username}'s team has been saved!")
        else:
            st.warning("Please enter your name before submitting your team.")
else:
    st.warning("You must select exactly 10 players: 2 from Tier 1, 3 from Tier 2, 3 from Tier 3, and 2 from Tier 4.")

if os.path.exists("saved_teams.csv"):
    st.subheader("Saved Teams Leaderboard")
    saved_df = pd.read_csv("saved_teams.csv")
    st.dataframe(saved_df)
