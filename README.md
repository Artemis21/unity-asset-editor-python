# unity-asset-editor-python
Unity asset editor in Python.


## Example usuage

```python
from src import AssetFile, Reader, Writer

with open open('test_file.assets', 'rb') as in_file:
    reader = Reader(in_file)
    asset_file = reader.read(AssetFile)

# We can access attributes of the file.
print(asset_file.header.unity_version)

# Or the assets inside it...
asset = asset_file.objects[0]
print(asset.file_name)

# We can even save the assets to files
with open('test_out.object', 'wb') as f:
    f.write(asset.file_content)

# We can also edit the assets
asset_file.objects[0].file_name = 'renamedfile.txt'
asset_file.objects[0].file_content = b'New asset content.'

# And recompile the asset file
with open('test_file_edited.assets', 'wb') as out_file:
    writer = Writer(out_file)
    writer.write(asset_file)
```
