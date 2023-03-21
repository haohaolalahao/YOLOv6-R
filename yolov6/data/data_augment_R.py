#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# This code is based on
# https://github.com/ultralytics/yolov5/blob/master/utils/dataloaders.py

import math
import random

import cv2
import numpy as np
import torch
from mmcv.ops import box_iou_rotated




def RFlipVertical(img: np.ndarray, bboxes: np.ndarray):
    """
    # NOTE old [xmin, ymin xmax, ymax, x_center, y_center, w, h, class_id, or class_id_2 angle]
    # NOTE i   [ 0     1    2      3     4        5        6  7     8                     9or-1]
    # NOTE new [class_id, x_center, y_center, longSide, shortSide, angle]
    # NOTE i   [    0         1         2     3             4        5  ]
    # NOTE cv2: HWC
    """
    h = img.shape[0]
    img = img[::-1, :, :]
    bboxes[:, 2] = h - bboxes[:, 2]
    # * angle = 180 - angle
    bboxes[:, -1] = 180 - bboxes[:, -1]
    # * angle 180° 无定义 转到 0°
    bboxes[bboxes[:, -1] == 180, -1] = 0

    return img, bboxes


def RFlipHorizontal(img, bboxes):
    """
    # NOTE old [xmin, ymin xmax, ymax, x_center, y_center, w, h, class_id, or class_id_2 angle]
    # NOTE i   [ 0     1    2      3     4        5        6  7     8                     9or-1]
    # NOTE new [class_id, x_center, y_center, longSide, shortSide, angle]
    # NOTE i   [    0         1         2     3             4        5  ]
    # NOTE cv2: HWC
    """
    w = img.shape[1]
    img = img[:, ::-1, :]
    # * x' = w - x; y' = y
    bboxes[:, 1] = w - bboxes[:, 1]
    # * angle = 180 - angle
    bboxes[:, -1] = 180 - bboxes[:, -1]
    # * angle 180° 无定义 转到 0°
    bboxes[bboxes[:, -1] == 180, -1] = 0
    return img, bboxes


def RRotate(img, bboxes):
    # NOTE new [xmin, ymin xmax, ymax, x_center, y_center, w, h, class_id, or class_id_2 angle]
    # NOTE i   [ 0     1    2      3     4        5        6  7     8                     9or-1]
    # NOTE new [class_id, x_center, y_center, longSide, shortSide, angle]
    # NOTE i   [    0         1         2     3             4        5  ]
    # NOTE cv2: HWC
    # NOTE 0°， 90°， 180°， 270°
    degree = 90
    pn = np.random.randint(low=0, high=4, size=None, dtype="l")
    # pn = 3
    h, w = img.shape[:2]
    M = np.eye(3)
    M[:2] = cv2.getRotationMatrix2D(angle=degree * pn, center=(w / 2, h / 2), scale=1.0)

    img = cv2.warpAffine(img, M[:2], dsize=(w, h), borderValue=(128, 128, 128))

    # Transform label coordinates
    n = len(bboxes)
    # warp points
    xy = np.ones((n, 3))

    # x_center y_center
    xy[:, :2] = bboxes[:, [1, 2]].reshape(n, 2)
    xy = xy @ M.T  # transform
    xy = xy[:, :2].reshape(n, 2)

    # create new boxes
    x = xy[:, 0:1].clip(0, w)
    y = xy[:, 1:2].clip(0, h)

    bboxes[:, 1] = x[:, -1]
    bboxes[:, 2] = y[:, -1]
    # if pn == 0:
    #     bboxes[:, [5, 7, 9, 11]] = x
    #     bboxes[:, [6, 8, 10, 12]] = y
    # elif pn == 1:
    #     bboxes[:, [11, 5, 7, 9]] = x
    #     bboxes[:, [12, 6, 8, 10]] = y
    # elif pn == 2:
    #     bboxes[:, [9, 11, 5, 7]] = x
    #     bboxes[:, [10, 12, 6, 8]] = y
    # elif pn == 3:
    #     bboxes[:, [7, 9, 11, 5]] = x
    #     bboxes[:, [8, 10, 12, 6]] = y

    bboxes[:, -1] = bboxes[:, -1] + pn * 90

    bboxes[:, -1] = np.where(bboxes[:, -1] > 180, bboxes[:, -1] - 180, bboxes[:, -1])
    bboxes[:, -1] = np.where(bboxes[:, -1] > 180, bboxes[:, -1] - 180, bboxes[:, -1])

    # * angle 180° 无定义 转到 0°
    bboxes[bboxes[:, -1] == 180, -1] = 0

    # xy4 = np.concatenate((x.min(1), y.min(1), x.max(1), y.max(1))).reshape(4, n).T
    # bboxes[:, [0, 1, 2, 3]] = xy4

    # for anno in bboxes:
    #     points = np.array(
    #         [[int(anno[5]), int(anno[6])], [int(anno[7]), int(anno[8])], [int(anno[9]), int(anno[10])],
    #          [int(anno[11]), int(anno[12])]])
    #     cv2.polylines(new_img, [points], 1, (0, 128, 255), 2)
    # import matplotlib.pyplot as plt
    # plt.figure("Image_Rot")  # 图像窗口名称
    # plt.imshow(new_img / 255, cmap='jet')
    # plt.show()
    return img, bboxes


def augment_hsv(im, hgain=0.5, sgain=0.5, vgain=0.5):
    """HSV color-space augmentation."""
    if hgain or sgain or vgain:
        r = np.random.uniform(-1, 1, 3) * [hgain, sgain, vgain] + 1  # random gains
        hue, sat, val = cv2.split(cv2.cvtColor(im, cv2.COLOR_BGR2HSV))
        dtype = im.dtype  # uint8

        x = np.arange(0, 256, dtype=r.dtype)
        lut_hue = ((x * r[0]) % 180).astype(dtype)
        lut_sat = np.clip(x * r[1], 0, 255).astype(dtype)
        lut_val = np.clip(x * r[2], 0, 255).astype(dtype)

        im_hsv = cv2.merge((cv2.LUT(hue, lut_hue), cv2.LUT(sat, lut_sat), cv2.LUT(val, lut_val)))
        cv2.cvtColor(im_hsv, cv2.COLOR_HSV2BGR, dst=im)  # no return needed


def letterbox(im, new_shape=(640, 640), color=(114, 114, 114), auto=True, scaleup=True, stride=32, return_int=False):
    """Resize and pad image while meeting stride-multiple constraints."""
    shape = im.shape[:2]  # current shape [height, width]
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)
    elif isinstance(new_shape, list) and len(new_shape) == 1:
        new_shape = (new_shape[0], new_shape[0])

    # Scale ratio (new / old)
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    if not scaleup:  # only scale down, do not scale up (for better val mAP)
        r = min(r, 1.0)

    # Compute padding
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding

    if auto:  # minimum rectangle
        dw, dh = np.mod(dw, stride), np.mod(dh, stride)  # wh padding

    dw /= 2  # divide padding into 2 sides
    dh /= 2

    if shape[::-1] != new_unpad:  # resize
        im = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    im = cv2.copyMakeBorder(im, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
    if not return_int:
        return im, r, (dw, dh)
    else:
        return im, r, (left, top)


def mixup(im, labels, im2, labels2):
    """Applies MixUp augmentation https://arxiv.org/pdf/1710.09412.pdf."""
    r = np.random.beta(32.0, 32.0)  # mixup ratio, alpha=beta=32.0
    im = (im * r + im2 * (1 - r)).astype(np.uint8)
    labels = np.concatenate((labels, labels2), 0)
    return im, labels


def box_candidates(box1, box2, wh_thr=2, ar_thr=20, area_thr=0.1, eps=1e-16):  # box1(4,n), box2(4,n)
    """Compute candidate boxes: box1 before augment, box2 after augment, wh_thr (pixels), aspect_ratio_thr, area_ratio."""
    w1, h1 = box1[2] - box1[0], box1[3] - box1[1]
    w2, h2 = box2[2] - box2[0], box2[3] - box2[1]
    ar = np.maximum(w2 / (h2 + eps), h2 / (w2 + eps))  # aspect ratio
    return (w2 > wh_thr) & (h2 > wh_thr) & (w2 * h2 / (w1 * h1 + eps) > area_thr) & (ar < ar_thr)  # candidates


def random_affine(img, labels=(), degrees=10, translate=0.1, scale=0.1, shear=10, new_shape=(640, 640)):
    """Applies Random affine transformation."""
    n = len(labels)
    height, width = new_shape

    M, s = get_transform_matrix(img.shape[:2], (height, width), degrees, scale, shear, translate)
    if (M != np.eye(3)).any():  # image changed
        img = cv2.warpAffine(img, M[:2], dsize=(width, height), borderValue=(114, 114, 114))

    # Transform label coordinates
    if n:
        new = np.zeros((n, 4))

        xy = np.ones((n * 4, 3))
        xy[:, :2] = labels[:, [1, 2, 3, 4, 1, 4, 3, 2]].reshape(n * 4, 2)  # x1y1, x2y2, x1y2, x2y1
        xy = xy @ M.T  # transform
        xy = xy[:, :2].reshape(n, 8)  # perspective rescale or affine

        # create new boxes
        x = xy[:, [0, 2, 4, 6]]
        y = xy[:, [1, 3, 5, 7]]
        new = np.concatenate((x.min(1), y.min(1), x.max(1), y.max(1))).reshape(4, n).T

        # clip
        new[:, [0, 2]] = new[:, [0, 2]].clip(0, width)
        new[:, [1, 3]] = new[:, [1, 3]].clip(0, height)

        # filter candidates
        i = box_candidates(box1=labels[:, 1:5].T * s, box2=new.T, area_thr=0.1)
        labels = labels[i]
        labels[:, 1:5] = new[i]

    return img, labels


# TODO Random Flip Function
def RRandomFlip(img, bboxes, flip_ratio = 0.25, direction="horizon", version="oc"):
    """
    Flip an image horizontally or vertically.
    Args:
        img (ndarray): Image to be flipped.
        direction (str): The flip direction, either "horizontal" or
            "vertical" or "diagonal".
    Returns:
        ndarray: The flipped image.
    """
    assert bboxes.shape[-1] % 5 == 0
    orig_shape = bboxes.shape
    bboxes = bboxes.reshape((-1, 5))
    flipped = bboxes.copy()
    img_shape = img
    if direction == 'horizontal':
        flipped[:, 0] = img_shape[1] - bboxes[:, 0] - 1
        flip_img = np.flip(img, axis=1)
    elif direction == 'vertical':
        flipped[:, 1] = img_shape[0] - bboxes[:, 1] - 1
        flip_img = np.flip(img, axis=0)
    elif direction == 'diagonal':
        flipped[:, 0] = img_shape[1] - bboxes[:, 0] - 1
        flipped[:, 1] = img_shape[0] - bboxes[:, 1] - 1
        flip_img = np.flip(img, axis=(0, 1))
        return flip_img, flipped.reshape(orig_shape)
    else:
        raise ValueError(f'Invalid flipping direction "{direction}"')
    if version == 'oc':
        rotated_flag = (bboxes[:, 4] != np.pi / 2)
        flipped[rotated_flag, 4] = np.pi / 2 - bboxes[rotated_flag, 4]
        flipped[rotated_flag, 2] = bboxes[rotated_flag, 3]
        flipped[rotated_flag, 3] = bboxes[rotated_flag, 2]
    else:
        flipped[:, 4] = norm_angle(np.pi - bboxes[:, 4], self.version)
    return flip_img, flipped.reshape(orig_shape)

#TODO RESIZE Augmentation
# def RResize(img, bboxes, keep_ratio=True, ratio_range=None, img_scale = None)


def mosaic_augmentation(img_size, imgs, hs, ws, labels, hyp):
    """Applies Mosaic augmentation."""
    assert len(imgs) == 4, "Mosaic augmentation of current version only supports 4 images."

    labels4 = []
    s = img_size
    yc, xc = (int(random.uniform(s // 2, 3 * s // 2)) for _ in range(2))  # mosaic center x, y
    for i in range(len(imgs)):
        # Load image
        img, h, w = imgs[i], hs[i], ws[i]
        # place img in img4
        if i == 0:  # top left
            img4 = np.full((s * 2, s * 2, img.shape[2]), 114, dtype=np.uint8)  # base image with 4 tiles
            x1a, y1a, x2a, y2a = max(xc - w, 0), max(yc - h, 0), xc, yc  # xmin, ymin, xmax, ymax (large image)
            x1b, y1b, x2b, y2b = w - (x2a - x1a), h - (y2a - y1a), w, h  # xmin, ymin, xmax, ymax (small image)
        elif i == 1:  # top right
            x1a, y1a, x2a, y2a = xc, max(yc - h, 0), min(xc + w, s * 2), yc
            x1b, y1b, x2b, y2b = 0, h - (y2a - y1a), min(w, x2a - x1a), h
        elif i == 2:  # bottom left
            x1a, y1a, x2a, y2a = max(xc - w, 0), yc, xc, min(s * 2, yc + h)
            x1b, y1b, x2b, y2b = w - (x2a - x1a), 0, w, min(y2a - y1a, h)
        elif i == 3:  # bottom right
            x1a, y1a, x2a, y2a = xc, yc, min(xc + w, s * 2), min(s * 2, yc + h)
            x1b, y1b, x2b, y2b = 0, 0, min(w, x2a - x1a), min(y2a - y1a, h)

#NOTE RandomCrop
def RRandomCrop(img, bboxes, labels, crop_size, allow_negative_crop = False, bbox_clip_border=True, iof_thr=0.7, version='oc'):

    assert crop_size[0] > 0 and crop_size[1] > 0
    margin_h = max(img.shape[0] - crop_size[0], 0)
    margin_w = max(img.shape[1] - crop_size[1], 0)
    offset_h = np.random.randint(0, margin_h + 1)
    offset_w = np.random.randint(0, margin_w + 1)
    crop_y1, crop_y2 = offset_h, offset_h + crop_size[0]
    crop_x1, crop_x2 = offset_w, offset_w + crop_size[1]
    img = img[crop_y1:crop_y2, crop_x1:crop_x2, ...]
    img_shape = img.shape
    height, width, _ = img_shape
    bbox_offset = np.array([offset_w, offset_h, 0, 0, 0],
                                   dtype=np.float32)
    bboxes = bboxes - bbox_offset

    windows = np.array([width / 2, height / 2, width, height, 0],
                               dtype=np.float32).reshape(-1, 5)

    valid_inds = box_iou_rotated(
                torch.tensor(bboxes), torch.tensor(windows),
                mode='iof').numpy().squeeze() > iof_thr
    if (not valid_inds.any() and not allow_negative_crop):
        return None,None,None
    rboxes = bboxes[valid_inds,:]
    rlabels = labels[valid_inds]

    return img, rboxes, rlabels

    # Concat/clip labels
    labels4 = np.concatenate(labels4, 0)
    for x in labels4[:, 1:]:
        np.clip(x, 0, 2 * s, out=x)

    # Augment
    img4, labels4 = random_affine(
        img4,
        labels4,
        degrees=hyp["degrees"],
        translate=hyp["translate"],
        scale=hyp["scale"],
        shear=hyp["shear"],
        new_shape=(img_size, img_size),
    )

    return img4, labels4


def mosaic_augmentation_obb(img_size, imgs, hs, ws, labels, hyp):
    """Applies Mosaic augmentation."""
    assert len(imgs) == 4, "Mosaic augmentation of current version only supports 4 images."

    labels4 = []
    s = img_size
    yc, xc = (int(random.uniform(s // 2, 3 * s // 2)) for _ in range(2))  # mosaic center x, y
    for i in range(len(imgs)):
        # Load image
        img, h, w = imgs[i], hs[i], ws[i]
        # place img in img4
        if i == 0:  # top left
            img4 = np.full((s * 2, s * 2, img.shape[2]), 114, dtype=np.uint8)  # base image with 4 tiles
            x1a, y1a, x2a, y2a = max(xc - w, 0), max(yc - h, 0), xc, yc  # xmin, ymin, xmax, ymax (large image)
            x1b, y1b, x2b, y2b = w - (x2a - x1a), h - (y2a - y1a), w, h  # xmin, ymin, xmax, ymax (small image)
        elif i == 1:  # top right
            x1a, y1a, x2a, y2a = xc, max(yc - h, 0), min(xc + w, s * 2), yc
            x1b, y1b, x2b, y2b = 0, h - (y2a - y1a), min(w, x2a - x1a), h
        elif i == 2:  # bottom left
            x1a, y1a, x2a, y2a = max(xc - w, 0), yc, xc, min(s * 2, yc + h)
            x1b, y1b, x2b, y2b = w - (x2a - x1a), 0, w, min(y2a - y1a, h)
        elif i == 3:  # bottom right
            x1a, y1a, x2a, y2a = xc, yc, min(xc + w, s * 2), min(s * 2, yc + h)
            x1b, y1b, x2b, y2b = 0, 0, min(w, x2a - x1a), min(y2a - y1a, h)

        img4[y1a:y2a, x1a:x2a] = img[y1b:y2b, x1b:x2b]  # img4[ymin:ymax, xmin:xmax]
        padw = x1a - x1b
        padh = y1a - y1b

        # Labels
        labels_per_img = labels[i].copy()
        if labels_per_img.size:
            # NOTE 输出全部转变为真实值, [x, y, w, h, angle]
            # x [padw, padw + w]
            # y [padh, padh + h]
            boxes = np.copy(labels_per_img[:, 1:])
            boxes[:, 0] = w * boxes[:, 0] + padw  # center x
            boxes[:, 1] = h * boxes[:, 1] + padh  # center y
            boxes[:, 2] = w * boxes[:, 2]  # longSide / w
            boxes[:, 3] = h * boxes[:, 3]  # shortSide / h
            # NOTE filter
            valid_inds = filter_box_candidates(boxes, x1a, x2a, y1a, y2a, min_bbox_size=4)
            labels_per_img[:, 1:] = boxes
            labels_per_img = labels_per_img[valid_inds]

        labels4.append(labels_per_img)

    # Concat/clip labels
    labels4 = np.concatenate(labels4, 0)

    # NOTE 不做affine,一个是label不好调整, 另一个参考mmyolo的RTM, affine会造成影响
    # NOTE img5, labels4 需要重新resize
    # img4, labels4 = random_affine(img4, labels4,
    #                               degrees=hyp['degrees'],
    #                               translate=hyp['translate'],
    #                               scale=hyp['scale'],
    #                               shear=hyp['shear'],
    #                               new_shape=(img_size, img_size))

    img4 = cv2.resize(img4, (img_size, img_size))
    labels4[:, 1:5] /= 2.0

    return img4, labels4


def filter_box_candidates(bboxes, w_min, w_max, h_min, h_max, min_bbox_size=4, ratio=0.25):
    """Filter out small bboxes and outside bboxes after Mosaic."""
    bbox_x, bbox_y, bbox_w, bbox_h = bboxes[:, 0], bboxes[:, 1], bboxes[:, 2], bboxes[:, 3]
    # TODO 截断resize情况,比较复杂, 考虑中心点到边界距离
    # 比例截断系数, 0.5 * 0.3
    ratio *= 0.5
    valid_inds = (
        (bbox_x > w_min)
        & (bbox_x < w_max)
        & (bbox_y > h_min)
        & (bbox_y < h_max)
        & ((bbox_x + ratio * bbox_w) < w_max)
        & ((bbox_x - ratio * bbox_w) > w_min)
        & ((bbox_y + ratio * bbox_h) < h_max)
        & ((bbox_y - ratio * bbox_h) > h_min)
        & (bbox_w > min_bbox_size)
        & (bbox_h > min_bbox_size)
    )
    valid_inds = np.nonzero(valid_inds)[0]
    return valid_inds
