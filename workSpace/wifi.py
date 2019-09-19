import network
import time
import conf
import led
import machine

wlan = None

# 此处使用timer实现wifi链接状态检查，为的是尽早释放主进程，否则upycraft将识别不到开发板
def __build_checker(callback, timer):
  def checker(t):
    if wlan.isconnected():
      timer.deinit()
      callback()
    else:
      print('Waiting wifi!')
  return checker
  
def init_wifi(callback):
  global wlan
  wifi_conf = conf.get('wifi')
  wlan = network.WLAN(network.STA_IF)
  wlan.active(True)
  wlan.disconnect()
  print('Connect to ', wifi_conf['ssid'], wifi_conf['password'])
  wlan.connect(wifi_conf['ssid'], wifi_conf['password'])
  wifi_timer = machine.Timer(-1)
  checker = __build_checker(callback, wifi_timer)
  wifi_timer.init(period=1000, mode=machine.Timer.PERIODIC, callback=checker)

def connect(callback):
  init_wifi(callback)




