# derived from https://gist.github.com/six519/28802627584b21ba1f6a
# unlicensed

import uno
import subprocess
import time
import os

from com.sun.star.beans import PropertyValue

from unoservice.util import PDF_FILTERS

LIBREOFFICE_DEFAULT_PORT = 6519
LIBREOFFICE_DEFAULT_HOST = "localhost"

LIBREOFFICE_IMPORT_TYPES = {
    "docx": {
        "FilterName": "MS Word 2007 XML"
    },
    "pdf": {
        "FilterName": "PDF - Portable Document Format"
    },
    "jpg": {
        "FilterName": "JPEG - Joint Photographic Experts Group"
    },
    "html": {
        "FilterName": "HTML Document"
    },
    "odp": {
        "FilterName": "OpenDocument Presentation (Flat XML)"
    },
    "pptx": {
        "FilterName": "Microsoft PowerPoint 2007 XML"
    }
}


class PythonLibreOffice(object):

    def __init__(self, host=LIBREOFFICE_DEFAULT_HOST, port=LIBREOFFICE_DEFAULT_PORT):
        self.host = host
        self.port = port
        self.local_context = uno.getComponentContext()
        self.resolver = self.local_context.ServiceManager.createInstanceWithContext("com.sun.star.bridge.UnoUrlResolver", self.local_context)
        self.connectionString = "socket,host=%s,port=%s;urp;StarOffice.ComponentContext" % (LIBREOFFICE_DEFAULT_HOST, LIBREOFFICE_DEFAULT_PORT)
        self.context = None
        self.desktop = None
        self.runUnoProcess()
        self.__lastErrorMessage = ""

        try:
            self.context = self.resolver.resolve("uno:%s" % self.connectionString)
            self.desktop = self.context.ServiceManager.createInstanceWithContext("com.sun.star.frame.Desktop", self.context)
        except Exception as e:
            self.__lastErrorMessage = str(e)

    @property
    def lastError(self):
        return self.__lastErrorMessage

    def terminateProcess(self):
        try:
            if self.desktop:
                self.desktop.terminate()
        except Exception as e:
            self.__lastErrorMessage = str(e)
            return False
        return True

    def convertFile(self, inputFilename):
        if self.desktop:
            tOldFileName = os.path.splitext(inputFilename)
            outputFilename = "%s.pdf" % tOldFileName[0]
            inputFormat = tOldFileName[1].replace(".", "")
            inputUrl = uno.systemPathToFileUrl(os.path.abspath(inputFilename))
            outputUrl = uno.systemPathToFileUrl(os.path.abspath(outputFilename))

            if inputFormat in LIBREOFFICE_IMPORT_TYPES:
                inputProperties = {"Hidden": True}
                inputProperties.update(LIBREOFFICE_IMPORT_TYPES[inputFormat])

                doc = self.desktop.loadComponentFromURL(inputUrl, "_blank", 0, self.propertyTuple(inputProperties))

                try:
                    doc.refresh()
                except Exception:
                    pass

                docFilter = self.getDocumentFilter(doc)
                if docFilter:
                    try:
                        doc.storeToURL(outputUrl, self.propertyTuple(docFilter))
                        doc.close(True)

                        return True
                    except Exception as e:
                        self.__lastErrorMessage = str(e)
        self.terminateProcess()
        return False

    def propertyTuple(self, propDict):
        properties = []
        for k,v in propDict.items():
            property = PropertyValue()
            property.Name = k
            property.Value = v
            properties.append(property)

        return tuple(properties)

    def getDocumentFilter(self, doc):
        for (service, pdf) in PDF_FILTERS:
            if doc.supportsService(service):
                return pdf

    def runUnoProcess(self):
        subprocess.Popen('soffice --headless --norestore --accept="%s"' % self.connectionString, shell=True, stdin=None, stdout=None, stderr=None)
        time.sleep(3)


if __name__ == "__main__":
    test_libreoffice = PythonLibreOffice()
    # convert MS Word Document file (docx) to PDF
    test_libreoffice.convertFile("/unoservice/fixtures/agreement.docx")