import logging, copy
from colorama import Fore, Style, init  # Colorama is a library for coloring console output. Not mandatory, but looks pretty.

## Polyphony - also it's not friendly with logging, may need to implement a custom colorizer formatter based on properties of the logging records.
# logger.debug("foo Test", color.Cyan ) (or event.Received|event.Requested)
# CURRENTLY USING GREEN CYAN RED
# GREEN - Received
# CYAN - Sent
# RED - Exception/Error

class Events():
    REQUESTED = 'REQUESTED'
    RECEIVED = 'RECEIVED'

class ColorFormatter(logging.Formatter):
    def __init__(self, fmt):
        super().__init__()
        self.fmt = fmt
        self.LevelsFormatters = {
            logging.ERROR: Fore.RED + self.fmt + Fore.RESET,
            logging.CRITICAL: Fore.RED + self.fmt + Fore.RESET
        }
        self.EventFormatters = {
            Events.REQUESTED: Fore.CYAN + self.fmt + Fore.RESET,
            Events.RECEIVED: Fore.GREEN + self.fmt + Fore.RESET
        }
    
    def format(self, record):
        formatter = logging.Formatter(self.fmt)
        copyrecord = copy.copy(record)
        if hasattr(copyrecord, 'event') and copyrecord.event in self.EventFormatters:
            formatter = logging.Formatter(self.EventFormatters.get(copyrecord.event))
        else:
            copyrecord.event = 'LOGGING'
        if record.levelno in self.LevelsFormatters:
            formatter = logging.Formatter(self.LevelsFormatters.get(copyrecord.levelno))
        return formatter.format(copyrecord)
