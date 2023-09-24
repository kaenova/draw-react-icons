# Py-Script Main Files

1. `api.py`: For serving an API to embed request image and query to Database
1. `icon-selector.py`: Checking hash of parent id to smart upload into `embed-gen.py`. This file will generate a json that have all parent id that needs to be updated
1. `embed-gen.py`: Reading zip from generated `node-script/image-generator` and json from `icon-selector.py` to smart update the icons
1. `update-checksum.py`: Updating checksum from generated json from `icon-selector.py`
