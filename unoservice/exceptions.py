
class ConverterException(Exception):
    pass


class SystemFailure(ConverterException):
    pass


class ConversionFailure(ConverterException):
    pass


class ConversionTimeout(SystemFailure):
    pass


def handle_timeout(signum, frame):
    raise ConversionTimeout('Conversion timed out.')
