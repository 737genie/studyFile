from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
import pandas as pd


url = "https://www.koreabaseball.com/Player/Register.aspx"

# select = Select(driver.find_element(By.ID, "tblScheduleList"))
# select.select_by_value(day)

def PlayerListByTeam():

  options = Options()

  driver = webdriver.Chrome(options=options)
  driver.get(url)

  final_header = ['등번호', '이름', '투타유형', '생년월일', '체격', '포지션', '팀'] 

  tables = driver.find_elements(By.CLASS_NAME, "tNData")
  tables = tables[2:6]
  lines = []


  print(len(tables))
  for i, table in enumerate(tables) :
    playerlist = table.text
    # print(playerlist)
    thead = table.find_element(By.TAG_NAME, "thead")
    header = thead.text.split()
    table_type = header[1] if len(header) > 1 else '알수없음'

    if table_type in ['투수', '내야수', '외야수', '포수']:
      position_name = table_type
    else:
      position_name = table_type
    
    tbody = table.find_element(By.TAG_NAME, "tbody")
    rows = tbody.find_elements(By.TAG_NAME, "tr")

    for value in rows:
      body = value.find_elements(By.TAG_NAME, "td")
      player_list = []
      for b in body:
        player_list.append(b.text)

      player_list.append(position_name)
      lines.append(player_list)

    data = []

    df = pd.DataFrame(lines, columns=final_header)
    # df = df.drop(columns=['게임센터', '하이라이트', 'TV', '라디오'])



  print(df)
  # print(header)

  driver.quit()


PlayerListByTeam()