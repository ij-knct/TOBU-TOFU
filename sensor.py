# import GPIO and so on
from enum import Enum
import spidev


# copy test.py to this file

# 0106 Touch
# 0108 Temperature
# 0109 Light
# 0116 Distance

class Sensors(Enum):
    TOUCH = 0
    TEMPERATURE = 1
    LIGHT = 2
    DISTANCE = 3
    DEFAULT = 4


class Sensor:
    spi = spidev.SpiDev()

    def __init__(self, pin: int = 0):
        self.PIN = pin
        self.data = 0
        self.spi.open(0, 0)

    def __del__(self):
        self.spi.close()

    def mapped_data(self, data: int, in_min: int, in_max: int, out_min: int, out_max: int):
        """
        データを指定の範囲に変換するメソッド
        :param data: 変換したいデータ
        :param in_min: 変換前のデータの最低値
        :param in_max: 変換前のデータの最大値
        :param out_min: 変換後のデータの最低値
        :param out_max: 変換後のデータの最大値
        :return: 変換後のデータ
        """
        return (data - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

    def mapped_data(self, out_min: int, out_max: int):
        """
        データを指定の範囲に変換するメソッド
        :param out_min: 変換後のデータの最低値
        :param out_max: 変換後のデータの最大値
        :return: 変換後のデータ
        """
        return self.mapped_data(self.data, 0, 1023, out_min, out_max)

    def read_data(self):
        adc = spi.xfer2([1, (8 + self.PIN) << 4, 0])
        self.data = ((adc[1] & 3) << 8) + adc[2]
        return self.data

    @classmethod
    def generate(cls, sensor: Sensors, pin: int = 0):
        if sensor == Sensors.TOUCH:
            return TouchSensor(pin)

        elif sensor == Sensors.TEMPERATURE:
            return TemperatureSensor(pin)

        elif sensor == Sensors.LIGHT:
            return LightSensor(pin)

        elif sensor == Sensors.DISTANCE:
            return DistanceSensor(pin)


class TouchSensor(Sensor):

    def __init__(self, pin: int = 0):
        super(TouchSensor, self).__init__(pin)

    def __del__(self):
        super(TouchSensor, self).__del__()


class TemperatureSensor(Sensor):

    def __init__(self, pin: int = 0):
        super(TemperatureSensor, self).__init__(pin)

    def __del__(self):
        super(TemperatureSensor, self).__del__()


class LightSensor(Sensor):

    def __init__(self, pin: int = 0):
        super(LightSensor, self).__init__(pin)

    def __del__(self):
        super(LightSensor, self).__del__()


class DistanceSensor(Sensor):

    def __init__(self, pin: int = 0):
        super(DistanceSensor, self).__init__(pin)

    def __del__(self):
        super(DistanceSensor, self).__del__()
