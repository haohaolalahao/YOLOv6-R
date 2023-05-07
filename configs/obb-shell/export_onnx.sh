CUDA_VISIBLE_DEVICES=1 python deploy/ONNX/export_onnx_R.py \
	--device '0' \
	--batch-size 1 \
	--weights "runs/DOTA-ms-baseline/yolov6n_MGAR1/weights/best_ckpt.pt" \
	--simplify \
	--half \
	--inplace
