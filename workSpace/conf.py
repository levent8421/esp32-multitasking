import json

conf_data = None

__CONF_FILE_NAME = 'conf.json'

def load_conf():
  global conf_data
  with open(__CONF_FILE_NAME, 'r') as f:
    conf_str = f.read()
    
  try:
    conf_data = json.loads(conf_str)
  except e:
    print('Configuration file read fail!', e)

def get(name):
  return conf_data[name]

load_conf()


