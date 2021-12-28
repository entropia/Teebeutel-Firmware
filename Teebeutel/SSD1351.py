import framebuf
from machine import Pin, SPI
from framebuf import FrameBuffer
import time


def delay(wait: int):
    time.sleep(wait / 1000)


class Display(FrameBuffer):
    DEBUG = True

    SSD1351_WIDTH = 128
    SSD1351_HEIGHT = 128
    SSD1351_CMD_SETCOLUMN = [0x15]
    SSD1351_CMD_SETROW = [0x75]
    SSD1351_CMD_WRITERAM = [0x5C]
    SSD1351_CMD_READRAM = [0x5D]
    SSD1351_CMD_SETREMAP = [0xA0]
    SSD1351_CMD_STARTLINE = [0xA1]
    SSD1351_CMD_DISPLAYOFFSET = [0xA2]
    SSD1351_CMD_DISPLAYALLOFF = [0xA4]
    SSD1351_CMD_DISPLAYALLON = [0xA5]
    SSD1351_CMD_NORMALDISPLAY = [0xA6]
    SSD1351_CMD_INVERTDISPLAY = [0xA7]
    SSD1351_CMD_FUNCTIONSELECT = [0xAB]
    SSD1351_CMD_DISPLAYOFF = [0xAE]
    SSD1351_CMD_DISPLAYON = [0xAF]
    SSD1351_CMD_PRECHARGE = [0xB1]
    SSD1351_CMD_DISPLAYENHANCE = [0xB2]
    SSD1351_CMD_CLOCKDIV = [0xB3]
    SSD1351_CMD_SETVSL = [0xB4]
    SSD1351_CMD_SETGPIO = [0xB5]
    SSD1351_CMD_PRECHARGE2 = [0xB6]
    SSD1351_CMD_SETGRAY = [0xB8]
    SSD1351_CMD_USELUT = [0xB9]
    SSD1351_CMD_PRECHARGELEVEL = [0xBB]
    SSD1351_CMD_VCOMH = [0xBE]
    SSD1351_CMD_CONTRASTABC = [0xC1]
    SSD1351_CMD_CONTRASTMASTER = [0xC7]
    SSD1351_CMD_MUXRATIO = [0xCA]
    SSD1351_CMD_COMMANDLOCK = [0xFD]
    SSD1351_CMD_HORIZSCROLL = [0x96]
    SSD1351_CMD_STOPSCROLL = [0x9E]
    SSD1351_CMD_STARTSCROLL = [0x9F]

    def __init__(self, spi_id: int, cs: int, dc: int, res: int, freq=10000000):
        self.buffer = bytearray(self.SSD1351_WIDTH * self.SSD1351_HEIGHT * 2)
        super().__init__(self.buffer,
                         self.SSD1351_WIDTH,
                         self.SSD1351_HEIGHT,
                         framebuf.RGB565)

        self.spi = SPI(spi_id, freq)
        self.cs = Pin(cs, Pin.OUT, value=1)
        self.dc = Pin(dc, Pin.OUT, value=0)
        self.res = Pin(res, Pin.OUT, value=0)

    def set_cs(self, value: int):
        self.cs.value(value)

    def set_dc(self, value: int):
        self.dc.value(value)

    def set_res(self, value: int):
        self.res.value(value)

    def write_data(self, data: list):
        self.set_cs(0)
        self.set_dc(1)
        self.spi.write(bytearray(data))
        self.set_cs(1)

    def write_command(self, data: list):
        self.set_cs(0)
        self.set_dc(0)
        self.spi.write(bytearray(data))
        self.set_cs(1)

    def set_gram_pointer(self, column: int, row: int):
        self.write_command(self.SSD1351_CMD_SETCOLUMN)
        self.write_data([column])
        self.write_data([self.SSD1351_WIDTH-1])
        self.write_command(self.SSD1351_CMD_SETROW)
        self.write_data([row])
        self.write_data([self.SSD1351_HEIGHT-1])

    # cheap fill
    def cheap_fill(self, color):
        self.set_gram_pointer(0, 0)
        self.write_command(self.SSD1351_CMD_WRITERAM)
        color_fill_byte = color * self.SSD1351_WIDTH
        self.set_cs(0)
        self.set_dc(1)
        for i in range(0, self.SSD1351_HEIGHT):
            self.spi.write(bytearray(color_fill_byte))
        self.set_cs(1)

    def init(self):
        self.set_cs(0)
        self.set_res(0)
        delay(500)
        self.set_res(1)
        delay(500)

        self.write_command(self.SSD1351_CMD_COMMANDLOCK)  # command lock
        self.write_data([0x12])
        self.write_command(self.SSD1351_CMD_COMMANDLOCK)  # command lock
        self.write_data([0xB1])

        self.write_command(self.SSD1351_CMD_DISPLAYOFF)  # display off
        self.write_command(self.SSD1351_CMD_DISPLAYALLOFF)  # ?

        self.set_gram_pointer(0, 0)

        self.write_command(self.SSD1351_CMD_CLOCKDIV)
        self.write_data([0xF1])

        self.write_command(self.SSD1351_CMD_MUXRATIO)
        self.write_data([0x7F])

        self.write_command(self.SSD1351_CMD_STARTLINE)
        self.write_data([0x00])

        self.write_command(self.SSD1351_CMD_DISPLAYOFFSET)
        self.write_data([0x00])

        self.write_command(self.SSD1351_CMD_SETREMAP)
        self.write_data([0x66])  # 65,536 Colors Mode, 180 degree rotated

        self.write_command(self.SSD1351_CMD_SETGPIO)
        self.write_data([0x00])

        self.write_command(self.SSD1351_CMD_FUNCTIONSELECT)
        self.write_command([0x01])

        self.write_command(self.SSD1351_CMD_SETVSL)
        self.write_data([0xA0])
        self.write_data([0xB5])
        self.write_data([0x55])

        self.write_command(self.SSD1351_CMD_CONTRASTABC)
        self.write_data([0xC8])
        self.write_data([0x80])
        self.write_data([0xC0])

        self.write_command(self.SSD1351_CMD_CONTRASTMASTER)
        self.write_data([0x0F])

        self.write_command(self.SSD1351_CMD_PRECHARGE)
        self.write_data([0x32])

        self.write_command(self.SSD1351_CMD_DISPLAYENHANCE)
        self.write_data([0xA4])
        self.write_data([0x00])
        self.write_data([0x00])

        self.write_command(self.SSD1351_CMD_PRECHARGELEVEL)
        self.write_data([0x17])

        self.write_command(self.SSD1351_CMD_PRECHARGE2)
        self.write_data([0x01])

        self.write_command(self.SSD1351_CMD_VCOMH)
        self.write_data([0x05])

        self.write_command(self.SSD1351_CMD_NORMALDISPLAY)

        self.cheap_fill([0x00, 0x00])

        self.write_command(self.SSD1351_CMD_DISPLAYON)

    def deinit(self):
        self.write_command(self.SSD1351_CMD_DISPLAYOFF)
        self.write_command(self.SSD1351_CMD_FUNCTIONSELECT)
        self.write_data([0x00])

    def show(self):
        self.set_gram_pointer(0, 0)
        self.write_command(self.SSD1351_CMD_WRITERAM)
        self.set_cs(0)
        self.set_dc(1)
        self.spi.write(self.buffer)
        self.set_cs(1)

    def rgb_to_rgb565(self, red: int, green: int, blue: int):
        return (int(blue / 255 * 31) << 11) | (int(red / 255 * 31) << 5) | (int(green / 255 * 31))
