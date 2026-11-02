#!/bin/bash

hailomz compile \
  --ckpt /mnt/d/best.onnx \
  --yaml ~/hailo_model_zoo/hailo_model_zoo/cfg/networks/yolov8s.yaml \
  --hw-arch hailo8l \
  --calib-path /mnt/d/calib_images \
  --classes 3 \
  --start-node-names images \
  --end-node-names \
    /model.22/cv2.0/cv2.0.2/Conv \
    /model.22/cv3.0/cv3.0.2/Conv \
    /model.22/cv2.1/cv2.1.2/Conv \
    /model.22/cv3.1/cv3.1.2/Conv \
    /model.22/cv2.2/cv2.2.2/Conv \
    /model.22/cv3.2/cv3.2.2/Conv