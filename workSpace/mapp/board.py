import machine

class BoardContext:
  def __init__(self):
    pass

class MicroPythonBoardContext(BoardContext):
  def __init__(self):
    super().__init__()
    
  @staticmethod
  def build_pin(pin_no, mode):
    return machine.Pin(pin_no, mode)
    
  def pin_out(self, pin_no, value):
    if pin_no in self.__pin_cache:
      pin = self.__pin_cache[pin_no]
    else:
      pin = MicroPythonBoardContext.build_pin(pin_no, machine.Pin.OUT)
      self.__pin_cache[pin_no] = pin
    pin.value(value)

