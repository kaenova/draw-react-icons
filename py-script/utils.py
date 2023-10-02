import os
import zipfile
import typing
import threading
import queue
import argparse
import json

from checksumdir import dirhash


def parse_arg_embed_generator(
    default_zip_path, default_json_path, embedder_dict, indexing_methods
):
    arg_parser = argparse.ArgumentParser(
        "Embedding Updater",
        "This program is a runner to run an embedding inference for an react-icons image that are bundled in a zip file and only run for inputted josn file. The image of the emdeds need to have a background of black and the foreground of white. You can invert the image using --invert argument",
    )
    arg_parser.add_argument(
        "--input-zip",
        default=default_zip_path,
        help="Path of input zip file",
    )
    arg_parser.add_argument(
        "--input-json",
        default=default_json_path,
        help="Path of input json file",
    )
    arg_parser.add_argument(
        "--embedder",
        choices=list(embedder_dict.keys()),
        default=list(embedder_dict.keys())[0],
        help="Embedder model to embed the image",
    )
    arg_parser.add_argument(
        "--invert",
        help="Invert image black and white",
        type=bool,
        default=True,
    )
    arg_parser.add_argument(
        "--normalize",
        help="True image to [0..1] range",
        type=bool,
        default=True,
    )
    arg_parser.add_argument(
        "--qdrant-endpoint",
        help="Qdrant Cloud endpoint URI",
        default=os.environ["QDRANT_ENDPOINT"],
    )
    arg_parser.add_argument(
        "--qdrant-api-key",
        help="Qdrant Cloud API Key",
        default=os.environ["QDRANT_API_KEY"],
    )
    arg_parser.add_argument(
        "--upload-batch",
        help="Number of batch to be uploaded, for rough estimation there are 44000 icons",
        type=int,
        default=500,
    )
    arg_parser.add_argument(
        "--indexing",
        choices=indexing_methods,
        help="Indexing method on milvus if collection is not created",
        required=True,
    )
    return arg_parser.parse_args()


def parse_arg_checksum_gen(default_zip_path, default_json_path):
    arg_parser = argparse.ArgumentParser(
        "Checksum JSON",
        "This program is a runner to check checksum on database from inputted zip and output a json of the mismatch checksum",
    )
    arg_parser.add_argument(
        "--qdrant-endpoint",
        help="Qdrant Cloud endpoint URI",
        default=os.environ["QDRANT_ENDPOINT"],
    )
    arg_parser.add_argument(
        "--qdrant-api-key",
        help="Qdrant Cloud API Key",
        default=os.environ["QDRANT_API_KEY"],
    )
    arg_parser.add_argument(
        "-i",
        default=default_zip_path,
        help="Path of input zip file",
    )
    arg_parser.add_argument(
        "-o",
        default=default_json_path,
        help="Path of output json file",
    )
    return arg_parser.parse_args()


def parse_arg_api(embedder_dict):
    arg_parser = argparse.ArgumentParser(
        "API Embedding",
        "This program run an HTTP API server to search related vector",
    )
    arg_parser.add_argument(
        "--embedder",
        choices=list(embedder_dict.keys()),
        default=list(embedder_dict.keys())[0],
        help="Embedder model to embed the image",
    )
    return arg_parser.parse_args()


def extract_zip(zip_path: "str", out_path: "str"):
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(out_path)


def get_folder_count_stat(parent_folder_path: "str") -> "typing.Dict[str,str]":
    parent_id_list = os.listdir(parent_folder_path)
    parent_id_stat = {}
    for parent_id in parent_id_list:
        parent_id_path = os.path.join(parent_folder_path, parent_id)
        total = count_files_inside_folder(parent_id_path)
        parent_id_stat[parent_id] = total
    parent_id_stat["total"] = sum(parent_id_stat.values())
    return parent_id_stat


def get_folder_checksum_stat(parent_folder_path: "str") -> "typing.Dict[str,str]":
    parent_id_list = os.listdir(parent_folder_path)
    nums_parent_id = len(parent_id_list)
    parent_id_stat = {}
    q = queue.Queue()

    threads: "typing.List[threading.Thread]" = []

    def add_check_sum(queue: "queue.Queue", path: "str", parent_id: "str"):
        md5_hash = dirhash(path, "md5")
        queue.put((parent_id, md5_hash))

    for parent_id in parent_id_list:
        parent_id_path = os.path.join(parent_folder_path, parent_id)
        t = threading.Thread(target=add_check_sum, args=(q, parent_id_path, parent_id))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    while not q.empty():
        q_val = q.get()
        parent_id_stat[q_val[0]] = q_val[1]

    if len(list(parent_id_stat.keys())) != nums_parent_id:
        raise ValueError("Threads data is corrupt, please try again")

    return parent_id_stat


def list_files(start_path):
    for root, dirs, files in os.walk(start_path):
        level = root.replace(start_path, "").count(os.sep)
        indent = " " * 4 * (level)
        print("{}{}/".format(indent, os.path.basename(root)))
        subindent = " " * 4 * (level + 1)
        for f in files:
            print("{}{}".format(subindent, f))


def count_files_inside_folder(folder_path: "str") -> "int":
    dir_list = os.listdir(folder_path)
    total = 0
    for i in dir_list:
        dir_obj_path = os.path.join(folder_path, i)
        if os.path.isfile(dir_obj_path):
            total += 1
    return total


def batch(iterable: typing.List, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx : min(ndx + n, l)], ndx


def generate_json_checksum(data: typing.Dict[str, str], path: str):
    str_json_data = json.dumps(data)
    with open(path, "w") as outfile:
        outfile.write(str_json_data)


def read_json_checksum(path: str) -> typing.Dict[str, str]:
    f = open(path)
    data = json.load(f)
    f.close()
    return data
