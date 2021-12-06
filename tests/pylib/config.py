import sys
PY_VERSION = sys.version_info
print('%s called with Python version %s.%s' % (__name__,
                                                PY_VERSION.major,
                                                PY_VERSION.minor))
if PY_VERSION.major == 2:
    print("Python 3 required")
    sys.exit(1)

from configparser import SafeConfigParser

# Signal is used in class methods write_config() at the bottom
# of this file. Signal lock forces exection to conclude before
# other Signal operations can execute. 
#
# from facil.threadutils import Signal
# with Signal._lock():
#     config.write_config(a,b,c)
from .threadutils import Signal

class ToolConfig(SafeConfigParser):
    """ Return a config parser object with default values.
        """

    def __init__(self, filename, _DEFAULTS=[]):
        self.filename = filename
        self._DEFAULTS = _DEFAULTS
        #self.exchangelist = []
        SafeConfigParser.__init__(self)
        self.load()
        #self.init_defaults(self._DEFAULTS)
              
        #else:
        #    print "Critical parsing error. Config file %s does not contain default settings." % filename
        #    sys.exit(0)

        # upgrade from deprecated "currency" to "quote_currency"
        # todo: remove this piece of code again in a few months
        if self.has_option("gox", "currency"):
            self.set("gox", "quote_currency", self.get_string("gox", "currency"))
            self.remove_option("gox", "currency")
            self.save()

    def init_defaults(self, defaults):
        """add the missing default values, default is a list of defaults"""
        for (sect, opt, default) in defaults:
            self._default(sect, opt, default)

    def save(self):
        """save the config to the .ini file"""
        with open(self.filename, 'w') as configfile:
            self.write(configfile, space_around_delimiters=True)

    def load(self):
        """(re)load the config from the .ini file"""
        self.read(self.filename)

    def get_safe(self, sect, opt):
        """get value without throwing exception."""
        try:
            return self.get(sect, opt)

        except: # pylint: disable=W0702
            for (dsect, dopt, default) in self._DEFAULTS:
                if dsect == sect and dopt == opt:
                    self._default(sect, opt, default)
                    return default
            return ""

    def get_bool(self, sect, opt):
        """get boolean value from config"""
        return self.get_safe(sect, opt) == "True"

    def get_string(self, sect, opt):
        """get string value from config"""
        return self.get_safe(sect, opt)

    def get_int(self, sect, opt):
        """get int value from config"""
        vstr = self.get_safe(sect, opt)
        try:
            return int(vstr)
        except ValueError:
            return 0

    def get_float(self, sect, opt):
        """get int value from config"""
        vstr = self.get_safe(sect, opt)
        try:
            return float(vstr)
        except ValueError:
            return 0.0

    def _default(self, section, option, default):
        """create a default option if it does not yet exist"""
        if not self.has_section(section):
            self.add_section(section)
        if not self.has_option(section, option):
            self.set(section, option, default)
            self.save()
    
    ##
    # functions for managing .ini file options
    #
    def write_config_setting(self, section, option, value):
        """write a setting in the ini file"""
        with Signal._lock:
            setting = self.get_string(section, option)
            self.set(section, option, str(value))
            self.save()
    
    def toggle_setting(self, alternatives, section, option, direction):
        """toggle a setting in the ini file"""
        with Signal._lock:
            setting = self.get_string(section, option)
            try:
                newindex = (alternatives.index(setting) + direction) % len(alternatives)
            except ValueError:
                newindex = 0
            self.set(section, option, alternatives[newindex])
            self.save()
        return alternatives[newindex]

