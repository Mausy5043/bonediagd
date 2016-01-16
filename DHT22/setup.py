from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages, Extension
import sys

# Pick the right extension to compile based on the platform.
extensions = []

extensions.append(Extension("bonediagd_DHT.BBB_DHT22_driver",
                ["src/BBB_DHT22_driver.c", "src/common_dht_read.c", "src/bbb_dht_read.c", "src/bbb_mmio.c"],
                libraries=['rt'],
                extra_compile_args=['-std=gnu99']))

# Call setuptools setup function to install package.
# Original code by T. DiCola
setup(name            = 'bonediagd_DHT',
    version           = '0.0.1',
    author            = 'Mausy5043',
    author_email      = '',
    description       = 'Library to get readings from the DHT11, DHT22, and AM2302 humidity and temperature sensors on a Beaglebone Black.',
    license           = 'MIT',
    url               = '',
    packages          = find_packages(),
    ext_modules       = extensions)
