"""
MODBUS SLAVE
winxos 20191220
"""
from binascii import unhexlify
class ModbusRegister:
    def __init__(self,
                 start,
                 length,
                 reg,
                 dev,
                 read= None,
                 write= None):
        self.start, self.length = start, length
        self.reg, self.dev = reg, dev
        self.read, self.write = read, write


class ModbusSlave:
    def __init__(self, address, regs, sender):
        self.regs = regs
        self.address = address
        self.send = sender

    def read_registers(self, addr, sz):
        """
        0x03 function
        :return: True/False, Value
        """
        for reg in self.regs:
            if reg.start <= addr < reg.start + reg.length:
                if reg.read:
                    reg.read(reg.reg, reg.dev)
                    offset = addr - reg.start
                    return True, reg.reg[offset: offset + sz]

    def write_register(self, addr, value):
        """
        0x06 function
        :return: True/False, Value
        """
        for reg in self.regs:
            if reg.start <= addr < reg.start + reg.length:
                if reg.write:
                    reg.reg[addr - reg.start] = value
                    reg.write(reg.reg, reg.dev)
                    return True, 0

    def write_registers(self, addr, sz, data):
        """
        0x10 function
        the [addr, addr+sz) should in the range of a ModbusRegister
        :return: True/False, Value
        """
        for reg in self.regs:
            if reg.start <= addr and addr + sz < reg.start + reg.length:
                if reg.write:
                    reg.reg[addr - reg.start:] = data[:]
                    reg.write(reg.reg, reg.dev)
                    return True, 0

    def deal(self, data: bytes):
        print(data)
        if data[0] != 0x00 and data[0] != self.address:
            return False
        if data[1] == 0x03:
            self.read_registers(data[2] * 256 + data[3], data[4] * 256 + data[5])
        elif data[1] == 0x06:
            self.write_register(data[2] * 256 + data[3], data[4] * 256 + data[5])
        elif data[1] == 0x10:
            self.write_registers(data[2] * 256 + data[3], data[4] * 256 + data[5], data[6:])

    def receive(self, data):
        """
        call this while received data
        :param data: bytes
        """
        pass

    def receive_ascii(self, data):
        """
        modbus ascii protocol
        :return: True/False, Value
        """
        if not data.startswith(":") or not data.endswith("\r\n") or len(data) % 2 == 0:
            return False
        mdata = unhexlify(data[1:-2])
        print(mdata)
        if sum(mdata) % 0x100 != 0:
            return False
        self.deal(mdata[:-1])


def rd(a, b):
    print(a)


def wt(a, b):
    print(a)


def s(n):
    print(n)


r = [1, 2, 3]
d = [4, 5, 6]


def test():
    regs = [ModbusRegister(0, 4, r, d, rd, wt)]
    a = ModbusSlave(1, regs, s)
    a.read_registers(1, 1)
    a.write_registers(1, 2, [5, 6])
    a.receive_ascii(":010300000001FB\r\n")


if __name__ == '__main__':
    test()


