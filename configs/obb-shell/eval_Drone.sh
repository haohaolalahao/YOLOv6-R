CUDA_VISIBLE_DEVICES=0 python3 tools/eval_R_Deploy.py \
	--data "./data/DIOR.yaml" \
	--weights "/home/crescent/YOLOv6-R/demo.engine"\
	--batch-size 1 \
	--img-size 800 \
	--conf-thres 0.1 \
	--iou-thres 0.65 \
	--task "val"\
	--device 0 \
	--save_dir "./runs/val/" \
	--name "dior" \
	--do_coco_metric False \
	--do_pr_metric True \
	--ap_method 'VOC07' \
	--verbose \
	--half \
	--plot_confusion_matrix \
	--letterbox_return_int \
	--scale_exact \
    --force_no_pad
# --not_infer_on_rect
# --test_load_size 800 \
# parser.add_argument('--reproduce_640_eval', default=False, action='store_true', help='whether to reproduce 640 infer result, overwrite some config')
# parser.add_argument('--eval_config_file', type=str, default='./configs/experiment/eval_640_repro.py', help='config file for repro 640 infer result')
# parser.add_argument('--config-file', default='', type=str, help='experiments description file, lower priority than reproduce_640_eval')
