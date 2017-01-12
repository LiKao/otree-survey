import sys

import logging
logger = logging.getLogger(__name__)

# Taken from http://stackoverflow.com/questions/6949395/is-there-a-way-to-get-a-line-number-from-an-elementtree-element
#
# Force python XML parser not faster C accelerators
# because we can't hook the C implementation
sys.modules['_elementtree'] = None
import xml.etree.ElementTree as XML

# This extension of the XML-Parser allows us to retrieve the
# Line number from the elements for better error reporting
class LineNumberingParser(XML.XMLParser):
        def _start(self, *args, **kwargs):
                # Here we assume the default XML parser which is expat
                # and copy its element position attributes into output Elements
                element = super(self.__class__, self)._start(*args, **kwargs)
                element.start_line_number = self.parser.CurrentLineNumber
                element.start_column_number = self.parser.CurrentColumnNumber
                element.start_byte_index = self.parser.CurrentByteIndex
                return element

        def _end(self, *args, **kwargs):
                element = super(self.__class__, self)._end(*args, **kwargs)
                element.end_line_number = self.parser.CurrentLineNumber
                element.end_column_number = self.parser.CurrentColumnNumber
                element.end_byte_index = self.parser.CurrentByteIndex
                return element

def XmlParse(filename):
    logger.info("Reading XML File %s" % filename)
    return XML.parse(filename, parser=LineNumberingParser())