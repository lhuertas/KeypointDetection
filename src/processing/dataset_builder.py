import tensorflow as tf
import glob
from src.processing import dataset_functions
from src.configs.storage_config import TRAIN_TFRECORDS

AUTOTUNE = tf.data.experimental.AUTOTUNE


def get_tfrecord_filenames(path: str):

    print("Retrieving TFrecords from:", path)
    tfrecord_files = glob.glob(path + "*")
    tfrecord_files.sort()
    if not tfrecord_files:
      raise ValueError("Couldn't find TFrecord files at:" + path)
    return tfrecord_files


def build_training_ds(tfrecord_filenames: list, labels_placement_function, config) -> tf.data.Dataset:
    """    :param config: default config
    :param labels_placement_function: a model function, which applies the last stage of transformation to the dataset, to distribute the
    various labels correctly according to model outputs
    :param tfrecord_filenames: should be list of correct TFrecord filename, either local or remote (gcs, with gs:// prefix)"""
    # TFrecord files to raw format
    dataset_transformer = dataset_functions.DatasetTransformer(config)
    ds = tf.data.TFRecordDataset(tfrecord_filenames)  # num of reads can be put here, but I don't think I/O is the bottleneck

    # raw format to imgs,tensors(coords kpts)
    ds = ds.map(dataset_transformer.read_tfrecord, num_parallel_calls=AUTOTUNE)

    # cache  ,caching is here before decompressing jpgs and label tensors (should be ~9GB) , (full dataset should be ~90, cache later if RAM available)
    if config.CACHE: ds = ds.cache()
    if config.SHUFFLE: ds = ds.shuffle(config.SHUFFLE_BUFFER)

    ds = ds.map(dataset_transformer.open_image, num_parallel_calls=AUTOTUNE)  # jpeg to array
    ds = ds.map(dataset_transformer.make_label_tensors, num_parallel_calls=AUTOTUNE)  # tensors to label_tensors (46,46,17/38)

    ds = ds.batch(config.BATCH_SIZE)

    # only image augmentation
    if config.IMAGE_AUG: ds = ds.map(dataset_transformer.image_only_augmentation, num_parallel_calls=AUTOTUNE)
    if config.MIRROR_AUG: ds = ds.map(dataset_transformer.mirror_augmentation, num_parallel_calls=AUTOTUNE)

    ds = ds.map(dataset_transformer.apply_mask, num_parallel_calls=AUTOTUNE)
    ds = ds.map(labels_placement_function, num_parallel_calls=AUTOTUNE)  # imgs,label_tensors arrange for model outputs

    ds = ds.repeat()
    if config.PREFETCH: ds = ds.prefetch(config.PREFETCH)
    return ds


def build_validation_ds(tfrecord_filenames: list, labels_placement_function, config) -> tf.data.Dataset:
    """Generate validation dataset from TFrecord file locations
    :param config: effective config dict
    :param labels_placement_function: a model function, which applies the last stage of transformation to the dataset, to distribute the
    various labels correctly according to model outputs
    :param tfrecord_filenames: should be list of correct TFrecord filename, either local or remote (gcs, with gs:// prefix)"""
    # TFrecord files to raw format
    dataset_transformer = dataset_functions.DatasetTransformer(config)

    ds = tf.data.TFRecordDataset(tfrecord_filenames)  # num of reads can be put here, but I don't think I/O is the bottleneck
    # raw format to imgs,tensors(coords kpts)
    ds = ds.map(dataset_transformer.read_tfrecord, num_parallel_calls=AUTOTUNE)

    if config.CACHE: ds = ds.cache()

    ds = ds.map(dataset_transformer.open_image, num_parallel_calls=AUTOTUNE)  # jpeg to array
    ds = ds.map(dataset_transformer.make_label_tensors, num_parallel_calls=AUTOTUNE)  # tensors to label_tensors (46,46,17/38)

    ds = ds.batch(config.BATCH_SIZE)

    ds = ds.map(dataset_transformer.apply_mask, num_parallel_calls=AUTOTUNE)
    ds = ds.map(labels_placement_function, num_parallel_calls=AUTOTUNE)  # imgs,label_tensors arrange for model outputs

    if config.PREFETCH: ds = ds.prefetch(config.PREFETCH)
    return ds

if __name__ == "__main__":
    from modelling.model import ModelDatasetComponent
    import configs.default_config as config
    train_tfrecords = get_tfrecord_filenames(TRAIN_TFRECORDS)
    model = ModelDatasetComponent(config)
    ds = build_training_ds(train_tfrecords, model.place_training_labels, config)
