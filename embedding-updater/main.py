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
