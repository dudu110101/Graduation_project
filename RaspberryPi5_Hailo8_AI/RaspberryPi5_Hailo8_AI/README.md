\# Raspberry Pi 5 기반 PCB 조립 불량 검사 시스템



Raspberry Pi 5와 Hailo AI 가속기를 기반으로 YOLOv8을 이용하여 PCB 조립 상태를 실시간으로 검사하고, 불량 유형에 따라 자동으로 분류하는 임베디드 시스템입니다.



\## 1. 프로젝트 개요



컨베이어 벨트를 통해 이동하는 PCB를 카메라로 촬영하고, YOLOv8 기반 객체 검출 모델을 이용하여 조립 불량을 검사합니다.



검출된 불량 유형에 따라 Raspberry Pi 5에서 Arduino Nano로 제어 신호를 전달하고, 서보모터를 이용하여 PCB를 분류합니다.



\### 검사 대상



\* Good : 정상 PCB

\* Bent : 부품 휨

\* Missing : 부품 누락

\* Solder Defect : 납땜 불량



\## 2. 시스템 구성



```text

Camera

&#x20;  ↓

Raspberry Pi 5

&#x20;  ↓

Hailo AI Accelerator

&#x20;  ↓

YOLOv8

&#x20;  ↓

PCB Defect Inspection

&#x20;  ↓

Arduino Nano

&#x20;  ↓

Servo Motors

&#x20;  ↓

PCB Sorting

```



컨베이어 벨트는 Raspberry Pi 5의 GPIO와 L9110S 모터 드라이버를 이용하여 제어합니다.



\## 3. 주요 기능



\* Raspberry Pi Camera Module을 이용한 실시간 영상 입력

\* Hailo AI 가속기를 이용한 YOLOv8 추론

\* PCB 조립 불량 검출

\* Bent / Missing / Solder Defect 분류

\* 정상 및 불량 PCB 검사 결과 카운트

\* 불량 PCB 이미지 저장 및 표시

\* Arduino Nano를 이용한 서보모터 제어

\* 컨베이어 벨트 자동 제어

\* 검사 결과 로그 저장



\## 4. Hardware



| Hardware                     | Description    |

| ---------------------------- | -------------- |

| Raspberry Pi 5               | 시스템 제어 및 영상 처리 |

| Hailo AI Accelerator         | YOLOv8 추론 가속   |

| Raspberry Pi Camera Module 3 | PCB 영상 촬영      |

| Arduino Nano                 | 서보모터 제어        |

| L9110S                       | DC 모터 제어       |

| TT Motor                     | 컨베이어 벨트 구동     |

| Servo Motor × 3              | PCB 분류         |



\## 5. Software



\* Python

\* OpenCV

\* Picamera2

\* HailoRT

\* Hailo Model Zoo

\* YOLOv8

\* Arduino IDE



\## 6. Project Structure



```text

RaspberryPi5\_Halio8\_AI/

│

├── .gitignore

├── README.md

│

├── python/

│   ├── main.py

│   ├── config.py

│   ├── camera.py

│   ├── detector.py

│   ├── conveyor.py

│   ├── inspector.py

│   ├── display.py

│   ├── logger.py

│   └── arduino.py

│

├── arduino/

│   └── servo\_controller.ino

│

└── model\_conversion/

&#x20;   ├── onnx\_to\_hef.sh

&#x20;   └── README.md

```



\## 7. Python Configuration



주요 설정은 `python/config.py`에서 관리합니다.



```text

Camera:

960 × 540



YOLO Input:

512 × 512



Confidence:

0.50



PCB ROI:

(370, 160) \~ (570, 320)



PCB Detection:

8 consecutive frames



Defect Confirmation:

3 frames



Motor GPIO:

22, 23



Motor PWM:

75%



Arduino:

/dev/ttyUSB0

9600 baud

```



\## 8. HEF Model



Hailo에서 사용하는 HEF 모델 파일은 저장소에 포함하지 않습니다.



기본 모델 경로:



```text

/home/pi/Desktop/holy.hef

```



ONNX 모델을 HEF로 변환하는 방법은 다음 파일을 참고합니다.



```text

model\_conversion/onnx\_to\_hef.sh

model\_conversion/README.md

```



\## 9. Arduino



Arduino Nano는 Raspberry Pi 5와 Serial 통신을 사용하여 서보모터를 제어합니다.



사용하는 Serial 장치:



```text

/dev/ttyUSB0

```



Baud rate:



```text

9600

```



서보모터는 PCB 불량 유형에 따라 각각 다른 동작을 수행합니다.



```text

BENT

MISSING

SOLDER

```



정상 PCB의 경우 별도의 서보 동작을 수행하지 않습니다.



\## 10. Dataset



YOLOv8 학습에 사용한 PCB 이미지 데이터셋은 저장소에 포함하지 않습니다.



대용량 데이터셋 및 학습 결과 파일은 GitHub 저장소의 크기를 고려하여 제외합니다.



\## 11. 실행



Raspberry Pi에서 필요한 환경을 구성한 후 다음과 같이 실행합니다.



```bash

cd \~/RaspberryPi5\_Halio8\_AI/python



python3 main.py

```



실행 전 다음 항목이 정상적으로 연결되어 있어야 합니다.



\* Raspberry Pi Camera

\* Hailo AI Accelerator

\* Arduino Nano

\* L9110S Motor Driver

\* Conveyor Motor

\* Servo Motors



\## 12. License



This project was developed as a university graduation project.



