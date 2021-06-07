import xbmcaddon
import datetime
import time
from lib.logging import *
from lib.oled import *
from lib.charset import *
from lib.settings import *
from lib.player import *

codecs = {"ac3": "DD",
          "eac3": "DD",
          "dtshd_ma": "DTS-MA",
          "dca": "DTS",
          "truehd": "DD-HD",
          "aac": "AAC",
          "wmapro": "WMA",
          "mp3float": "MP3",
          "flac": "FLAC",
          "dsd_lsbf_planar": "DSD",
          "aac": "AAC",
          "pcm_s16be": "PCM",
          "mp2": "MP2",
          "pcm_u8": "PCM"}
channels = {"1": "1.0",
            "2": "2.0",
            "3": "2.1",
            "4": "4.0",
            "5": "5.0",
            "6": "5.1",
            "7": "7.0",
            "8": "7.1"}


class Monitor(xbmc.Monitor):
    def __init__(self):
        super(Monitor, self).__init__()
        self._settingsChangedCallback = None
        self._ScreensaverActivatedCallback = None
        self._ScreensaverDeactivatedCallback = None

    def setSettingsChangedCallback(self, callback):
        self._settingsChangedCallback = callback

    def onSettingsChanged(self):
        if (self._settingsChangedCallback is not None):
            self._settingsChangedCallback.onSettingsChanged()

    def setScreensaverActivatedCallback(self, callback):
        self._ScreensaverActivatedCallback = callback

    def onScreensaverActivated(self):
        if (self._ScreensaverActivatedCallback is not None):
            self._ScreensaverActivatedCallback.onScreensaverActivated()

    def setScreensaverDeactivatedCallback(self, callback):
        self._ScreensaverDeactivatedCallback = callback

    def onScreensaverDeactivated(self):
        if (self._ScreensaverDeactivatedCallback is not None):
            self._ScreensaverDeactivatedCallback.onScreensaverDeactivated()


class OledAddon():
    def __init__(self, monitor):
        self._player = XBMCPlayer()
        self._player.setOnAVStartedCallback(self)
        self._player.setOnPlayBackStoppedCallback(self)
        self._player.setOnPlayBackEndedCallback(self)
        self._videoAudioCodec = None
        self._videoAudioChannels = None
        self._monitor = monitor
        self._monitor.setSettingsChangedCallback(self)
        self._monitor.setScreensaverActivatedCallback(self)
        self._monitor.setScreensaverDeactivatedCallback(self)
        self._settings = OledSettings()
        self._settings.readSettings()
        self._font = self.getFont(self._settings.font())
        self._largeFont = self.getLargeFont(self._settings.font())
        self._status = "idle"
        self._wait = 0
        self._totalTimeOld = 0
        self._totalTime = 0
        self._oled = Oled(self._settings.i2cAddress(),
                          self._settings.displayType(),
                          self._settings.flipDisplay())
        self._oled.setBrightness(self._settings.brightness())

    def __del__(self):
        self._oled.close()

    def onAVStarted(self):
        self._oled.setBrightness(self._settings.playbackBrightness())
        if (not self._settings.clockOnlyMode()):
            self._oled.clear()
            if (xbmc.Player().isPlayingVideo()):
                self._status = "video"
                if (not self._oled.isDisplayHeight32() and not self._settings.hideIcons()):
                    info = self.getVideoDetails()
                    self._oled.drawIcons(info, 0, 6, True, self._settings.iconType(), fiveBySevenFullset)
            elif (xbmc.Player().isPlayingAudio()):
                self._status = "audio"
                if (not self._oled.isDisplayHeight32() and not self._settings.hideIcons()):
                    info = self.getAudioDetails()
                    self._oled.drawIcons(["TRACK"], 2 if self._settings.iconType() else 3, 6, False, self._settings.iconType(), fiveBySevenFullset)
                    self._oled.drawIcons(info, 50, 6, False, self._settings.iconType(), fiveBySevenFullset)

    def onPlayBackEnded(self):
        self._oled.clear()
        self._oled.setBrightness(self._settings.brightness())
        self._status = "waiting"
        self._wait = 0

    def onPlayBackStopped(self):
        self._oled.clear()
        self._oled.setBrightness(self._settings.brightness())
        self._status = "waiting"
        self._wait = 0

    def onSettingsChanged(self):
        self._settings.readSettings()
        self._font = self.getFont(self._settings.font())
        self._largeFont = self.getLargeFont(self._settings.font())
        self._oled = Oled(self._settings.i2cAddress(),
                          self._settings.displayType(),
                          self._settings.flipDisplay())
        self._oled.setBrightness(self._settings.brightness())

    def onScreensaverDeactivated(self):
        if self._status == "off":
            self._status = "idle"
        if (self._status == "video"):
            self._oled.setBrightness(self._settings.playbackBrightness())

    def onScreensaverActivated(self):
        if (self._status != "video" and self._status != "audio" and not self._settings.clockwhilescreensaver()):
            self._status = "off"
        if (self._status == "video"):
            self._oled.setBrightness(self._settings.brightness())

    def getFont(self, font):
        if (font == "5x7 dot matrix"):
            return dotmatrix
        if (font == "7 segment"):
            return sevenSeg

    def getLargeFont(self, font):
        if (font == "5x7 dot matrix"):
            return dotmatrixLarge
        if (font == "7 segment"):
            return sevenSegLarge

    def getHDRStatus(self):
        try:
            with open("/sys/class/amhdmitx/amhdmitx0/config") as fp:
                for line in fp:
                    if ":" in line:
                        parts = line.split(":")
                        if parts[0].strip() == "EOTF":
                            if (parts[1].strip().upper() == "SDR" and self._settings.hideSRDIcon()):
                                return None
                            else:
                                return parts[1].strip()
        except IOError:
            return None
        return None

    def run(self):
        while not self._monitor.abortRequested():
            if self._monitor.waitForAbort(0.5):
                break
            self.update()
        self._oled.close()

    def getVideoDetails(self):
        info = []
        audioCodec = xbmc.getInfoLabel("VideoPlayer.AudioCodec")
        self._videoAudioCodec = audioCodec
        audioChannels = xbmc.getInfoLabel("VideoPlayer.AudioChannels")
        self._videoAudioChannels = audioChannels
        resolution = xbmc.getInfoLabel("VideoPlayer.VideoResolution")
        hdr = self.getHDRStatus()
        logNotice("Video Resolution: " + resolution)
        logNotice("Video Audio codec: " + audioCodec)
        logNotice("Video Audio channels: " + audioChannels)
        if (audioCodec in codecs):
            info.append(codecs[audioCodec])
        if (audioChannels in channels):
            info.append(channels[audioChannels])
        if (resolution == "4K"):
            info.append(resolution)
        else:
            if (int(resolution) < 720):
                info.append("SD")
            else:
                info.append(resolution)
        if (hdr is not None):
            info.append(hdr.upper())
        return info

    def checkAudioDetails(self):
        if (not self._oled.isDisplayHeight32() and not self._settings.hideIcons()):
            audioCodec = xbmc.getInfoLabel("VideoPlayer.AudioCodec")
            audioChannels = xbmc.getInfoLabel("VideoPlayer.AudioChannels")

            if audioCodec != self._videoAudioCodec or audioChannels != self._videoAudioChannels:
                self._oled.clear()
                info = self.getVideoDetails()
                self._oled.drawIcons(info, 0, 6, True, self._settings.iconType(), fiveBySevenFullset)

    def getAudioDetails(self):
        info = []
        audioCodec = xbmc.getInfoLabel("MusicPlayer.Codec")
        audioSamplerate = xbmc.getInfoLabel("MusicPlayer.BitRate")
        logNotice("Music Audio Codec: " + audioCodec)
        logNotice("Music Audio Samplerate: " + audioSamplerate)
        if (audioCodec in codecs):
            info.append(codecs[audioCodec])
        if (audioSamplerate.isdigit()):
            info.append(audioSamplerate)
        return info

    def update(self):
        # Fix for Kodi's broken onPlayBackStopped
        # Wait a couple of seconds to make sure playback has stopped
        # and we havent just changed track
        if self._status == "waiting":
            self._wait += 1
            if self._wait >= 4:
                self._status = "idle"
        ############################################################

        if self._status == "off":
            self._oled.clear()
            self._oled.display()

        if self._status == "idle":
            now = datetime.datetime.today()
            seconds = (now.hour * 60) + now.minute
            self._oled.drawTime(
                seconds, 0, 16 - (self._oled.isDisplayHeight32() * 16), self._largeFont, False, True)
            self._oled.display()

        if self._status == "video":
            try:
                self._totalTimeOld = self._totalTime
                self.checkAudioDetails()
                videotype = xbmc.Player().getPlayingFile()
                videotype = videotype.split(":")
                if videotype[0] == "pvr":
                    elapsedTime = xbmc.getInfoLabel("PVR.EpgEventElapsedTime")
                    totalTime = xbmc.getInfoLabel("PVR.EpgEventDuration")
                    elapsedTime = elapsedTime.split(":")
                    totalTime = totalTime.split(":")
                    if len(elapsedTime) == 3:
                        elapsedTime = 3600*int(elapsedTime[0]) + 60*int(elapsedTime[1]) + int(elapsedTime[2])
                    else:
                        elapsedTime = 60*int(elapsedTime[0]) + int(elapsedTime[1])
                    if len(totalTime) == 3:
                        totalTime = 3600*int(totalTime[0]) + 60*int(totalTime[1]) + int(totalTime[2])
                    else:
                        totalTime = 60*int(totalTime[0]) + int(totalTime[1])
                    if totalTime < 1:
                        elapsedTime = int(xbmc.Player().getTime())
                        totalTime = int(xbmc.Player().getTotalTime())
                else:
                    elapsedTime = int(xbmc.Player().getTime())
                    totalTime = int(xbmc.Player().getTotalTime())
                self._totalTime = totalTime
                remainingTime = totalTime - elapsedTime
                if self._settings.displayTimeElapsed():
                    playtime = elapsedTime
                else:
                    playtime = remainingTime
                if (playtime >= 0):
                    self._oled.drawProgress(elapsedTime, totalTime)
                    if (totalTime < 3600 and self._settings.shortFormat()):
                        if self._totalTimeOld >= 3600:
                            self._oled.clear()
                            if (not self._oled.isDisplayHeight32() and not self._settings.hideIcons()):
                                info = self.getVideoDetails()
                                self._oled.drawIcons(info, 0, 6, True, self._settings.iconType(), fiveBySevenFullset)
                        self._oled.drawTime(playtime, 0, 20 - (self._oled.isDisplayHeight32() * 20), self._font, False, True)
                        
                    else:
                        self._oled.drawTime(playtime, 0, 20 - (self._oled.isDisplayHeight32() * 20), self._font, True, True)
                    self._oled.display()
                 
            except:
                pass

        if self._status == "audio":
            try:
                elapsedTime = xbmc.getInfoLabel("Player.Time")
                totalTime = xbmc.getInfoLabel("Player.Duration ")
                elapsedTime = elapsedTime.split(":")
                totalTime = totalTime.split(":")
                if len(elapsedTime) == 3:
                    elapsedTime = 3600*int(elapsedTime[0]) + 60*int(elapsedTime[1]) + int(elapsedTime[2])
                else:
                    elapsedTime = 60*int(elapsedTime[0]) + int(elapsedTime[1])
                if len(totalTime) == 3:
                    totalTime = 3600*int(totalTime[0]) + 60*int(totalTime[1]) + int(totalTime[2])
                else:
                    totalTime = 60*int(totalTime[0]) + int(totalTime[1])
                remainingTime = totalTime - elapsedTime
                if self._settings.displayTimeElapsed():
                    playtime = elapsedTime
                else:
                    playtime = remainingTime
                if (playtime >= 0):
                    self._oled.drawProgress(elapsedTime, totalTime)
                    if (xbmc.getInfoLabel("MusicPlayer.TrackNumber") != ""):
                        self._oled.drawTrack(int(xbmc.getInfoLabel("MusicPlayer.TrackNumber")), 0, 20 - (self._oled.isDisplayHeight32() * 20), self._font)
                    #self._oled.drawTrack(int(xbmc.getInfoLabel("MusicPlayer.PlaylistPosition ")), 0, 20 - (self._oled.isDisplayHeight32() * 20), self._font)
                    self._oled.drawTime(playtime, 48, 20 - (self._oled.isDisplayHeight32() * 20), self._font, False, False)
                    self._oled.display()
            except:
                pass

if __name__ == "__main__":
    logNotice('Service started')
    monitor = Monitor()
    oled = OledAddon(monitor)
    oled.run()
    logNotice('Service stopped')
