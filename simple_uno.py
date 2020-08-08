import uno
from com.sun.star.beans import PropertyValue
from com.sun.star.lang import DisposedException, IllegalArgumentException
from com.sun.star.connection import NoConnectException
from com.sun.star.io import IOException
from com.sun.star.script import CannotConvertException
from com.sun.star.uno import RuntimeException

DESKTOP = "com.sun.star.frame.Desktop"
RESOLVER = "com.sun.star.bridge.UnoUrlResolver"
CONNECTION = (
    "socket,host=localhost,port=2002,tcpNoDelay=1;urp;StarOffice.ComponentContext"
)

context = uno.getComponentContext()
resolver = context.ServiceManager.createInstanceWithContext(RESOLVER, context)
context = resolver.resolve("uno:%s" % CONNECTION)
svc = context.ServiceManager.createInstanceWithContext(DESKTOP, context)
