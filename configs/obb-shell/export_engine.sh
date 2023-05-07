onnx_path="runs/HRSC2016-baseline/yolov6n-obb+nodetach/weights/best_ckpt.onnx"
engine_path="runs/HRSC2016-baseline/yolov6n-obb+nodetach/weights/best_ckpt.engine"
CUDA_VISIBLE_DEVICES=1 trtexec \
    --onnx=$onnx_path \
    --saveEngine=$engine_path \
    --fp16 \
    --verbose
