import os
import zipfile
import typing
import threading
import queue
from checksumdir import dirhash


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
        yield iterable[ndx : min(ndx + n, l)]
