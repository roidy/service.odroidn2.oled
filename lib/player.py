import xbmc


class XBMCPlayer(xbmc.Player):
    def __init__(self):
        super(XBMCPlayer, self).__init__()
        self._onAVStartedCallback = None
        self._onPlayBackStoppedCallback = None
        self._onPlayBackEndedCallback = None

    def setOnAVStartedCallback(self, callback):
        self._onAVStartedCallback = callback

    def setOnPlayBackStoppedCallback(self, callback):
        self._onPlayBackStoppedCallback = callback

    def setOnPlayBackEndedCallback(self, callback):
        self._onPlayBackEndedCallback = callback

    def onAVStarted(self):
        if (self._onAVStartedCallback is not None):
            self._onAVStartedCallback.onAVStarted()

    def onPlayBackStopped(self):
        if (self._onPlayBackStoppedCallback is not None):
            self._onPlayBackStoppedCallback.onPlayBackStopped()

    def onPlayBackEnded(self):
        if (self._onPlayBackEndedCallback is not None):
            self._onPlayBackEndedCallback.onPlayBackEnded()
