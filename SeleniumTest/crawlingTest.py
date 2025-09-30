from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
import pandas as pd


url = "https://www.koreabaseball.com/Schedule/Schedule.aspx"

# select = Select(driver.find_element(By.ID, "tblScheduleList"))
# select.select_by_value(day)

def GameScheduleByDay(day):

  options = Options()

  driver = webdriver.Chrome(options=options)
  driver.get(url)

  table = driver.find_element(By.ID, "tblScheduleList")
  schedule = table.text
  thead = table.find_element(By.TAG_NAME, "thead")
  header = thead.text.split()
  tbody = table.find_element(By.TAG_NAME, "tbody")
  rows = tbody.find_elements(By.TAG_NAME, "tr")

  lines = []
  for value in rows:
    body = value.find_elements(By.TAG_NAME, "td")
    schedule_list = []
    for b in body:
      schedule_list.append(b.text)
    lines.append(schedule_list)

  data = []
  game_day = None

  for line in lines:
    if line[0].endswith(')'):
      game_day = line[0]
      data.append(line)
    else:
      line.insert(0, game_day)
      data.append(line)

  df = pd.DataFrame(data, columns=header)
  df = df.drop(columns=['게임센터', '하이라이트', 'TV', '라디오'])


  day_str = f'.{day}('
  df_filtered = df[df['날짜'].str.contains(day_str, na=False, regex=False)]


  print(df_filtered)

  driver.quit()


GameScheduleByDay(23)