from distutils.core import setup
setup(
  name = 'download_thingspeak',
  packages = ['download_thingspeak'], # this must be the same as the name above
  version = '1.2',
  description = 'Download data from a thingspeak channel using their API',
  author = 'Mike Smith',
  author_email = 'm.t.smith@sheffield.ac.uk',
  url = 'https://github.com/lionfish0/download_thingspeak.git',
  download_url = 'https://github.com/lionfish0/download_thingspeak/archive/1.01.tar.gz',
  keywords = ['thingspeak'],
  classifiers = [],
  install_requires=['requests'],
)

