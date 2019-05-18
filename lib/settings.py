import xbmcaddon
from lib.logging import *

addon = xbmcaddon.Addon(id="service.odroidn2.oled")


def getSetting(id):
    return addon.getSetting(id).lower()


def getBool(id):
    value = getSetting(id).lower()
    if (value == "true"):
        return True
    else:
        return False


def getInt(id):
    return int(getSetting(id))


def getHex(id):
    return int(getSetting(id), 16)


class OledSettings:
    def __init__(self):
        self.readSettings()

    def readSettings(self):
        self._settingI2CAddress = getHex("i2c.address")
        self._settingdisplayType = getSetting("display.type")
        self._settingShortFormat = getBool("display.shortformat")
        self._settingBrightness = getInt("display.brightness")
        self._settingPlaybackBrightness = getInt("display.playbackbrightness")
        self._settingFont = getSetting("display.font")
        self._settingFlipDisplay = getBool("display.flip")
        self._settingClockOnlyMode = getBool("display.clockonlymode")
        self._settingHideIcons = getBool("display.hideicons")
        self._settingsHideSDRIcon = getBool("display.hidesdricon")
        self._settingsIconType = getSetting("display.icontype")

    def i2cAddress(self):
        return self._settingI2CAddress

    def displayType(self):
        return self._settingdisplayType

    def shortFormat(self):
        return self._settingShortFormat

    def brightness(self):
        return self._settingBrightness

    def playbackBrightness(self):
        return self._settingPlaybackBrightness

    def font(self):
        return self._settingFont

    def flipDisplay(self):
        return self._settingFlipDisplay

    def clockOnlyMode(self):
        return self._settingClockOnlyMode

    def hideIcons(self):
        return self._settingHideIcons

    def hideSRDIcon(self):
        return self._settingsHideSDRIcon

    def iconType(self):
        if self._settingsIconType == "solid":
            return True
        else:
            return False
