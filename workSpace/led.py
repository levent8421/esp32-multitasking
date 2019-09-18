from machine import Pin

class StatusLed:
  def __init__(self, pin_num):
    self.__pin = Pin(pin_num, Pin.OUT)
    self.__stat = False
    self.off()
    
  def on(self):
    self.__stat = True
    self.__pin.value(0)
    
  def off(self):
    self.__stat = False
    self.__pin.value(1)
    
  def switch(self):
    if(self.__stat):
      self.off()
    else:
      self.on()
    
status_led = StatusLed(2)
