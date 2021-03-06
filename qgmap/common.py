from qgmap.config import config

doTrace = False

import json
import os
import decorator

backend = config['backend']

if backend == "PyQt5":
    from PyQt5.QtCore import pyqtSignal, QUrl, QUrlQuery, QXmlStreamReader
    from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
    from PyQt5.QtWebKit import QWebSettings
    from PyQt5.QtWebKitWidgets import QWebPage, QWebView
    from PyQt5.QtWidgets import QApplication

#elif backend == "PyQt4":
#    from PyQt4.QtCore import pyqtSignal, QUrl, QUrlQuery, QXmlStreamReader
#    from PyQt4.QtGui import QApplication
#    from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkRequest
#    from PyQt4.QtWebKit import QWebPage, QWebSettings, QWebView


@decorator.decorator
def trace(function, *args, **k):
    """Decorates a function by tracing the begining and
    end of the function execution, if doTrace global is True"""

    if doTrace: print("> " + function.__name__, args, k)
    result = function(*args, **k)
    if doTrace: print("< " + function.__name__, args, k, "->", result)
    return result


class _LoggedPage(QWebPage):
    @trace
    def javaScriptConsoleMessage(self, msg, line, source):
        print('JS: %s line %d: %s' % (source, line, msg))


class GeoCoder(QNetworkAccessManager):
    class NotFoundError(Exception):
        pass

    @trace
    def __init__(self, parent):
        super(GeoCoder, self).__init__(parent)

    @trace
    def geocode(self, location):
        url = QUrl("http://maps.googleapis.com/maps/api/geocode/xml")

        query = QUrlQuery()
        query.addQueryItem("address", location)
        query.addQueryItem("sensor", "false")

        url.setQuery(query)
        """
        url = QUrl("http://maps.google.com/maps/geo/")
        url.addQueryItem("q", location)
        url.addQueryItem("output", "csv")
        url.addQueryItem("sensor", "false")
        """
        request = QNetworkRequest(url)
        reply = self.get(request)
        while reply.isRunning():
            QApplication.processEvents()

        reply.deleteLater()
        self.deleteLater()
        return self._parseResult(reply)

    @trace
    def _parseResult(self, reply):
        xml = reply.readAll()
        reader = QXmlStreamReader(xml)
        while not reader.atEnd():
            reader.readNext()
            if reader.name() != "geometry": continue
            reader.readNextStartElement()
            if reader.name() != "location": continue
            reader.readNextStartElement()
            if reader.name() != "lat": continue
            latitude = float(reader.readElementText())
            reader.readNextStartElement()
            if reader.name() != "lng": continue
            longitude = float(reader.readElementText())
            return latitude, longitude
        raise GeoCoder.NotFoundError


class QGoogleMap(QWebView):
    @trace
    def __init__(self, parent, debug=True):
        super(QGoogleMap, self).__init__(parent)
        if debug:
            QWebSettings.globalSettings().setAttribute(
                QWebSettings.DeveloperExtrasEnabled, True)
            self.setPage(_LoggedPage())

        self.initialized = False
        self.loadFinished.connect(self.onLoadFinished)
        self.page().mainFrame().addToJavaScriptWindowObject(
            "qtWidget", self)

        basePath = os.path.abspath(os.path.dirname(__file__))
        url = 'file://' + basePath + '/qgmap.html'
        self.load(QUrl(url))

    @trace
    def onLoadFinished(self, ok):
        if self.initialized: return
        if not ok:
            print("Error initializing Google Maps")
        self.initialized = True
        self.centerAt(0, 0)
        self.setZoom(1)

    @trace
    def waitUntilReady(self):
        while not self.initialized:
            QApplication.processEvents()

    @trace
    def geocode(self, location):
        return GeoCoder(self).geocode(location)

    @trace
    def runScript(self, script):
        return self.page().mainFrame().evaluateJavaScript(script)

    @trace
    def centerAt(self, latitude, longitude):
        self.runScript("gmap_setCenter({},{})".format(latitude, longitude))

    @trace
    def setZoom(self, zoom):
        self.runScript("gmap_setZoom({})".format(zoom))

    @trace
    def center(self):
        center = self.runScript("gmap_getCenter()")
        return center.lat, center.lng

    @trace
    def centerAtAddress(self, location):
        try:
            latitude, longitude = self.geocode(location)
        except GeoCoder.NotFoundError:
            print("Not found {}".format(location))
            return None, None
        self.centerAt(latitude, longitude)
        return latitude, longitude

    @trace
    def addMarkerAtAddress(self, location, **extra):
        if 'title' not in extra:
            extra['title'] = location
        try:
            latitude, longitude = self.geocode(location)
        except GeoCoder.NotFoundError:
            return None
        return self.addMarker(location, latitude, longitude, **extra)

    @trace
    def addMarker(self, key, latitude, longitude, **extra):
        return self.runScript(
            "gmap_addMarker("
            "key={!r}, "
            "latitude={}, "
            "longitude={}, "
            "{}"
            "); "
                .format(key, latitude, longitude, json.dumps(extra)))

    @trace
    def moveMarker(self, key, latitude, longitude):
        return self.runScript(
            "gmap_moveMarker({!r}, {}, {});".format(key, latitude, longitude))

    @trace
    def setMarkerOptions(self, keys, **extra):
        return self.runScript(
            "gmap_changeMarker("
            "key={!r}, "
            "{}"
            "); "
                .format(keys, json.dumps(extra)))

    @trace
    def deleteMarker(self, key):
        return self.runScript(
            "gmap_deleteMarker("
            "key={!r} "
            "); ".format(key))

    mapMoved = pyqtSignal(float, float)
    mapClicked = pyqtSignal(float, float)
    mapRightClicked = pyqtSignal(float, float)
    mapDoubleClicked = pyqtSignal(float, float)

    markerMoved = pyqtSignal(str, float, float)
    markerClicked = pyqtSignal(str)
    markerDoubleClicked = pyqtSignal(str)
    markerRightClicked = pyqtSignal(str)
