import os


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
