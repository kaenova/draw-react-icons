# NOTE: If you wnat to develop this, make sure you have dist.zip inside embedding-updater folder
# Download the dist.zip through here: https://drive.google.com/file/d/13Fnm3ingRAmDnhu2P8p8wROBfhbD7QwL/view?usp=sharing

import os
import pathlib
import zipfile

# For Github Action Automation on Getting Image
# Extracting Zip from artifact
script_path = pathlib.Path(__file__).parent.resolve()
zip_file = os.path.join(script_path, "dist.zip")
icons_folder = os.path.join(script_path, "dist")
with zipfile.ZipFile(zip_file,"r") as zip_ref:
    zip_ref.extractall(icons_folder)

# Now image is saved on the same directory of this script with a folder 'dist'
print(os.listdir(icons_folder))
# output: ['vsc', 'rx', 'tfi', 'ri', 'lu', 'di', 'ti', 'fc', 'im', 'si', 'fa', 'lia', 'hi', 'hi2', 'bs', 'gi', 'sl', 'bi', 'fi', 'cg', 'wi', 'tb', 'io', 'ci', 'gr', 'pi', 'io5', 'ai', 'md', 'go', 'fa6']
# The output above are folders of icon group. Inside that folders are jpeg of an icon with a code in the filename

# TODO: Do smart image update
# Smart update (don't update available icon, only update icon that isn't in the database)

# TODO: Create icon embedding based on icon to be saved into database, use the filename of the icon as key
