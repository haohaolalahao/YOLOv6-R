weight_path="weights/yolov6_l_MGAR_DOTA_ms.pt"
source_path="data/images"
# save_dir=""
project="runs/inference"
name="exp"
CUDA_VISIBLE_DEVICES=1 python tools/infer_R.py \
	--weights $weight_path \
	--source $source_path \
	--project $project \
	--name $name \
	--yaml "data/DOTA-ms.yaml" \
	--img-size 1024 \
	--conf-thres 0.1 \
	--iou-thres 0.65 \
	--max-det 1000 \
	--device 0 \
	--half
# --hide-labels
# --hide-conf
# --save-dir $save_dir
# --save-txt
# --classes 1 2 3
# --agnostic-nms
# --not-save-img
# --view-img
# --webcam
# --webcam-addr
