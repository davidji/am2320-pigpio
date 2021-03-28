import time
import pigpio
from struct import unpack

class AM2320:
    DEFAULT_BUS = 1
    ADDRESS = 0xB8>>1 # the data sheet says 0xB8, but that is it's 'write' address
    WAKE_UP_CODE = 0x00
    READ_REGISTER_CODE = 0x03
    WRITE_REGISTERS_CODE = 0x10
    HIGH_HUMIDITY_REGISTER = 0x00
    LOW_HUMIDITY_REGISTER = 0x01
    HIGH_TEMPERATURE_REGISTER = 0x02
    LOW_TEMPERATURE_REGISTER = 0x03
    MODEL_LOW_REGISTER = 0x08
    MODEL_HIGH_REGISTER = 0x09
    VERSION_NUMBER_REGISTER = 0x0A
    DEVICE_ID_REGISTER_0 = 0x0B
    DEVICE_ID_REGISTER_1 = 0x0C
    DEVICE_ID_REGISTER_2 = 0x0D

    def __init__(self, pi, bus = DEFAULT_BUS):
        self.pi = pi
        self.bus = bus
    
    def wake_up(self):
        handle = self.pi.i2c_open(self.bus, AM2320.ADDRESS)
        if handle >= 0:
            try:
                self.pi.i2c_write_device(handle, [AM2320.WAKE_UP_CODE])
            except:
                pass
            finally:
                self.pi.i2c_close(handle)
            time.sleep(0.001)
        else:
            raise Exception("no handle")


    def read_registers(self, address, count):
        handle = self.pi.i2c_open(self.bus, AM2320.ADDRESS)
        if handle >= 0:
            try:
                self.pi.i2c_write_device(handle, [AM2320.READ_REGISTER_CODE, address, count])
                time.sleep(0.0016)
                (recv_count, recv_data) = self.pi.i2c_read_device(handle, count + 4)
                if (recv_count == count + 4 
                    and recv_data[0] == AM2320.READ_REGISTER_CODE 
                    and recv_data[1] == count):
                    return recv_data[2:2+count]
                elif recv_data < 0:
                    raise Exception("Error response {}". format(recv_count))
                else:
                    raise Exception("response is malformed: size {} , data: {}".format(recv_count, recv_data))
            finally:
                self.pi.i2c_close(handle)
        else:
            raise Exception("no handle")
        return None

    def read_temp_humidity(self):
        data = self.read_registers(AM2320.HIGH_HUMIDITY_REGISTER, 4)
        (humidity, temperature) = unpack(">HH", data)
        return tuple(float(x)/10.0 for x in (temperature, humidity))

if __name__ == '__main__':
    pi = pigpio.pi()
    am2320 = AM2320(pi,1)
    am2320.wake_up()
    print(am2320.read_temp_humidity())

