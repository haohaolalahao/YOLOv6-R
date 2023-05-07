CUDA_VISIBLE_DEVICES=1 trtexec \
    --onnx=/home/crescent/YOLOv6-R/runs/DIOR/yolov6s_csl_dfl_AdamW_small_lr3/weights/best_ckpt.onnx \
    --saveEngine=/home/crescent/YOLOv6-R/demo.engine \
    --fp16 \
    --verbose \

    