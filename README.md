# Odroid N2 OLED Driver
Odroid N2 Kodi service for controlling an i2c oled display.
![Untitled](https://user-images.githubusercontent.com/4118048/57568209-06776c80-73dc-11e9-87ea-a966197095fd.jpg)

### Download:- [Odroid N2 Oled Driver v0.1.5](https://github.com/roidy/service.odroidn2.oled/releases/download/v0.1.5/service.odroidn2.oled.zip)

__NOTE: This addon is in no way connected to OpenVFD and does not require OpenVFD to work, if you already have a vfd.conf file that is setup for the N2 then please remove it.__

## Supported Displays
This addon supports 4 pin I2C 128x32 or 128x64 oled displays that use either the SSD1306 or SH1106 driver.
This addon does NOT support SPI displays commonly identified by the display having 7 pins, although most SPI displays can be converted into I2C, this requires board level soldering and is beyond the scope of this documentation. 

Common displays that have been tested with this addon.
* 1.3" 128x64 SH1106 Oled
* 0.96" 128x64 SSD1306 Oled
* 0.91" 128x32 SSD1306 Oled

![DSC_0048](https://user-images.githubusercontent.com/4118048/57567801-9dd9c100-73d6-11e9-8ba5-455794c6b8df.JPG)

## Connecting a I2C Display
__WARNING!!__
__Incorrectly wiring anything to the GPIO of your Odroid N2 may cause permanent damage to your device. Please double/triple check your wiring before powering on your N2.__

The 4 pin I2C oled display should be connected to pins 1,3,5 and 6 of the Odroid N2's GPIO. Pin 1 is closest to the N2's audio jack.

__The pinout of the oled may vary so be careful to wire the correct pins from the N2 to the correct pins of your particular display.__

|N2 Pin|N2 Pin Name|OLED Pin|
|------|-----------|--------|
|1|3.3V Power|VCC/VDD|
|3|I2C_EE_M2_SDA|SDA|
|5|I2C_EE_M2_SCL|SCL|
|6|Ground|GND|

![figure-17](https://user-images.githubusercontent.com/4118048/57568074-3f164680-73da-11e9-8af6-2f7e831ae3ba.png)

## Connecting a SPI Display
This information is accurate for the 2.42" displays as show in the picture, other SPI displays may work but are not guarenteed to.

|N2 Pin|N2 Pin Name|OLED Pin|
|-----|-----|-----|
|1|3.3V Power|VCC|
|6|Ground|GND|
|16|GPIOX_0|RES|
|18|GPIOX_1|DC|
|19|SPI_A_MOSI|SDA|
|23|SPI_A_SCLK|SCL|
|39|Ground|CS|

The Oled CS pin can be tied to any free ground pin on the Odroid N2 (9,14,20,25,30,34 or 39)

![gfx](https://user-images.githubusercontent.com/4118048/87856703-bcabdf80-c918-11ea-9c72-06ebb335b5d4.jpg)

__NOTE: SPI is disabled by default on the Odroid N2 and must be activated by issuing the following command from a SSH session__

```
mount -o remount,rw /flash
fdtput -t s /flash/dtb.img /soc/cbus@ffd00000/spi@13000/spidev@0 status "okay"
fdtput -t s /flash/dtb.img /soc/cbus@ffd00000/spi@13000 status "okay"
reboot
```

## Configuration
If your oled shows nothing or corrupted content then the addon may be configured to the wrong display size or driver or I2C address, simply open the addons settings page and select the correct display size and driver combination and the correct I2C address.

## Disclaimer
__The author of this addon and the following documentation accepts no responsibility for damage caused by the use of this software package/addon and it's documentation.__
