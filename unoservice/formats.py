from lxml import etree

from unoservice.util import normalize_extension

NS = {'oor': 'http://openoffice.org/2001/registry'}
PREFIX = '{%s}' % NS['oor']


class Formats(object):
    FILES = [
        '/usr/lib/libreoffice/share/registry/writer.xcd',
        '/usr/lib/libreoffice/share/registry/calc.xcd',
        '/usr/lib/libreoffice/share/registry/impress.xcd',
        '/usr/lib/libreoffice/share/registry/draw.xcd',
    ]

    def __init__(self):
        self.mime_types = {}
        self.extensions = {}
        for xcd_file in self.FILES:
            doc = etree.parse(xcd_file)
            path = './*[@oor:package="org.openoffice.TypeDetection"]/node/node'
            for tnode in doc.xpath(path, namespaces=NS):
                node = {}
                for prop in tnode.findall('./prop'):
                    name = prop.get('%sname' % PREFIX)
                    for value in prop.findall('./value'):
                        node[name] = value.text

                name = node.get('Type', node.get('UIName'))
                name = node.get('PreferredFilter', name)

                media_type = node.get('MediaType')
                if media_type is not None:
                    self.mime_types[media_type] = name
                extensions = node.get('Extensions', '')
                for ext in extensions.split(' '):
                    ext = normalize_extension(ext)
                    if ext is not None:
                        self.extensions[ext] = name

    def get_filter(self, extension, mime_type):
        if mime_type in self.mime_types:
            return self.mime_types.get(mime_type)
        if extension in self.extensions:
            return self.extensions.get(extension)


if __name__ == "__main__":
    formats = Formats()
    print(formats.get_filter('docx', None))
