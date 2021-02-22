"""Tool for editing Unity assets."""
from .reader_writers import AssetFile
from .streams import Reader, Writer


ASSET_FILE = (
    '/home/artemis/.local/share/Steam/steamapps/common/'
    'The Battle of Polytopia/Polytopia_Data/sharedassets0.assets'
)
# ASSET_FILE = './test2.assets'

stream_in = open(ASSET_FILE, 'rb')
reader = Reader(stream_in)
stream_out = open('./test.assets', 'wb')
writer = Writer(stream_out)

assets = reader.read(AssetFile)
writer.write(assets)
