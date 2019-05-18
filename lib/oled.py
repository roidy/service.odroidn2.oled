from smbus2 import SMBus
from smbus2 import SMBusWrapper
from lib.logging import *
import time
import xbmcgui

CHARGEPUMP = 0x8D
COLUMNADDR = 0x21
COMSCANDEC = 0xC8
COMSCANINC = 0xC0
DISPLAYALLON = 0xA5
DISPLAYALLON_RESUME = 0xA4
DISPLAYOFF = 0xAE
DISPLAYON = 0xAF
EXTERNALVCC = 0x1
INVERTDISPLAY = 0xA7
MEMORYMODE = 0x20
NORMALDISPLAY = 0xA6
PAGEADDR = 0x22
SEGREMAP = 0xA0
SETCOMPINS = 0xDA
SETCONTRAST = 0x81
SETDISPLAYCLOCKDIV = 0xD5
SETDISPLAYOFFSET = 0xD3
SETHIGHCOLUMN = 0x10
SETLOWCOLUMN = 0x00
SETMULTIPLEX = 0xA8
SETPRECHARGE = 0xD9
SETSEGMENTREMAP = 0xA1
SETSTARTLINE = 0x40
SETVCOMDETECT = 0xDB
SWITCHCAPVCC = 0x2


class Oled:
    def __init__(self, i2c, displayType, flipDisplay):
        self._width = 128
        self._height = 64
        self._i2c = i2c
        self._flipDisplay = flipDisplay
        self._displayType = displayType
        self._pages = self._height // 8
        self._image = [0] * (self._width * self._height)
        try:
            self.bus = SMBus(2)
        except IOError:
            xbmcgui.Dialog().notification("OLED IO Error", "Please check your I2C address and controller type.", xbmcgui.NOTIFICATION_ERROR, 5000)
        if self._displayType == "128x64-sh1106":
            self.displayHeight32 = False
            self._initSH1106()
            self.display = self._displaySH1106
        elif self._displayType == "128x64-ssd1306":
            self.displayHeight32 = False
            self._initSSD1306_64()
            self.display = self._displaySSD1306
        elif self._displayType == "128x32-ssd1306":
            self.displayHeight32 = True
            self._initSSD1306_32()
            self.display = self._displaySSD1306
        self.clear()
        self.display()

    def isDisplayHeight32(self):
        return self.displayHeight32

    def _command(self, c):
        self.bus.write_byte_data(self._i2c, 0x00, c)

    def _initSH1106(self):
        self._command(DISPLAYOFF)
        self._command(NORMALDISPLAY)
        self._command(SETDISPLAYCLOCKDIV)
        self._command(0x80)
        self._command(SETMULTIPLEX)
        self._command(0x3F)
        self._command(SETDISPLAYOFFSET)
        self._command(0x00)
        self._command(SETSTARTLINE | 0x00)
        self._command(CHARGEPUMP)
        self._command(0x14)
        self._command(MEMORYMODE)
        self._command(0x00)
        if (self._flipDisplay):
            self._command(SEGREMAP)
            self._command(SETCOMPINS)
            self._command(PAGEADDR)
            self._command(COMSCANINC)
        else:
            self._command(SEGREMAP | 0x1)
            self._command(SETCOMPINS)
            self._command(PAGEADDR)
            self._command(COMSCANDEC)
        self._command(SETCONTRAST)
        self._command(0xCF)
        self._command(SETPRECHARGE)
        self._command(0xF1)
        self._command(SETVCOMDETECT)
        self._command(0x00)
        self._command(DISPLAYALLON_RESUME)
        self._command(NORMALDISPLAY)
        self._command(0x2e)
        self._command(DISPLAYON)

    def _initSSD1306_64(self):
        self._command(DISPLAYOFF)
        self._command(SETDISPLAYCLOCKDIV)
        self._command(0x80)
        self._command(SETMULTIPLEX)
        self._command(0x3F)
        self._command(SETDISPLAYOFFSET)
        self._command(0x0)
        self._command(SETSTARTLINE | 0x0)
        self._command(CHARGEPUMP)
        self._command(0x14)  # 0x14 0x2f
        self._command(MEMORYMODE)
        self._command(0x00)
        if (self._flipDisplay):
            self._command(SEGREMAP)
            self._command(COMSCANINC)
        else:
            self._command(SEGREMAP | 0x1)
            self._command(COMSCANDEC)
        self._command(SETCOMPINS)
        self._command(0x12)
        self._command(SETCONTRAST)
        self._command(0xCF)
        self._command(SETPRECHARGE)
        self._command(0xF1)
        self._command(SETVCOMDETECT)
        self._command(0x00)  # 0x40 0x00
        self._command(DISPLAYALLON_RESUME)
        self._command(NORMALDISPLAY)
        self._command(DISPLAYON)

    def _initSSD1306_32(self):
        self._command(DISPLAYOFF)
        self._command(SETDISPLAYCLOCKDIV)
        self._command(0x80)
        self._command(SETMULTIPLEX)
        self._command(0x1F)
        self._command(SETDISPLAYOFFSET)
        self._command(0x0)
        self._command(SETSTARTLINE | 0x0)
        self._command(CHARGEPUMP)
        self._command(0x14)  # 0x14 0x2f
        self._command(MEMORYMODE)
        self._command(0x00)
        if (self._flipDisplay):
            self._command(SEGREMAP)
            self._command(COMSCANINC)
        else:
            self._command(SEGREMAP | 0x1)
            self._command(COMSCANDEC)
        self._command(SETCOMPINS)
        self._command(0x02)
        self._command(SETCONTRAST)
        self._command(0xCF)
        self._command(SETPRECHARGE)
        self._command(0xF1)
        self._command(SETVCOMDETECT)
        self._command(0x00)  # 0x40 0x00
        self._command(DISPLAYALLON_RESUME)
        self._command(NORMALDISPLAY)
        self._command(DISPLAYON)

    def _displaySH1106(self):
        page = 0xB0
        step = self._width * 8
        for y in xrange(0, step * 8, step):
            self._command(page)
            self._command(0x02)
            self._command(0x10)
            page += 1

            buffer = []
            for x in xrange(self._width):
                byte = 0
                for n in xrange(0, step, self._width):
                    byte |= (self._image[x + y + n] & 0x01) << 8
                    byte >>= 1
                buffer.append(byte)

            # Write buffer data
            for i in xrange(0, len(buffer), 16):
                with SMBusWrapper(2) as bus:
                    bus.write_i2c_block_data(self._i2c, 0x40, buffer[i:i+16])

    def _displaySSD1306(self):
        buffer = []
        for page in xrange(self._pages):
            for x in xrange(self._width):
                bits = 0
                for bit in [0, 1, 2, 3, 4, 5, 6, 7]:
                    bits = bits << 1
                    bits |= self._image[x + ((page * 8 + 7 - bit) * self._width)]
                buffer.append(bits)

        self._command(COLUMNADDR)
        self._command(0)              # Column start address. (0 = reset)
        self._command(self._width - 1)   # Column end address.
        self._command(PAGEADDR)
        self._command(0)              # Page start address. (0 = reset)
        self._command(self._pages - 1)  # Page end address.

        # Write buffer data
        for i in xrange(0, len(buffer), 16):
            with SMBusWrapper(2) as bus:
                bus.write_i2c_block_data(self._i2c, 0x40, buffer[i:i+16])

    def clear(self):
        for i in xrange(self._width * self._height):
            self._image[i] = 0

    def close(self):
        self.clear()
        self.display()
        self.bus.close()

    def setBrightness(self, brightness):
        self._command(SETCONTRAST)
        if brightness == 16:
            self._command(255)
        else:
            self._command((brightness * 16) - 16)

    def getStringWidth(self, str, charset):
        charStride = charset[0][3]

        dashFix = 0
        for c in str:
            char = ord(c)
            if char == 45:
                dashFix += -3
            if char == 46:
                dashFix += -4

        return len(str) * charStride + dashFix + 3

    def drawIcons(self, info, x, y, center, solid, charset):
        if (center):
            width = 0
            for i in xrange(0, len(info)):
                w = self.getStringWidth(
                    info[i], charset)
                width += w + 4

            x = ((128 - width) // 2) + 4

        for i in xrange(0, len(info)):
            pos = self.drawString(
                info[i], x, y, solid, charset)
            x += pos + 4

    def drawString(self, str, x, y, solid, charset):
        charWidth = charset[0][0]
        charHeight = charset[0][1]
        charByteHeight = charset[0][2]
        charStride = charset[0][3]
        strWidth = len(str) * charStride - 1
        px = x
        py = y

        if solid:
            border = False
            for by in xrange(y - 2, y + 1 + charHeight + 1):
                for bx in xrange(x - 2, x + strWidth + 2):
                    self._image[bx + (by * self._width)
                                ] = 0
        else:
            border = True

        dashFix = 0
        for c in str:
            char = ord(c)
            if char == 32:
                px += charStride
            if char == 45:
                self._image[px + (py + 3) * self._width] = 1
                self._image[px + 1 + (py + 3) * self._width] = 1
                px += 3
                dashFix += -3
            if char == 46:
                self._image[px + (py + 6) * self._width] = 1
                px += 2
                dashFix += -4
            if char >= 48 and char <= 57:
                self._drawChar(char - 47, px, py, charWidth,
                               charByteHeight, charset)
                px += charStride
            elif char >= 65 and char <= 90:
                self._drawChar(char - 54, px, py, charWidth,
                               charByteHeight, charset)
                px += charStride

        if border:
            for bx in xrange(x - 2, x + strWidth + 2 + dashFix):
                self._image[bx + ((y - 3) * self._width)] = 1
                self._image[bx + ((y + 2 + charHeight) * self._width)] = 1

            for by in xrange(y - 2, y + 2 + charHeight):
                self._image[x - 3 + (by * self._width)] = 1
                self._image[x + 2 + strWidth + dashFix + (by * self._width)] = 1

        if solid:
            for by in xrange(y - 2, y + 1 + charHeight + 1):
                for bx in xrange(x - 2, x + strWidth + 2 + dashFix):
                    self._image[bx + (by * self._width)
                                ] = not self._image[bx + (by * self._width)]
            self._image[x - 2 +
                        ((y - 2) * self._width)] = 0
            self._image[x - 2 +
                        ((y + charHeight + 1) * self._width)] = 0

            self._image[x + strWidth + 1 + dashFix +
                        ((y - 2) * self._width)] = 0
            self._image[x + strWidth + 1 + dashFix +
                        ((y + charHeight + 1) * self._width)] = 0

        return len(str) * charStride + dashFix + 3

    def _drawChar(self, char, x, y, cw, cbh, chset):
        for sx in xrange(0, cw):
            for sy in xrange(0, cbh):
                dy = y
                chdata = chset[char][sx + sy * cw]
                for bit in [0, 1, 2, 3, 4, 5, 6, 7]:
                    self._image[(sx + x) + ((8 * sy) + dy) *
                                self._width] = (chdata >> bit) & 0x01
                    dy += 1

    def drawProgress(self, seconds, totalSeconds):
        if self.displayHeight32:
            y = 31
        else:
            y = 56

        for py in xrange(y - 3, y + 4):
            self._image[10 + (py * self._width)] = 1
            self._image[117 + (py * self._width)] = 1

        if seconds > 0 and totalSeconds > 0:
            progress = float(float(seconds) / float(totalSeconds) * 107.0)

            for x in range(107):

                if x <= progress:
                    self._image[(x + 10) + ((y - 1) * self._width)] = 1
                    self._image[(x + 10) + (y * self._width)] = 1
                    self._image[(x + 10) + ((y + 1) * self._width)] = 1
                else:
                    self._image[(x + 10) + ((y - 1) * self._width)] = 0
                    self._image[(x + 10) + (y * self._width)] = 0
                    self._image[(x + 10) + ((y + 1) * self._width)] = 0

    def drawTime(self, seconds, x, y, charset, fullsize=True, center=True):
        hours = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds = seconds % 60

        cw = charset[11][0]
        ch = charset[11][1]
        digit_stride = charset[11][2]
        colon_stride = charset[11][3]

        if fullsize and center:
            w = (digit_stride * 4) + colon_stride + colon_stride + cw
            x = (128 - w) / 2

        elif not fullsize and center:
            w = (digit_stride * 3) + colon_stride + cw
            x = (128 - w) / 2

        pos = x
        if fullsize:
            self._drawChar(hours, pos, y, cw, ch, charset)  # hours
            pos += digit_stride
            self._drawChar(10, pos, y, cw, ch, charset)  # :
            pos += colon_stride
        self._drawChar(minutes // 10, pos, y, cw, ch, charset)  # min 10
        pos += digit_stride
        self._drawChar(minutes % 10, pos, y, cw, ch, charset)  # min 1
        pos += digit_stride
        self._drawChar(10, pos, y, cw, ch, charset)  # :
        pos += colon_stride
        self._drawChar(seconds // 10, pos, y, cw, ch, charset)  # sec 10
        pos += digit_stride
        self._drawChar(seconds % 10, pos, y, cw, ch, charset)  # sec 1

    def drawTrack(self, track, x, y, charset):
        cw = charset[11][0]
        ch = charset[11][1]
        digit_stride = charset[11][2]
        pos = x

        self._drawChar(track // 10, pos, y, cw, ch, charset)  # Track 10
        pos += digit_stride
        self._drawChar(track % 10, pos, y, cw, ch, charset)  # Track 1
