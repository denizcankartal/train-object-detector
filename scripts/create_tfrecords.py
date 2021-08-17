import os
import io
import pandas as pd
from argparse import ArgumentParser
import tensorflow.compat.v1 as tf
from PIL import Image
from object_detection.utils import dataset_util, label_map_util
from collections import namedtuple

# reference -> https://tensorflow-object-detection-api-tutorial.readthedocs.io/en/latest/training.html#create-label-map

def split(df, group):
    data = namedtuple("data", ["filename", "object"])
    gb = df.groupby(group)
    return [data(filename, gb.get_group(x)) for filename, x in zip(gb.groups.keys(), gb.groups)]

def class_text_to_int(label_map_dict, row_label):
    return label_map_dict[row_label]


def create_tf_example(group, path, label_map_dict):
    with tf.gfile.GFile(os.path.join(path, '{}'.format(group.filename)), 'rb') as fid:
        encoded_jpg = fid.read()
    
    encoded_jpg_io = io.BytesIO(encoded_jpg)
    image = Image.open(encoded_jpg_io)
    width, height = image.size

    filename = group.filename.encode('utf8')
    image_format = b'jpg'
    xmins = []
    xmaxs = []
    ymins = []
    ymaxs = []
    classes_text = []
    classes = []

    for index, row in group.object.iterrows():
        xmins.append(row['xmin'] / width)
        xmaxs.append(row['xmax'] / width)
        ymins.append(row['ymin'] / height)
        ymaxs.append(row['ymax'] / height)
        classes_text.append(row['class'].encode('utf8'))
        classes.append(class_text_to_int(label_map_dict, row['class']))

    tf_example = tf.train.Example(features=tf.train.Features(feature={
        'image/height': dataset_util.int64_feature(height),
        'image/width': dataset_util.int64_feature(width),
        'image/filename': dataset_util.bytes_feature(filename),
        'image/source_id': dataset_util.bytes_feature(filename),
        'image/encoded': dataset_util.bytes_feature(encoded_jpg),
        'image/format': dataset_util.bytes_feature(image_format),
        'image/object/bbox/xmin': dataset_util.float_list_feature(xmins),
        'image/object/bbox/xmax': dataset_util.float_list_feature(xmaxs),
        'image/object/bbox/ymin': dataset_util.float_list_feature(ymins),
        'image/object/bbox/ymax': dataset_util.float_list_feature(ymaxs),
        'image/object/class/text': dataset_util.bytes_list_feature(classes_text),
        'image/object/class/label': dataset_util.int64_list_feature(classes),
    }))
    return tf_example

def main():
    parser = ArgumentParser()

    parser.add_argument("-l", "--labels_path", required=True, help="Path to the labels (.pbtxt) file.", type=str)
    parser.add_argument("-o", "--output", required=True, help="Path to output the TFrecord file, e.g. train.record", type=str)
    parser.add_argument("-i", "--images_path", required=True, help="path to the images directory")
    parser.add_argument("-c", "--csv_path", required=True, help="path to the csv file")
    
    args = vars(parser.parse_args())

    label_map = label_map_util.load_labelmap(args["labels_path"])
    label_map_dict = label_map_util.get_label_map_dict(label_map)
    
    writer = tf.python_io.TFRecordWriter(args["output"])
    path = os.path.join(args["images_path"])
    examples = pd.read_csv(args["csv_path"])
    grouped = split(examples, 'filename')

    for group in grouped:
        tf_example = create_tf_example(group, path, label_map_dict)
        writer.write(tf_example.SerializeToString())
    
    writer.close()
    print('Successfully created the TFRecords: {}'.format(args["output"]))

if __name__ == "__main__":
    main()