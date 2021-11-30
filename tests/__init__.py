import sys
import ctypes
import binascii
#import inspect      # beta only: return the name of the calling function

# load libraries from LD_LIBRARY_PATH
# give the user some pointers if they didn't README.md
try:
    lastlib = "libchacha.so"
    libcha = ctypes.CDLL(lastlib)
    print('loaded %s' % libcha._name)
    
    lastlib = "libpoly1305.so"
    libpoly = ctypes.CDLL(lastlib)
    print('loaded %s' % libpoly._name)
    
    lastlib = "libchachapoly_aead.so"
    libaead = ctypes.CDLL(lastlib)
    print('loaded %s' % libaead._name)
    
except Exception as e:
    print('exception loading %s: %s' % (lastlib, e))
    import os
    libpath = os.path.abspath(os.path.dirname(__file__))
    if libpath not in os.environ['LD_LIBRARY_PATH']:
        print('\nadd %s to LD_LIBRARY_PATH:\n' % libpath)
        sys.exit(1)

class AEAD(ctypes.Structure):
    """
    Class object mapping for C struct chachapolyaead_ctx.
    
    Returned by chacha20poly1305_init() and contains two instances
    of class ChaChaCTX - assigned to attributes 'main' and 'header', 
    repsectively.
    
    K_1 (stored in main.input) is used to crypt payload data.
    K_2 (stored in header.input) crypts payload size.
    """
    
    #_pack_ = 1
    _fields_ = [
                ('main', ChaChaCTX),
                ('header', ChaChaCTX)
                ]
