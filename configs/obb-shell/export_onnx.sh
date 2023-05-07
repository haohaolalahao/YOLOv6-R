CUDA_VISIBLE_DEVICES=1 python deploy/ONNX/export_onnx_R.py \
	--device '0' \
	--batch-size 1 \
	--img-size 800 \
	--weights "runs/HRSC2016-baseline/yolov6n-obb+nodetach/weights/best_ckpt.pt" \
	--simplify \
	--half \
	--inplace
