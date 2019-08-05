from setuptools import setup
import os

os.system('git clone https://github.com/mukulhase/WebWhatsapp-Wrapper.git &&' +
          'mv WebWhatsapp-Wrapper/webwhatsapi . &&' +
          'rm -rf WebWhatsapp-Wrapper')

setup(
   install_requires=[
      'asn1crypto',
      'certifi',
      'cffi',
      'cryptography',
      'future',
      'numpy',
      'protobuf',
      'pycparser',
      'python-axolotl',
      'python-axolotl-curve25519',
      'python-dateutil',
      'python-magic',
      'python-telegram-bot',
      'selenium',
      'six',
      'telegram',
      'typing',
      'urllib3'
   ], #external packages as dependencies
)
