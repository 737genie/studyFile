import MySQLdb

conn = MySQLdb.connect(
    user="user1",
    passwd="user1",
    host="localhost",
    db="kbo_crawl_player_data"
    # charset="utf-8"
)
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS game")

cursor.execute("""
CREATE TABLE game (
    game_date       DATE,
    stadium         VARCHAR(50),
    home_team       VARCHAR(20),
    away_team       VARCHAR(20),
    away_score      INT,
    home_score      INT,
    away_pitcher    VARCHAR(30),
    home_pitcher    VARCHAR(30),
    winning_team    VARCHAR(20),
    winning_score   INT
);
""")
conn.commit()