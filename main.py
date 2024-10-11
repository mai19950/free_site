import os
import re
from sys import argv
import requests
import base64
import urllib.parse
from typing import Optional, Literal

headers = {
  "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
}
KeyType = Optional[Literal['ios', 'v2ray', 'clash']]

class Main:
  paths = [
    "tolinkshare2",
    "abshare",
    "mksshare"
  ]
  dirs = ['v2ray', 'ios', 'clash']
  sub_links = {}
  type: KeyType = None

  def __init__(self, type: KeyType = None) -> None:
    self.type = type
    self.submodule_path = self.paths[0]

  def add_suffix(self, line: str) -> str:
    # 提取备注
    # 去掉 ss:// 前缀
    ss_content = line[5:]
    # 进行 Base64 解码，添加必要的填充
    base64_str = ss_content.split('@')[0]
    padding = len(base64_str) % 4
    if padding != 0:
      base64_str += '=' * (4 - padding)

    try:
      # 进行 Base64 解码
      decoded_bytes = base64.b64decode(base64_str)
      decoded_string = decoded_bytes.decode('utf-8')

      # 提取加密方式和密码
      server, port_with_remark = ss_content.split('@')[1].split(':', 1)
      method, password = decoded_string.split(':')
      port, remark = port_with_remark.split('#')
      remark = urllib.parse.unquote(remark)
      if '|' not in remark:
        return ""
      cleaned_remark = re.sub(r' \|.*', f'_{self.submodule_path}', remark)
      return f'ss://{base64.b64encode(f"{method}:{password}".encode()).decode()}@{server}:{port}#{urllib.parse.quote(cleaned_remark)}'
    except Exception as e:
      print(e.args)
      return line

  def parse_origin(self, text: str) -> str:
    decoded_bytes = base64.b64decode(text)
    decoded_string = decoded_bytes.decode('utf-8')
    nodes = []
    for line in decoded_string.split('\n'):
      if not line.strip(): continue
      node = self.add_suffix(line)
      if not node: continue
      nodes.append(node)
    return "\n".join(nodes)

  def get_item_link(self, key: str, url: str):
    try:
      url = re.sub(r'https?:/', 'https://', url) if re.match(r'https:/[^/]', url) else url
      with requests.get(url, headers=headers, timeout=10) as res:
        print(res.status_code, url)
        if res.status_code < 300:
          os.makedirs(key, exist_ok=True)
          with open(f"{key}/{self.submodule_path}.{key}", mode="w+", encoding="utf-8") as f:
            f.write(self.parse_origin(res.text))
    except:
      self.get_item_link(key, url)

  def request_links(self):
    items = self.sub_links.items()

    if self.type:
      self.get_item_link(self.type, self.sub_links[self.type])
      return

    for key, url in items:
      self.get_item_link(key, url)

  def set_links(self):
    with open(f"{self.submodule_path}/README.md", mode="r", encoding="utf-8") as f:
      text = f.read()
      res = re.search(
        r".*?Clash订阅.*?(?P<clash>http.*?)\n"
        r".*?v2rayN订阅.*?(?P<v2ray>http.*?)\n"
        r".*?iOS小火箭订阅.*?(?P<ios>http.*?)\n.*?",
        text,
        re.DOTALL
      )
      self.sub_links = res.groupdict()
      
  def walk(self, p: str):
    self.submodule_path = p
    if self.submodule_path in self.paths:
      self.set_links()
      self.request_links()

    if p == 'all':
      for it in self.paths:
        self.submodule_path = it
        self.set_links()
        self.request_links()

    if self.type:
      self.dirs = [self.type]

    for d in self.dirs:
      paths = [os.path.join(d, it) for it in os.listdir(d) if it.endswith(d)]
      paths.sort(key=lambda f: os.path.getmtime(f), reverse=True)
      print(paths)
      sites = ""
      for p in paths:
        with open(p, mode="r", encoding="utf-8") as f:
          sites += (f.read().strip() + '\n')
      with open(f"{d}/index", mode="w+", encoding="utf-8") as f:
        f.write(sites)
      encoded = base64.b64encode(sites.encode('utf-8')).decode('utf-8')
      with open(f"{d}/base64", mode="w+", encoding="utf-8") as f:
        f.write(encoded)


if __name__ == '__main__':
  Main('v2ray').walk(argv[1])