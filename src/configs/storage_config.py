import os

STORAGE_LOCAL = False  # look for images through http address
# Definitions for COCO 2017 dataset
DATASET_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) + "/data"
IMAGES_PATH = DATASET_PATH + "/val2017/"
TRAIN_ANNS = DATASET_PATH + "/annotations/person_keypoints_train2017.json"
TRAIN_FOOT_ANNS = DATASET_PATH + "/annotations/person_keypoints_train2017_foot_v1.json"
VALID_ANNS = DATASET_PATH + "/annotations/person_keypoints_val2017.json"
VALID_FOOT_ANNS = DATASET_PATH + "/annotations/person_keypoints_val2017_foot_v1.json"

# will be used as output files
ROOT_TFRECORDS_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) + "/data/TFrecords"
TRAIN_TFRECORDS = ROOT_TFRECORDS_PATH + "/training/"
VALID_TFRECORDS = ROOT_TFRECORDS_PATH + "/validation/"

RESULTS_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__))) + "/data/tmp"
TENSORBOARD_PATH = RESULTS_ROOT + "/tensorboard/"
CHECKPOINTS_PATH = RESULTS_ROOT + "/checkpoints/"
MODELS_PATH = RESULTS_ROOT + "/models/"