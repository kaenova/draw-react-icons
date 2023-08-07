# NOTE: If you wnat to develop this, make sure you have dist.zip inside embedding-updater folder
# Download the dist.zip through here: https://drive.google.com/file/d/13Fnm3ingRAmDnhu2P8p8wROBfhbD7QwL/view?usp=sharing

import os
import pathlib
import zipfile
import utils
import core
import data

import tensorflow as tf

from huggingface_hub import hf_hub_download

script_path = pathlib.Path(__file__).parent.resolve()

# Huggingface model related
huggingface_hub_model = "kaenova/quick_draw_cnn"
huggingface_file = "quick_draw_embed_500000_input_64_64_1.h5"
model_path = hf_hub_download(huggingface_hub_model, huggingface_file)
model = tf.keras.models.load_model(model_path)
input_size = model.input.type_spec.shape[1:]  # (H, W, 1)

# For Github Action Automation on Getting Image
# Extracting Zip from artifact
print("Extracting dist.zip")
zip_file = os.path.join(script_path, "dist.zip")
icons_folder = os.path.join(script_path, "dist")
with zipfile.ZipFile(zip_file, "r") as zip_ref:
    zip_ref.extractall(icons_folder)
print("Extract complete")

# Print stat
parent_id_list = os.listdir(icons_folder)
parent_id_stat = {}
for parent_id in parent_id_list:
    parent_path = os.path.join(icons_folder, parent_id)
    total = utils.count_files_inside_folder(parent_path)
    parent_id_stat[parent_id] = total
parent_id_stat["total"] = sum(parent_id_stat.values())
print("artifact stat:", parent_id_stat)

# Now image is saved on the same directory of this script with a folder 'dist'
# output: ['vsc', 'rx', 'tfi', 'ri', 'lu', 'di', 'ti', 'fc', 'im', 'si', 'fa', 'lia', 'hi', 'hi2', 'bs', 'gi', 'sl', 'bi', 'fi', 'cg', 'wi', 'tb', 'io', 'ci', 'gr', 'pi', 'io5', 'ai', 'md', 'go', 'fa6']
# The output above are folders of icon group. Inside that folders are jpeg of an icon with a code in the filename

# TODO: Do smart image update
# Smart update (don't update available icon, only update icon that isn't in the database)
update_parent_id = core.smart_update(icons_folder)
print(update_parent_id)

# TODO: Create icon embedding based on icon to be saved into database, use the filename of the icon as key
icon = data.IconData(
    "a",
    "b",
    os.path.join(script_path ,"dist/ai/AiFillAccountBook.jpg"),
    resize_shape=input_size[:2],
    invert_image=False,
)
print(icon.to_embeddings(model))

exit(0)
