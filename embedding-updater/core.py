import os
import typing


def smart_update(dist_dir: str) -> "typing.List[str]":
    """
    Return a list of parent_id that needs to be updated from dist folders.
    Dist folders should have a structure like this:
        `dist / (parent_id) / (icon_id).jpg`
    """
    assert os.path.isdir(dist_dir)
    dist_objs = os.listdir(dist_dir)
    parent_id_folders = []
    # Get Parent IDs Folder
    for dist_obj in dist_objs:
        dist_obj_path = os.path.join(dist_dir, dist_obj)
        if os.path.isdir(dist_obj_path):
            parent_id_folders.append(dist_obj)

    # TODO: Implement smart update
    return parent_id_folders
