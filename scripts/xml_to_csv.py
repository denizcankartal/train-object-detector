import os
import glob
import pandas as pd
import xml.etree.ElementTree as et
from argparse import ArgumentParser
import sys

## Example xml file structure, single object in an image!
'''
<annotation>
    <folder>drone-images</folder>
    <filename>drone-10.jpg</filename>
    <path>/home/username/thesis/ubuntu-tensorflow-opencv-selenium/training/images/drone-images/drone-10.jpg</path>
    <source>
        <database>Unknown</database>
    </source>
    <size>
        <width>225</width>
        <height>225</height>
        <depth>3</depth>
    </size>
    <segmented>0</segmented>
    <object>
        <name>drone</name>
        <pose>Unspecified</pose>
        <truncated>1</truncated>
        <difficult>0</difficult>
        <bndbox>
            <xmin>1</xmin>
            <ymin>59</ymin>
            <xmax>225</xmax>
            <ymax>155</ymax>
        </bndbox>
    </object>
</annotation>
'''

def xml_to_df(xml_path):
    l = []

    # get all the xml files inside of that path
    xml_files = sorted(glob.glob(xml_path + "/*.xml"))

    # go through each xml file
    for xml_file in xml_files:
        tree = et.parse(xml_file)
        root = tree.getroot()

        # get filename of that xml file
        filename = root.find("filename").text

        # get width and height of the xml file(image width and height)
        width = int(root.find("size").find("width").text)
        height = int(root.find("size").find("height").text)

        # find all the objects in that xml file
        # aka all the detected objects in the image
        objects = root.findall("object")

        # go through each detected object inside that image
        for obj in objects:
            # bounding box of one of the detected objects in that image
            bounding_box = obj.find("bndbox")
            # bounding box coordinates
            [xmin, ymin, xmax, ymax] = [int(coord.text) for coord in bounding_box]
            # object's name, aka label, class
            obj_class = obj.find("name").text

            value = [
                filename,
                width,
                height,
                obj_class,
                xmin,
                ymin,
                xmax,
                ymax
            ]

            # put that object in the list
            l.append(value)
        
        # create columns for the dataframe
        column_names = [
            "filename",
            "width",
            "height",
            "class",
            "xmin",
            "ymin",
            "xmax",
            "ymax"
        ]

        # use the list to create the dataframe
        df = pd.DataFrame(l, columns=column_names)
    
    return df

def is_path_existed(path):
    if not os.path.exists(path):
        sys.exit("{} is not existing, Exiting the program!".format(path))

def main():
    parser = ArgumentParser()
    
    parser.add_argument("-p", "--path", required=True, help="Path to xml files.")
    parser.add_argument("-o", "--output", required=True, help="Path to output the csv file.")
    
    args = vars(parser.parse_args())

    # check if paths are existing!

    # create dataframe
    df = xml_to_df(args["path"])

    print("Dataframe: ")
    print(df)
    # output csv file
    df.to_csv(args["output"], index=None)
    print("Converted {} xml files to a csv".format(len(df)))

if __name__ == "__main__":
    main()