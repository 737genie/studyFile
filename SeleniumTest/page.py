from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import MySQLdb

url = "https://www.koreabaseball.com/Schedule/GameCenter/Main.aspx#none;"

options = Options()
# options.add_argument("--headless") # 실제 브라우저 창을 띄우지 않고 실행하려면 주석 해제
driver = webdriver.Chrome(options=options)
driver.get(url)

# 데이터가 로드될 때까지 최대 10초 대기
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "li.game-cont"))
)

all_game_data = [] # 전체 데이터를 저장할 리스트

# 이전 버튼을 클릭할 횟수 설정 (예: 5일치)
MAX_ITERATIONS = 5

for i in range(MAX_ITERATIONS + 1): # 현재 날짜 포함
    print(f"--- {i}번째 날짜의 경기 데이터 추출 중... ---")
    
    # 1. 경기 목록 요소 다시 찾기 (날짜가 바뀌었을 수 있으므로 반복문 안에서 매번 찾음)
    game_elements = driver.find_elements(By.CSS_SELECTOR, "li.game-cont")

    for element in game_elements:
        game_data = {} 
        
        # 데이터 추출 로직 (이전 답변에서 완성된 로직 사용)
        game_data['경기일자'] = element.get_attribute("g_dt")
        game_data['경기장'] = element.get_attribute("s_nm")
        game_data['홈팀명'] = element.get_attribute("home_nm")
        game_data['원정팀명'] = element.get_attribute("away_nm")
        
        try:
            # 홈/원정 점수 및 투수 정보 추출
            away_info_div = element.find_element(By.CSS_SELECTOR, ".team.away")
            game_data['원정팀점수'] = away_info_div.find_element(By.CSS_SELECTOR, ".score").text
            game_data['원정팀투수'] = away_info_div.find_element(By.CSS_SELECTOR, ".today-pitcher p").text[1:].strip()
            
            home_info_div = element.find_element(By.CSS_SELECTOR, ".team.home")
            game_data['홈팀점수'] = home_info_div.find_element(By.CSS_SELECTOR, ".score").text
            game_data['홈팀투수'] = home_info_div.find_element(By.CSS_SELECTOR, ".today-pitcher p").text[1:].strip()

            # 승리팀/점수 식별
            home_score_class = home_info_div.find_element(By.CSS_SELECTOR, ".score").get_attribute("class")
            away_score_class = away_info_div.find_element(By.CSS_SELECTOR, ".score").get_attribute("class")
            
            # 💡 수정된 로직: 승패, 무승부, 경기 전/취소 순으로 판단
            
            # 1. 홈팀 승리
            if 'win' in home_score_class:
                game_data['승리팀'] = game_data['홈팀명']
                game_data['승리팀점수'] = game_data['홈팀점수']
            
            # 2. 원정팀 승리
            elif 'win' in away_score_class:
                game_data['승리팀'] = game_data['원정팀명']
                game_data['승리팀점수'] = game_data['원정팀점수']
            
            # 3. 무승부 (승리 클래스가 없고, 점수가 같으며, 점수가 N/A가 아닐 경우)
            elif game_data['홈팀점수'] == game_data['원정팀점수'] and game_data['홈팀점수'] != 'N/A':
                game_data['승리팀'] = "무승부"
                game_data['승리팀점수'] = game_data['홈팀점수'] # 또는 원정팀 점수
                
            # 4. 경기 전/취소 (위 조건에 모두 해당하지 않을 경우)
            else:
                game_data['승리팀'] = "경기 전/취소"
                game_data['승리팀점수'] = "N/A"
            
        except Exception:
            # 예외 발생 시 (예: 경기 시작 전이거나 데이터가 부족할 때)
            game_data['원정팀점수'] = "N/A"
            game_data['홈팀점수'] = "N/A"
            game_data['원정팀투수'] = "N/A"
            game_data['홈팀투수'] = "N/A"
            game_data['승리팀'] = "경기 전 취소"
            game_data['승리팀점수'] = "N/A"
            
        all_game_data.append(game_data)


    # 2. 다음 반복을 위해 "이전" 버튼 클릭
    if i < MAX_ITERATIONS:
        try:
            prev_button = driver.find_element(By.ID, "lnkPrev")
            prev_button.click()
            
            # 페이지가 새로 로드되기를 기다립니다.
            time.sleep(3) 

        except Exception:
            print("더 이상 이전 경기 일정이 없습니다.")
            break
        
driver.quit()

# 3. Pandas DataFrame 생성 및 결과 출력
df = pd.DataFrame(all_game_data)
# df.to_csv("kbo_game_data_5day.csv", index=False, encoding='utf-8-sig')
# print("\n--- 최종 추출된 경기 데이터 (5일치) ---")
# print(df)

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
    id              INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
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

insert_query = """
INSERT INTO game (
    game_date, stadium, home_team, away_team, away_score, home_score,
    away_pitcher, home_pitcher, winning_team, winning_score
) VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
)
"""

for row in df.itertuples(index=False):
    data_to_insert = list(row)

    for i in [4,5,9]:
        value = data_to_insert[i]

        if value in ["N/A", ""]:
            data_to_insert[i] = None
        else:
            try:
                data_to_insert[i] = int(value)
            except ValueError:
                data_to_insert[i] = None
    for i in [6,7,8]:
        value = data_to_insert[i]

        if value in ["경기 전 취소", "N/A"]:
            data_to_insert[i] = None
        
    try:
        cursor.execute(insert_query, tuple(data_to_insert))
    except Exception as e:
        print(f"데이터 삽입 오류 발생: {e}")
        print(f"오류가 발생한 데이터: {data_to_insert}")

conn.commit()
print(f"✅ 총 {len(df)}건의 경기 데이터가 데이터베이스에 성공적으로 삽입되었습니다. (NULL 값 처리 완료)")

cursor.close()
conn.close()