import os
import json

def coco_to_yolo_bbox(img_w, img_h, bbox):
    # COCO: [x_min, y_min, width, height]
    x, y, w, h = bbox
    x_center = (x + w / 2) / img_w
    y_center = (y + h / 2) / img_h
    w /= img_w
    h /= img_h
    return x_center, y_center, w, h

def main():
    folder = input("Enter the path to the folder containing 'images' and 'labels': ").strip()
    images_dir = os.path.join(folder, 'images')
    labels_dir = os.path.join(folder, '')
    coco_path = os.path.join(labels_dir, '_annotations.coco.json')
    yolo_labels_dir = os.path.join(folder, 'yolo_labels')
    os.makedirs(yolo_labels_dir, exist_ok=True)

    with open(coco_path, 'r') as f:
        coco = json.load(f)

    # Build image_id to (filename, width, height) mapping
    image_id_map = {img['id']: img for img in coco['images']}
    # Build category_id to class index mapping (YOLO expects 0-based)
    categories = sorted(coco['categories'], key=lambda c: c['id'])
    cat_id_to_idx = {cat['id']: idx for idx, cat in enumerate(categories)}

    # Collect annotations per image
    img_to_anns = {}
    for ann in coco['annotations']:
        img_to_anns.setdefault(ann['image_id'], []).append(ann)

    for img_id, img_info in image_id_map.items():
        img_name = os.path.splitext(img_info['file_name'])[0]
        w, h = img_info['width'], img_info['height']
        anns = img_to_anns.get(img_id, [])
        yolo_lines = []
        for ann in anns:
            class_idx = cat_id_to_idx[ann['category_id']]
            bbox = coco_to_yolo_bbox(w, h, ann['bbox'])
            yolo_lines.append(f"{class_idx} {' '.join(f'{x:.6f}' for x in bbox)}")
        # Write YOLO label file
        yolo_label_path = os.path.join(yolo_labels_dir, img_name + '.txt')
        with open(yolo_label_path, 'w') as f:
            f.write('\n'.join(yolo_lines))

    print(f"YOLO labels saved in: {yolo_labels_dir}")

if __name__ == '__main__':
    main()