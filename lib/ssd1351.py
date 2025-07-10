# SSD1351 OLED Display Driver for MicroPython
# Based on various open-source implementations

import time

from machine import Pin
from micropython import const
from misakifont import MisakiFont

# Constants for SSD1351 commands
SSD1351_CMD_SETCOLUMN = const(0x15)
SSD1351_CMD_SETROW = const(0x75)
SSD1351_CMD_WRITERAM = const(0x5C)
SSD1351_CMD_READRAM = const(0x5D)
SSD1351_CMD_SETREMAP = const(0xA0)
SSD1351_CMD_STARTLINE = const(0xA1)
SSD1351_CMD_DISPLAYOFFSET = const(0xA2)
SSD1351_CMD_DISPLAYALLOFF = const(0xA4)
SSD1351_CMD_DISPLAYALLON = const(0xA5)
SSD1351_CMD_NORMALDISPLAY = const(0xA6)
SSD1351_CMD_INVERTDISPLAY = const(0xA7)
SSD1351_CMD_FUNCTIONSELECT = const(0xAB)
SSD1351_CMD_DISPLAYOFF = const(0xAE)
SSD1351_CMD_DISPLAYON = const(0xAF)
SSD1351_CMD_PRECHARGE = const(0xB1)
SSD1351_CMD_DISPLAYENHANCE = const(0xB2)
SSD1351_CMD_CLOCKDIV = const(0xB3)
SSD1351_CMD_SETVSL = const(0xB4)
SSD1351_CMD_SETGPIO = const(0xB5)
SSD1351_CMD_PRECHARGE2 = const(0xB6)
SSD1351_CMD_SETGRAY = const(0xB8)
SSD1351_CMD_USELUT = const(0xB9)
SSD1351_CMD_PRECHARGELEVEL = const(0xBB)
SSD1351_CMD_VCOMH = const(0xBE)
SSD1351_CMD_CONTRASTABC = const(0xC1)
SSD1351_CMD_CONTRASTMASTER = const(0xC7)
SSD1351_CMD_MUXRATIO = const(0xCA)
SSD1351_CMD_COMMANDLOCK = const(0xFD)
SSD1351_CMD_HORIZSCROLL = const(0x96)
SSD1351_CMD_STOPSCROLL = const(0x9E)
SSD1351_CMD_STARTSCROLL = const(0x9F)


class SSD1351:
    def __init__(self, width, height, spi, dc, cs, rst, rate=10000000):
        self.width = width
        self.height = height
        self.spi = spi
        self.dc = dc
        self.cs = cs
        self.rst = rst
        self.rate = rate
        self.buffer = bytearray(width * height * 2)
        self.cs.init(Pin.OUT, value=1)
        self.dc.init(Pin.OUT, value=0)
        self.rst.init(Pin.OUT, value=1)
        self.init_display()

    def init_display(self):
        """Initialize the display"""
        self.reset()

        # Unlock the display
        self.write_cmd(SSD1351_CMD_COMMANDLOCK)
        self.write_data(0x12)

        self.write_cmd(SSD1351_CMD_COMMANDLOCK)
        self.write_data(0xB1)

        # Display off
        self.write_cmd(SSD1351_CMD_DISPLAYOFF)

        # Set clock div
        self.write_cmd(SSD1351_CMD_CLOCKDIV)
        self.write_data(0xF1)  # 7:4 = Oscillator Freq, 3:0 = CLK Div Ratio

        # Set MUX ratio
        self.write_cmd(SSD1351_CMD_MUXRATIO)
        self.write_data(0x7F)  # 127

        # Set display offset
        self.write_cmd(SSD1351_CMD_DISPLAYOFFSET)
        self.write_data(0x00)

        # Set start line
        self.write_cmd(SSD1351_CMD_STARTLINE)
        self.write_data(0x00)

        # Set remap
        self.write_cmd(SSD1351_CMD_SETREMAP)
        self.write_data(0x74)  # Color depth and rotation settings

        # Set GPIO
        self.write_cmd(SSD1351_CMD_SETGPIO)
        self.write_data(0x00)

        # Function select
        self.write_cmd(SSD1351_CMD_FUNCTIONSELECT)
        self.write_data(0x01)  # Internal VDD regulator

        # Set VSL
        self.write_cmd(SSD1351_CMD_SETVSL)
        self.write_data(0xA0)
        self.write_data(0xB5)
        self.write_data(0x55)

        # Set contrast
        self.write_cmd(SSD1351_CMD_CONTRASTABC)
        self.write_data(0xC8)
        self.write_data(0x80)
        self.write_data(0xC8)

        self.write_cmd(SSD1351_CMD_CONTRASTMASTER)
        self.write_data(0x0F)

        # Set precharge
        self.write_cmd(SSD1351_CMD_PRECHARGE)
        self.write_data(0x32)

        self.write_cmd(SSD1351_CMD_PRECHARGE2)
        self.write_data(0x01)

        # Set VCOMH
        self.write_cmd(SSD1351_CMD_VCOMH)
        self.write_data(0x05)

        # Normal display mode
        self.write_cmd(SSD1351_CMD_NORMALDISPLAY)

        # Clear screen
        self.fill(0)
        self.show()

        # Turn on the display
        self.write_cmd(SSD1351_CMD_DISPLAYON)

    def reset(self):
        """Reset the display"""
        self.rst.value(1)
        time.sleep_ms(50)
        self.rst.value(0)
        time.sleep_ms(50)
        self.rst.value(1)
        time.sleep_ms(50)

    def write_cmd(self, cmd):
        """Write a command to the display"""
        self.dc.value(0)  # Command mode
        self.cs.value(0)  # Select display
        self.spi.write(bytes([cmd]))
        self.cs.value(1)  # Deselect display

    def write_data(self, data):
        """Write data to the display"""
        self.dc.value(1)  # Data mode
        self.cs.value(0)  # Select display
        self.spi.write(bytes([data]))
        self.cs.value(1)  # Deselect display

    def write_data_buf(self, buf):
        """Write a buffer of data to the display"""
        self.dc.value(1)  # Data mode
        self.cs.value(0)  # Select display
        self.spi.write(buf)
        self.cs.value(1)  # Deselect display

    def set_addr_window(self, x0, y0, x1, y1):
        """Set the display window for pixel data"""
        self.write_cmd(SSD1351_CMD_SETCOLUMN)
        self.write_data(x0)
        self.write_data(x1)

        self.write_cmd(SSD1351_CMD_SETROW)
        self.write_data(y0)
        self.write_data(y1)

        self.write_cmd(SSD1351_CMD_WRITERAM)

    def color565(self, r, g, b):
        """Convert RGB888 to RGB565 format"""
        return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)

    def pixel(self, x, y, color):
        """Set a pixel at position (x, y) to the given color"""
        if 0 <= x < self.width and 0 <= y < self.height:
            idx = (y * self.width + x) * 2
            self.buffer[idx] = color >> 8
            self.buffer[idx + 1] = color & 0xFF

    def fill(self, color):
        """Fill the entire display with a specific color"""
        for i in range(0, len(self.buffer), 2):
            self.buffer[i] = color >> 8
            self.buffer[i + 1] = color & 0xFF

    def fill_rect(self, x, y, w, h, color):
        """Fill a rectangle area with a specific color"""
        for _y in range(y, y + h):
            for _x in range(x, x + w):
                self.pixel(_x, _y, color)

    def hline(self, x, y, w, color):
        """Draw a horizontal line"""
        self.fill_rect(x, y, w, 1, color)

    def vline(self, x, y, h, color):
        """Draw a vertical line"""
        self.fill_rect(x, y, 1, h, color)

    def rect(self, x, y, w, h, color):
        """Draw a rectangle outline"""
        self.hline(x, y, w, color)
        self.hline(x, y + h - 1, w, color)
        self.vline(x, y, h, color)
        self.vline(x + w - 1, y, h, color)

    def show_bitmap(self, fd, x, y, color, size=1):
        for row in range(7):
            for col in range(7):
                if (0x80 >> col) & fd[row]:
                    for i in range(size):
                        for j in range(size):
                            self.pixel(x + col * size + i,
                                       y + row * size + j,
                                       color)

    def text(self, text, x, y, color, font=None, size=1):
        mf = MisakiFont()
        for c in text:
            d = mf.font(ord(c), flgz=True)
            self.show_bitmap(d, x, y, color, size)
            x += 8 * size
            if x >= 128:
                x = 0
                y += 8 * size
            if y >= 128:
                y = 0

    def show(self):
        """Update the display with the current buffer"""
        self.set_addr_window(0, 0, self.width - 1, self.height - 1)
        self.write_data_buf(self.buffer)
