import json
from src.configs.storage_config import TRAIN_FOOT_ANNS, TRAIN_ANNS


def join_annotations_files(keypoint_annotations_file1, keypoint_annotations_file2):
    """
    Join annotations from two files into one.
    :param keypoint_annotations_file1: main annotation file
    :param keypoint_annotations_file2: additional annotations
    :return: json with the total keypoint annotations
    """

    main_dataset = json.load(open(keypoint_annotations_file1, 'r'))
    main_anns = main_dataset['annotations']
    ids = [ann['id'] for ann in main_anns]

    # additional anotations
    add_dataset = json.load(open(keypoint_annotations_file2, 'r'))
    add_anns = add_dataset['annotations']

    for id in ids:
        add_keypoint = [ann['keypoints'] for ann in add_anns if ann["id"]==id]
        main_keypoint = [ann["keypoints"] for ann in main_anns if ann["id"]==id]
        new_keypoints = add_keypoint[0] + main_keypoint[0]
        current_ann = [ann for ann in main_anns if ann["id"]==id]
        current_ann[0]["keypoints"] = new_keypoints


if __name__ == '__main__':
    join_annotations_files(TRAIN_FOOT_ANNS, TRAIN_ANNS)