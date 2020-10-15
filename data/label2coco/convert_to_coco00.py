
import os
import json

import argparse
import datetime
from pprint import pprint

# CLASSES = ('traffic3', 'traffic4', 'traffic3-back', 'traffic4-back', 'circle', 'circle-back')
# traffic3_CLASSES = ('traffic3', 'traffic3-occ-partially', 'traffic3rev', 'traffic3rev-occ-partially')
# traffic4_CLASSES = ('traffic4', 'traffic4-occ-partially', 'traffic4y', 'traffic4y-occ-partially')
# dets_CLASSES = CLASSES + traffic3_CLASSES + traffic4_CLASSES


CLASSES = ('RedLeft', 'Red')
traffic3_CLASSES = ('traffic3', 'traffic3-occ-partially', 'traffic3rev', 'traffic3rev-occ-partially')
traffic4_CLASSES = ('traffic4', 'traffic4-occ-partially', 'traffic4y', 'traffic4y-occ-partially')
dets_CLASSES = CLASSES + traffic3_CLASSES + traffic4_CLASSES

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--json_dir', type=str, default='./test_data/Annotations')
    parser.add_argument('--txt_path', type=str, default='./test_data/Annotations/image.txt')
    parser.add_argument('--output_json', type=str, default='./test_data/Annotations/sxp_train_val_2000.json')

    args = parser.parse_args()
    return args


def sort_coordinate(point_xy, is_traffic3r=False, is_traffic4y=False):
    assert len(point_xy) == 6 or len(point_xy) == 8
    x = point_xy[::2]
    y = point_xy[1::2]
    s_x = sorted(range(len(x)), key=x.__getitem__)
    s_y = sorted(range(len(y)), key=y.__getitem__)
    if len(point_xy) == 6:
        x1, y1 = x[s_y[0]], y[s_y[0]]
        x3, y3 = x[s_y[1]], y[s_y[1]]
        x4, y4 = x[s_y[2]], y[s_y[2]]
        if is_traffic3r:
            if x1 > x3:
                tmp_x, tmp_y = x1, y1
                x1, y1 = x3, y3
                x3, y3 = tmp_x, tmp_y
            return [x1 - 0.5, y1 - 0.5, 2,
                    x3 - 0.5, y3 - 0.5, 2,
                    0, 0, 0,
                    x4 - 0.5, y4 - 0.5, 2]
        else:
            if x4 > x3:
                tmp_x, tmp_y = x4, y4
                x4, y4 = x3, y3
                x3, y3 = tmp_x, tmp_y
            return [x1 - 0.5, y1 - 0.5, 2,
                    0, 0, 0,
                    x3 - 0.5, y3 - 0.5, 2,
                    x4 - 0.5, y4 - 0.5, 2]
    else:
        if is_traffic4y:
            return [x[s_y[0]] - 0.5, y[s_y[0]] - 0.5, 2,
                    x[s_x[3]] - 0.5, y[s_x[3]] - 0.5, 2,
                    x[s_y[3]] - 0.5, y[s_y[3]] - 0.5, 2,
                    x[s_x[0]] - 0.5, y[s_x[0]] - 0.5, 2]
        else:
            x1, y1 = x[s_y[0]], y[s_y[0]]
            x2, y2 = x[s_y[1]], y[s_y[1]]
            x3, y3 = x[s_y[2]], y[s_y[2]]
            x4, y4 = x[s_y[3]], y[s_y[3]]
            if x1 > x2:
                tmp_x, tmp_y = x1, y1
                x1, y1 = x2, y2
                x2, y2 = tmp_x, tmp_y
            if x4 > x3:
                tmp_x, tmp_y = x3, y3
                x3, y3 = x4, y4
                x4, y4 = tmp_x, tmp_y
            return [x1 - 0.5, y1 - 0.5, 2,
                    x2 - 0.5, y2 - 0.5, 2,
                    x3 - 0.5, y3 - 0.5, 2,
                    x4 - 0.5, y4 - 0.5, 2]


def convert_to_coco_dict(json_dir, txt_path):

    categories = [
        {"id": id+1, "name": name}
        for id, name in enumerate(CLASSES)
    ] # categories-->[{'name': 'RedLeft', 'id': 1}, {'name': 'Red', 'id': 2}]


    cat2label = {cat: i + 1 for i, cat in enumerate(CLASSES)} # cat2label-->{'RedLeft': 1, 'Red': 2}

    coco_images = []
    coco_annotations = []

    #json_ids = [d.name for d in os.scandir(json_dir)]
    with open(txt_path, 'r') as f:
        json_ids = f.readlines()
    json_ids = [(x.strip('\n'))[:-4]+'.json' for x in json_ids] # -->['1597149103.066496.json', '1597149103.254008.json']

    
    for json_id, json_name in enumerate(json_ids):
        print(json_id, json_name)
        json_path = os.path.join(json_dir, json_name)
        with open(json_path, 'r') as f:
            data = json.load(f)
            coco_image = {
                'id': json_id,
                'width': data['imageWidth'],
                'height': data['imageHeight'],
                'file_name': json_name[:-4]+'jpg'
            }
            coco_images.append(coco_image)

            anns_per_image = data['shapes']
            for annotation in anns_per_image:
                label = annotation['label']
                if label in dets_CLASSES:
                    # compute label id 
                    if label in traffic3_CLASSES:
                        label_id = cat2label['traffic3']
                    elif label in traffic4_CLASSES:
                        label_id = cat2label['traffic4']
                    else:
                        label_id = cat2label[label]


                    # create a new dict with only COCO fields
                    coco_annotation = {}
                    
                    # COCO requirement: XYWH box format
                    sub = [float(v) for points in annotation['points'] for v in points]
                    if annotation['shape_type'] == 'polygon':
                        bbox = [
                            int(min(sub[::2])),
                            int(min(sub[1::2])),
                            int(max(sub[::2])),
                            int(max(sub[1::2]))
                        ]
                        bbox_w = bbox[2] - bbox[0]
                        bbox_h = bbox[3] - bbox[1]
                        bbox = [bbox[0], bbox[1], bbox_w, bbox_h]
                        mask_polys = [sub]
                    else:
                        bbox = [
                            int(sub[0]),
                            int(sub[1]),
                            int(sub[2]),
                            int(sub[3])
                        ]
                        bbox_w = bbox[2] - bbox[0]
                        bbox_h = bbox[3] - bbox[1]
                        bbox = [bbox[0], bbox[1], bbox_w, bbox_h]
                        mask_polys = [[bbox[0], bbox[1], bbox[0]+bbox_w, bbox[1],
                                      bbox[2], bbox[3], bbox[0], bbox[3]+bbox_h]]

                    # if label in ['traffic3-back', 'traffic3', 'traffic3-occ-partially']:
                    #     assert len(mask_polys[0]) == 6
                    #     # keypoints = sort_coordinate(mask_polys[0])
                    # elif label in ['traffic3rev', 'traffic3rev-occ-partially']:
                    #     assert len(mask_polys[0]) == 6
                    #     # keypoints = sort_coordinate(mask_polys[0], is_traffic3r=True)
                    # elif label in ['traffic4', 'traffic4-occ-partially', 'traffic4-back']:
                    #     if len(mask_polys[0]) == 8:
                    #         assert len(mask_polys[0]) == 8
                    #         # keypoints = sort_coordinate(mask_polys[0])
                    #     else:
                    #         print('---------------------------------------------------',len(mask_polys[0]))
                    # elif label in ['traffic4y', 'traffic4y-occ-partially']:
                    #     assert len(mask_polys[0]) == 8
                    #     # keypoints = sort_coordinate(mask_polys[0], is_traffic3r=False, is_traffic4y=True)
                    # elif label in ['circle', 'circle-back']:
                    #     assert len(mask_polys[0]) == 8
                    #     keypoints = [mask_polys[0][0] - 0.5, mask_polys[0][1] - 0.5, 2,
                    #                  mask_polys[0][2] - 0.5, mask_polys[0][3] - 0.5, 2,
                    #                  mask_polys[0][4] - 0.5, mask_polys[0][5] - 0.5, 2,
                    #                  mask_polys[0][6] - 0.5, mask_polys[0][7] - 0.5, 2]
                    # else:
                    #     raise ValueError("The label isn't in detection directory")

                    num_keypoints = 4

                    # COCO requirement:
                    #   linking annotations to images
                    #   "id" field must start with 1
                    coco_annotation['id'] = len(coco_annotations) + 1
                    coco_annotation['image_id'] = coco_image['id']
                    coco_annotation['bbox'] = bbox
                    coco_annotation['area'] = bbox[2] * bbox[3]
                    coco_annotation['category_id'] = label_id
                    coco_annotation['iscrowd'] = 0
                    coco_annotation['segmentation'] = mask_polys
                    # coco_annotation['keypoints'] = keypoints
                    # coco_annotation['num_keypoints'] = num_keypoints
                    coco_annotations.append(coco_annotation)
        
    info = {
        "data_created": str(datetime.datetime.now()),
        "description": "Automatically generated TW traffic sign json file for COCO."
    }
    coco_dict = {
        'info': info,
        'images': coco_images,
        'annotations': coco_annotations,
        'categories': categories,
        'license': None,
    }

    return coco_dict


def main():
    args = parse_args()
    coco_dict = convert_to_coco_dict(args.json_dir, args.txt_path)
    with open(args.output_json, 'w') as f:
        json.dump(coco_dict, f) 


if __name__ == '__main__':
    main()
