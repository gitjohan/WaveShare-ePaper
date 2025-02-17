# /*****************************************************************************
# * | File        :	  epdconfig.py
# * | Author      :   Waveshare team
# * | Function    :   Hardware underlying interface
# * | Info        :
# *----------------
# * | This version:   V1.0
# * | Date        :   2019-06-21
# * | Info        :   
# ******************************************************************************
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

from os import path
import sys
import time

sys.path.append(r'/home/wannes/wisc')
from wanlib import loglvl, wisclogger, dtn


class RaspberryPi:
    # Pin definition
    RST_PIN = 17  # active low
    DC_PIN = 25  # high = data, low = command
    CS_PIN = 8  # active low
    BUSY_PIN = 24  # active high
    """
    ALSO USED (hardware spidev)
    GPIO 10 --> MOSI
    GPIO 11 --> CLK
    """

    def __init__(self):
        wisclog.debug("eink epd init")
        import spidev
        import RPi.GPIO

        self.GPIO = RPi.GPIO
        # SPI device, bus = 0, device = 0
        self.SPI = spidev.SpiDev(0, 0)

    def digital_write(self, pin, value):
        self.GPIO.output(pin, value)

    def digital_read(self, pin):
        return self.GPIO.input(pin)

    def delay_ms(self, delaytime):
        time.sleep(delaytime / 1000.0)

    def spi_writebyte(self, data):
        self.SPI.writebytes(data)

    def module_init(self):
        self.GPIO.setmode(self.GPIO.BCM)
        self.GPIO.setwarnings(False)
        self.GPIO.setup(self.RST_PIN, self.GPIO.OUT)
        self.GPIO.setup(self.DC_PIN, self.GPIO.OUT)
        self.GPIO.setup(self.CS_PIN, self.GPIO.OUT)
        self.GPIO.setup(self.BUSY_PIN, self.GPIO.IN)
        wisclog.deep("spi open for eink")
        self.SPI.open(0, 0)
        self.SPI.max_speed_hz = 4000000
        # SPI mode as two bit pattern of clock polarity and phase [CPOL|CPHA], min: 0b00 = 0, max: 0b11 = 3
        self.SPI.mode = 0b00
        return 0

    def module_exit(self):
        wisclog.deep("spi close for eink")
        self.SPI.close()
        self.GPIO.output(self.RST_PIN, 0)
        self.GPIO.output(self.DC_PIN, 0)
        self.GPIO.cleanup([self.RST_PIN, self.DC_PIN, self.CS_PIN, self.BUSY_PIN])


fn = path.basename(__file__)
wisclog = wisclogger(loglvl, fn, category='ink')
loginfo = f"appstart {fn.ljust(20)}: loglvl {loglvl}, {wisclog.logfile}"
wisclog.warning(loginfo)
print(f"{dtn('log')} {loginfo}")

# os.path.exists('/sys/bus/platform/drivers/gpiomem-bcm2835'):
implementation = RaspberryPi()

for func in [x for x in dir(implementation) if not x.startswith('_')]:
    setattr(sys.modules[__name__], func, getattr(implementation, func))
