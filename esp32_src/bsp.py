from time import sleep
from HLModbusSlave import ModbusRegister, ModbusSlave
from machine import Pin, PWM
class Motor:
    def __init__(self, in1, in2):
        self.in1 = PWM(Pin(in1))
        self.in2 = PWM(Pin(in2))

    def speed(self, v):
        if v>0:
          self.in1.duty(v)
          self.in2.duty(0)
        elif v<0:
          self.in1.duty(0)
          self.in2.duty(-v)
        else:
          self.in1.duty(0)
          self.in2.duty(0)


motors = [Motor(23,22),Motor(21,19),Motor(18,5),Motor(17,16)]
out_pin = [Pin(4, Pin.OUT),Pin(2, Pin.OUT)]

is_move = False


def car_move(a, b):
    global is_move
    is_move = True
    print(a)
    spds =[ ((a[i] >> 8) - (a[i] & 0x00ff)) / 255 for i in range(4)]
    for i in range(4):
      motors[i].speed(spds[i]*4)
    


def car_io(a, b):
    if a[0] == 0xff00:
        out_pin[0].on()
    elif a[0] == 0x00:
        out_pin[0].off()



regs = [ModbusRegister(0, 4, [0, 0, 0, 0], [], None, car_move),
        ModbusRegister(4, 1, [0], [], None, car_io),
        ]
car_handler = ModbusSlave(1, regs, None)


def monitor():
    global is_move
    while True:
        if is_move:
            if time.perf_counter() - last_tick > 0.5:
                for i in range(4):
                  motors[i].speed(0)
                  car_handler.regs[0].reg = [0, 0, 0, 0]
        sleep(0.01)

import _thread
_thread.start_new_thread(monitor,())
def test():
  print("test")
  for i in range(4):
    motors[i].speed(800)
    sleep(2)
    motors[i].speed(-800)
    sleep(2)
    motors[i].speed(0)
if __name__ == "__main__":
  test()




