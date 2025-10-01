from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

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
            
            if 'win' in home_score_class:
                game_data['승리팀'] = game_data['홈팀명']
                game_data['승리팀점수'] = game_data['홈팀점수']
            elif 'win' in away_score_class:
                game_data['승리팀'] = game_data['원정팀명']
                game_data['승리팀점수'] = game_data['원정팀점수']
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
print("\n--- 최종 추출된 경기 데이터 (5일치) ---")
print(df)