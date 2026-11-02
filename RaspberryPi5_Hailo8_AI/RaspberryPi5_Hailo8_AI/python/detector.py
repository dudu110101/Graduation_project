# detector.py

import cv2
import numpy as np

from hailo_platform import (
    HEF,
    VDevice,
    HailoStreamInterface,
    InferVStreams,
    ConfigureParams,
    InputVStreamParams,
    OutputVStreamParams,
    FormatType
)

from config import (
    HEF_PATH,
    INPUT_SIZE,
    CONF_THRESHOLD,
    CLASS_NAMES
)


class HailoDetector:

    def __init__(self):

        self.hef_path = HEF_PATH
        self.input_size = INPUT_SIZE
        self.conf_threshold = CONF_THRESHOLD
        self.class_names = CLASS_NAMES

        self.target = None
        self.network_group = None
        self.input_vstream_params = None
        self.output_vstream_params = None

        self.input_name = None

        self._initialize_hailo()


    # --------------------------------------------------------
    # Hailo 초기화
    # --------------------------------------------------------

    def _initialize_hailo(self):

        self.target = VDevice()

        self.hef = HEF(
            self.hef_path
        )

        configure_params = ConfigureParams.create_from_hef(
            self.hef,
            interface=HailoStreamInterface.PCIe
        )

        network_groups = self.target.configure(
            self.hef,
            configure_params
        )

        self.network_group = network_groups[0]

        self.input_vstream_params = InputVStreamParams.make(
            self.network_group,
            format_type=FormatType.UINT8
        )

        self.output_vstream_params = OutputVStreamParams.make(
            self.network_group,
            format_type=FormatType.FLOAT32
        )

        input_infos = self.hef.get_input_vstream_infos()

        self.input_name = input_infos[0].name


    # --------------------------------------------------------
    # Letterbox
    # --------------------------------------------------------

    def letterbox_image(self, image):

        original_height, original_width = image.shape[:2]

        scale = min(
            self.input_size / original_width,
            self.input_size / original_height
        )

        new_width = int(
            original_width * scale
        )

        new_height = int(
            original_height * scale
        )

        resized = cv2.resize(
            image,
            (new_width, new_height),
            interpolation=cv2.INTER_LINEAR
        )

        canvas = np.full(
            (
                self.input_size,
                self.input_size,
                3
            ),
            114,
            dtype=np.uint8
        )

        pad_x = (
            self.input_size - new_width
        ) // 2

        pad_y = (
            self.input_size - new_height
        ) // 2

        canvas[
            pad_y:pad_y + new_height,
            pad_x:pad_x + new_width
        ] = resized

        return canvas, scale, pad_x, pad_y


    # --------------------------------------------------------
    # Output parsing
    # --------------------------------------------------------

    def parse_output(
        self,
        output,
        scale,
        pad_x,
        pad_y,
        original_width,
        original_height
    ):

        detections = []

        if output is None:
            return detections

        try:

            if isinstance(output, dict):

                output_values = list(
                    output.values()
                )

                if len(output_values) == 0:
                    return detections

                output = output_values[0]

        except Exception:
            return detections


        # ----------------------------------------------------
        # Hailo YOLO output 형태 처리
        # ----------------------------------------------------

        try:

            if isinstance(output, np.ndarray):

                data = output

                # 출력이 리스트 구조인 경우
                if data.dtype == object:
                    data = np.asarray(
                        data.tolist(),
                        dtype=np.float32
                    )

                # 일반적인 [N, 6] 형태
                if data.ndim == 2:

                    for detection in data:

                        if len(detection) < 6:
                            continue

                        x1 = float(detection[0])
                        y1 = float(detection[1])
                        x2 = float(detection[2])
                        y2 = float(detection[3])

                        score = float(
                            detection[4]
                        )

                        class_id = int(
                            detection[5]
                        )

                        if score < self.conf_threshold:
                            continue

                        if class_id < 0:
                            continue

                        if class_id >= len(
                            self.class_names
                        ):
                            continue

                        # 정규화 좌표인지 확인
                        if (
                            0 <= x1 <= 1 and
                            0 <= y1 <= 1 and
                            0 <= x2 <= 1 and
                            0 <= y2 <= 1
                        ):

                            x1 *= self.input_size
                            x2 *= self.input_size
                            y1 *= self.input_size
                            y2 *= self.input_size

                        # padding 제거
                        x1 -= pad_x
                        x2 -= pad_x
                        y1 -= pad_y
                        y2 -= pad_y

                        # 원본 이미지 좌표 변환
                        x1 /= scale
                        x2 /= scale
                        y1 /= scale
                        y2 /= scale

                        x1 = max(
                            0,
                            min(
                                original_width - 1,
                                int(x1)
                            )
                        )

                        y1 = max(
                            0,
                            min(
                                original_height - 1,
                                int(y1)
                            )
                        )

                        x2 = max(
                            0,
                            min(
                                original_width - 1,
                                int(x2)
                            )
                        )

                        y2 = max(
                            0,
                            min(
                                original_height - 1,
                                int(y2)
                            )
                        )

                        detections.append({
                            "class_id": class_id,
                            "label": self.class_names[class_id],
                            "confidence": score,
                            "box": (
                                x1,
                                y1,
                                x2,
                                y2
                            )
                        })

        except Exception as e:

            print(
                f"[Hailo] Output parsing error: {e}"
            )

        return detections


    # --------------------------------------------------------
    # Detection
    # --------------------------------------------------------

    def detect(self, frame):

        original_height, original_width = (
            frame.shape[:2]
        )

        input_image, scale, pad_x, pad_y = (
            self.letterbox_image(frame)
        )

        input_data = np.expand_dims(
            input_image,
            axis=0
        )

        try:

            with self.network_group.activate():

                with InferVStreams(
                    self.network_group,
                    self.input_vstream_params,
                    self.output_vstream_params
                ) as infer_pipeline:

                    input_dict = {
                        self.input_name:
                            input_data
                    }

                    output = infer_pipeline.infer(
                        input_dict
                    )

            detections = self.parse_output(
                output,
                scale,
                pad_x,
                pad_y,
                original_width,
                original_height
            )

            return detections

        except Exception as e:

            print(
                f"[Hailo] Inference error: {e}"
            )

            return []


    # --------------------------------------------------------
    # Close
    # --------------------------------------------------------

    def close(self):

        try:

            if self.target is not None:
                self.target.release()

        except Exception:
            pass