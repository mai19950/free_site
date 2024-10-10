import os
import re
from sys import argv
from datetime import datetime
import requests
import pyperclip


class LocalLink:
  modules = [ "tolinkshare2", "abshare", "mksshare" ]
  current_module: str = None
  min_time_str = "2000-01-01 00:00:00"
  target_link: str = None


  @classmethod
  def compare_times(cls, time_srt: str, link: str) -> bool:
    # 转换为 datetime 对象
    min_time = datetime.strptime(cls.min_time_str, "%Y-%m-%d %H:%M:%S")
    cur_time = datetime.strptime(time_srt, "%Y-%m-%d %H:%M:%S")

    if cur_time > min_time:
      cls.target_link = link
      cls.min_time_str = time_srt
      return True
    return False

  @classmethod
  def parse_html(cls, text):
    res = re.search(
      r".*?最后更新时间:(?P<time>.*?)\n"
      r".*?iOS小火箭订阅.*?(?P<ios>http.*?)\n.*?", 
      text, 
      re.DOTALL
    )
    res_dict = None
    if res is None:
      return
    res_dict = res.groupdict()
    time = res_dict["time"].strip()
    link = res_dict["ios"].strip()
    cls.compare_times(time, link)
    print(f"{cls.current_module:<15}{time:<25}{link:<}")

  @classmethod
  def get_net(cls):
    if not cls.current_module:
      cls.current_module = cls.modules[0]
    # https://raw.githubusercontent.com/mksshare/mksshare.github.io/main/README.md
    url = f"https://raw.githubusercontent.com/{cls.current_module}/{cls.current_module}.github.io/main/README.md"
    try:
      with requests.get(url, timeout=10) as res:
        if res.status_code < 300:
          cls.parse_html(res.text)
    except:
      cls.get_net()

  @classmethod
  def walk(cls):
    for mod in cls.modules:
      cls.current_module = mod
      cls.get_net()
    pyperclip.copy(cls.target_link)


if __name__ == '__main__':
  LocalLink.walk()
