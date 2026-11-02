# inspector.py

import cv2
import numpy as np
from collections import Counter

from config import (
    ROI_X1,
    ROI_Y1,
    ROI_X2,
    ROI_Y2,
    PCB_DETECT_FRAMES,
    DEFECT_CONFIRM_FRAMES,
    BLUE_H_MIN,
    BLUE_S_MIN,
    BLUE_V_MIN,
    BLUE_H_MAX,
    BLUE_S_MAX,
    BLUE_V_MAX,
    BLUE_RATIO_THRESHOLD
)


# ============================================================
# Inspection Result
# ============================================================

class InspectionResult:

    def __init__(
        self,
        label="good",
        detections=None,
        is_finished=False,
        is_defect=False,
        should_stop=False
    ):

        self.label = label

        self.detections = (
            detections
            if detections is not None
            else []
        )

        self.is_finished = is_finished

        self.is_defect = is_defect

        # 컨베이어 정지 여부
        self.should_stop = should_stop


# ============================================================
# Inspector
# ============================================================

class Inspector:

    def __init__(self, detector):

        self.detector = detector

        # ----------------------------------------------------
        # PCB 진입 프레임
        # ----------------------------------------------------

        self.pcb_frame_count = 0

        # ----------------------------------------------------
        # 검사 중인지
        # ----------------------------------------------------

        self.inspecting = False

        # ----------------------------------------------------
        # 검사 프레임 결과
        # ----------------------------------------------------

        self.inspection_results = []

        # ----------------------------------------------------
        # 검사 이미지
        # ----------------------------------------------------

        self.inspection_frames = []

        # ----------------------------------------------------
        # 마지막 정상적인 detection 데이터
        # ----------------------------------------------------

        self.last_detections = []


    # ========================================================
    # ROI 내부 여부
    # ========================================================

    def is_box_in_roi(self, box):

        x1, y1, x2, y2 = box

        center_x = (
            x1 + x2
        ) / 2

        center_y = (
            y1 + y2
        ) / 2

        return (
            ROI_X1 <= center_x <= ROI_X2
            and
            ROI_Y1 <= center_y <= ROI_Y2
        )


    # ========================================================
    # PCB 감지
    #
    # YOLO detection이 아니라
    # ROI 내부의 파란색 PCB를 기준으로 판단
    # ========================================================

    def detect_pcb(self, frame):

        roi = frame[
            ROI_Y1:ROI_Y2,
            ROI_X1:ROI_X2
        ]

        if roi.size == 0:
            return False

        # RGB888 카메라 영상 → HSV
        hsv = cv2.cvtColor(
            roi,
            cv2.COLOR_RGB2HSV
        )

        lower_blue = np.array(
            [
                BLUE_H_MIN,
                BLUE_S_MIN,
                BLUE_V_MIN
            ],
            dtype=np.uint8
        )

        upper_blue = np.array(
            [
                BLUE_H_MAX,
                BLUE_S_MAX,
                BLUE_V_MAX
            ],
            dtype=np.uint8
        )

        mask = cv2.inRange(
            hsv,
            lower_blue,
            upper_blue
        )

        blue_pixels = cv2.countNonZero(
            mask
        )

        roi_area = (
            ROI_X2 - ROI_X1
        ) * (
            ROI_Y2 - ROI_Y1
        )

        if roi_area <= 0:
            return False

        blue_ratio = (
            blue_pixels / roi_area
        )

        return (
            blue_ratio
            >= BLUE_RATIO_THRESHOLD
        )


    # ========================================================
    # 불량 검사 시작
    # ========================================================

    def start_inspection(self):

        self.inspecting = True

        self.inspection_results = []

        self.inspection_frames = []

        self.last_detections = []


    # ========================================================
    # 검사 프레임 추가
    # ========================================================

    def add_inspection_result(
        self,
        detections,
        frame
    ):

        # 검사 이미지 저장
        self.inspection_frames.append(
            frame.copy()
        )

        # 현재 detection 저장
        self.last_detections = detections

        frame_labels = []

        for detection in detections:

            label = detection.get(
                "label",
                ""
            )

            if label in (
                "bent",
                "missing",
                "solder defect"
            ):

                frame_labels.append(
                    label
                )

        self.inspection_results.append(
            frame_labels
        )


    # ========================================================
    # 3프레임 불량 판정
    # ========================================================

    def determine_result(self):

        counter = Counter()

        for frame_result in (
            self.inspection_results
        ):

            for label in frame_result:

                counter[label] += 1

        # 불량이 한 번도 검출되지 않은 경우
        if not counter:
            return "good"

        # 가장 많이 검출된 불량
        label, count = (
            counter.most_common(1)[0]
        )

        # 동일 불량이 3프레임 이상 검출
        if count >= DEFECT_CONFIRM_FRAMES:

            return label

        return "good"


    # ========================================================
    # 검사 종료
    # ========================================================

    def finish_inspection(self):

        result_label = self.determine_result()

        is_defect = (
            result_label != "good"
        )

        # 화면에 표시할 detection은
        # 문자열 label이 아니라 실제 detection 데이터 사용
        detections = self.last_detections

        self.inspecting = False

        result = InspectionResult(
            label=result_label,
            detections=detections,
            is_finished=True,
            is_defect=is_defect,
            should_stop=False
        )

        return result


    # ========================================================
    # 전체 처리
    # ========================================================

    def process(
        self,
        frame,
        conveyor_running
    ):

        # ----------------------------------------------------
        # YOLO / Hailo 추론
        # ----------------------------------------------------

        detections = self.detector.detect(
            frame
        )

        # ----------------------------------------------------
        # 현재 검사 중
        # ----------------------------------------------------

        if self.inspecting:

            self.add_inspection_result(
                detections,
                frame
            )

            # 3프레임 검사 완료
            if len(
                self.inspection_results
            ) >= DEFECT_CONFIRM_FRAMES:

                return self.finish_inspection()

            return InspectionResult(
                detections=detections
            )


        # ----------------------------------------------------
        # 검사 중이 아니면
        # PCB 진입 확인
        # ----------------------------------------------------

        pcb_detected = self.detect_pcb(
            frame
        )

        if pcb_detected:

            self.pcb_frame_count += 1

        else:

            self.pcb_frame_count = 0


        # ----------------------------------------------------
        # PCB가 8프레임 연속 검출됨
        # ----------------------------------------------------

        if (
            self.pcb_frame_count
            >= PCB_DETECT_FRAMES
        ):

            self.pcb_frame_count = 0

            self.start_inspection()

            self.add_inspection_result(
                detections,
                frame
            )

            # main.py에서 컨베이어 정지
            return InspectionResult(
                detections=detections,
                should_stop=True
            )


        # ----------------------------------------------------
        # 일반 상태
        # ----------------------------------------------------

        return InspectionResult(
            detections=detections
        )


    # ========================================================
    # 마지막 검사 이미지 반환
    # ========================================================

    def get_last_inspection_frame(self):

        if not self.inspection_frames:
            return None

        return self.inspection_frames[-1]