\# ONNX to HEF Conversion



This project uses YOLOv8s for PCB defect detection.



The trained YOLOv8s model is exported to ONNX format and compiled into a Hailo HEF model using Hailo Model Zoo.



\## Model



\- Model: YOLOv8s

\- Number of classes: 3

\- Classes:

&#x20; - bent

&#x20; - missing

&#x20; - solder defect

\- Hardware architecture: Hailo-8L



\## Conversion



The ONNX model is compiled using the following command:



```bash

hailomz compile \\

&#x20; --ckpt /mnt/d/best.onnx \\

&#x20; --yaml \~/hailo\_model\_zoo/hailo\_model\_zoo/cfg/networks/yolov8s.yaml \\

&#x20; --hw-arch hailo8l \\

&#x20; --calib-path /mnt/d/calib\_images \\

&#x20; --classes 3 \\

&#x20; --start-node-names images \\

&#x20; --end-node-names \\

&#x20;   /model.22/cv2.0/cv2.0.2/Conv \\

&#x20;   /model.22/cv3.0/cv3.0.2/Conv \\

&#x20;   /model.22/cv2.1/cv2.1.2/Conv \\

&#x20;   /model.22/cv3.1/cv3.1.2/Conv \\

&#x20;   /model.22/cv2.2/cv2.2.2/Conv \\

&#x20;   /model.22/cv3.2/cv3.2.2/Conv

