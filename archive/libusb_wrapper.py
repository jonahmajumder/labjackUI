# libusb wrappers

from ctypes import cdll, util

LIBNAME = 'libusb-1.0.0'

libc = cdll.LoadLibrary(util.find_library(LIBNAME))

libc.libusb_init()

libc.libusb_exit(None)