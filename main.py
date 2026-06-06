

import pandas as pd
import matplotlib.pyplot as plt
import sqlite3

# Load all three seasons
df_2023 = pd.read_csv('nba_2023.csv')
df_2024 = pd.read_csv('nba_2024.csv')
df_2025 = pd.read_csv('nba_2025.csv')

# Add a 'Season' column to each DataFrame
df_2023['Season'] = 2023
df_2024['Season'] = 2024
df_2025['Season'] = 2025

# Cleaning data
def clean_data(df):
    df =df[df['Team'] != 'TOT']
    df = df.dropna(subset = ['PTS', 'Player','Age'])
    return df

df_2023 = clean_data(df_2023)
df_2024 = clean_data(df_2024)
df_2025 = clean_data(df_2025)

# Saving all three to SQLite
conn = sqlite3.connect('nba_analysis.db')
df_2023.to_sql('season_2023', conn, if_exists='replace', index=False)
df_2024.to_sql('season_2024', conn, if_exists='replace', index=False)
df_2025.to_sql('season_2025', conn, if_exists='replace', index=False)

# Finding the most improved player from 2023 to 2025 (PPG+APG+RPG, min 41 games played)
most_improved=  pd.read_sql(""" 
    SELECT 
    p25.Player,
    p25.Team,
    p23.PTS as pts_2023,
    p25.PTS as pts_2025,
    p23.AST as ast_2023,
    p25.AST as ast_2025,
    p23.TRB as trb_2023,
    p25.TRB as trb_2025, 
    ROUND((p25.PTS+p25.AST+p25.TRB) - (p23.PTS+p23.AST+p23.TRB),1) AS improvement
    FROM season_2025 p25
    JOIN season_2023 p23 ON p25.Player = p23.Player
    WHERE p25.PTS > p23.PTS AND p23.G > 41 AND p25.G > 41
    ORDER BY improvement DESC
    LIMIT 10
    """, conn)

# Printing the most improved players
print("Most Improved Players from 2023 to 2025:")
print(most_improved)

# Creating a bar chart to visualize the most improved players
plt.figure(figsize=(12, 6))
plt.bar(most_improved['Player'], most_improved['improvement'], color='royalblue')
plt.xticks(rotation=45, ha='right')
plt.title('Most Improved Players 2023 to 2025 (PTS + AST + REB)')
plt.xlabel('Player')
plt.ylabel('Combined PTS + AST + REB Improvement')
plt.tight_layout()
plt.savefig('most_improved.png')
plt.show()

# Finding the best 3 point shooting centers in 2025 (min 2 attempts per game)
best_three_point = pd.read_sql("""
    SELECT 
        Player,
        Team,
        "3PA",
        ROUND("3P%", 2) AS three_point_percentage
    FROM season_2025
    WHERE "3PA" >= 2 AND Pos = 'C'
    ORDER BY three_point_percentage DESC
    LIMIT 10
""", conn)


# Printing the best three-point players
print("Best 3-Point Shooting Centers in 2025 (min 2 attempts per game):")
print(best_three_point)

# Creating a bar chart to visualize the best three-point shooting centers
plt.figure(figsize=(12, 6))
plt.bar(best_three_point['Player'], best_three_point['three_point_percentage'], color='red')
plt.xticks(rotation=45, ha='right')
plt.title('Best 3-Point Shooting Centers 2025 (min 2 attempts per game)')
plt.xlabel('Player')
plt.ylabel('3-Point Shooting Percentage for centers')
plt.tight_layout()
plt.savefig('best_three_point_centers.png')
plt.show()

# Finding which teams develop the best young talent (players under 23)
best_young_talent = pd.read_sql("""
   SELECT 
    p25.Team,
    COUNT(p25.Player) AS young_players_developed,
    ROUND(AVG((p25.PTS+p25.AST+p25.TRB+p25.STL+p25.BLK) - 
    (p23.PTS+p23.AST+p23.TRB+p23.STL+p23.BLK)), 1) AS avg_improvement
FROM season_2025 p25
JOIN season_2023 p23 ON p25.Player = p23.Player
WHERE p23.Age < 23
GROUP BY p25.Team
ORDER BY avg_improvement DESC
LIMIT 10
""", conn)

# Printing the teams that develop the best young talent
print("Teams that Develop the Best Young Talent (players under 23):")
print(best_young_talent)

# Creating a bar chart to visualize the teams that develop the best young talent
plt.figure(figsize=(12, 6))
plt.bar(best_young_talent['Team'], best_young_talent['avg_improvement'], color='green')
plt.xticks(rotation=45, ha='right')
plt.title('Teams that Develop the Best Young Talent (players under 23)')
plt.xlabel('Team')
plt.ylabel('Average Improvement in PTS + AST + REB + STL + BLK')
plt.tight_layout()
plt.savefig('best_young_talent.png')
plt.show()

