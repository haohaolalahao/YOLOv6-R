# YOLOv6m model
model = dict(
    type="YOLOv6m",
    pretrained="weights/yolov6m.pt",
    depth_multiple=0.60,
    width_multiple=0.75,
    backbone=dict(
        type="CSPBepBackbone",
        num_repeats=[1, 6, 12, 18, 6],
        out_channels=[64, 128, 256, 512, 1024],
        csp_e=float(2) / 3,
        fuse_P2=True,
    ),
    neck=dict(
        type="CSPRepBiFPANNeck",
        num_repeats=[12, 12, 12, 12],
        out_channels=[256, 128, 128, 256, 256, 512],
        csp_e=float(2) / 3,
    ),
    head=dict(
        type="EffiDeHead",
        in_channels=[128, 256, 512],
        num_layers=3,
        begin_indices=24,
        anchors=3,
        anchors_init=[[10, 13, 19, 19, 33, 23], [30, 61, 59, 59, 59, 119], [116, 90, 185, 185, 373, 326]],
        out_indices=[17, 20, 23],
        strides=[8, 16, 32],
        atss_warmup_epoch=0,
        iou_type="giou",
        use_dfl=False,
        reg_max=0,  # if use_dfl is False, please set reg_max to 0
        distill_weight={"class": 0.8, "dfl": 1.0,},
        # NOTE for angle regression
        # angle_fitting_methods='regression',
        # angle_max=1,
        # NOTE for angle csl
        # angle_fitting_methods="csl",
        # angle_max=180,
        # NOTE for angle dfl
        # angle_fitting_methods='dfl',
        # angle_max=180,
        # NOTE for angle MGAR
        angle_fitting_methods='MGAR',
        angle_max=5,
    ),
)

loss = dict(
    loss_mode="hbb+angle",
    # loss_mode="obb",
    # NOTE for angle regression
    # loss_weight={"class": 1.0, "iou": 2.5, "dfl": 0.5, "angle": 0.05},
    # NOTE for angle classification
    # loss_weight={"class": 1.0, "iou": 2.5, "dfl": 0.5, "angle": 0.05, "cwd":10},
    # NOTE for angle MGAR
    loss_weight={"class": 1.0, "iou": 2.5, "dfl": 0.5, "angle": 0.05, "MGAR_cls": 0.05, "MGAR_reg": 0.05, 'cwd': 0.2, },
)
solver = dict(
    optim="AdamW",
    lr_scheduler="Cosine",
    lr0=0.00025,
    lrf=0.05,
    momentum=0.843,
    weight_decay=0.00036,
    warmup_epochs=2.0,
    warmup_momentum=0.5,
    warmup_bias_lr=0.05,
)

data_aug = dict(
    # degrees=0.373,
    # translate=0.245,
    # scale=0.898,
    # shear=0.602,
    hsv=0.0,
    hsv_h=0.0138,
    hsv_s=0.664,
    hsv_v=0.464,
    flipud=0.5,
    fliplr=0.5,
    rotate=0.5,
    rect_classes=[9,11],
    # NOTE mosaic 数值需要确定一下
    mosaic=0.0,
    mixup_mosaic=0.0,
    mixup=0.0,
)

eval_params = dict(
    conf_thres=0.03,
    verbose=True,
    do_coco_metric=False,
    do_pr_metric=True,
    plot_curve=True,
    plot_confusion_matrix=True,
    # NOTE VOC12 VOC07 COCO
    ap_method="COCO",
)
