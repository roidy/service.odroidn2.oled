import xbmc
import xbmcaddon

addonName = xbmcaddon.Addon().getAddonInfo('id')
addonVersion = xbmcaddon.Addon().getAddonInfo('version')


def log(message, level=xbmc.LOGDEBUG):
    xbmc.log('{0} v{1} -> {2}'.format(addonName,
                                      addonVersion, str(message)), level)


def logError(message):
    log(message, xbmc.LOGERROR)


def logWarning(message):
    log(message, xbmc.LOGWARNING)


def logNotice(message):
    log(message, xbmc.LOGNOTICE)
