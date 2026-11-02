# display.py

import cv2

from config import (
    WINDOW_NAME
)


class Display:

    def __init__(self):

        self.window_name = WINDOW_NAME

        self.good_count = 0
        self.bent_count = 0
        self.missing_count = 0
        self.solder_count = 0


    # ========================================================
    # 카운터 증가
    # ========================================================

    def update_count(self, label):

        if label == "good":

            self.good_count += 1

        elif label == "bent":

            self.bent_count += 1

        elif label == "missing":

            self.missing_count += 1

        elif label == "solder defect":

            self.solder_count += 1


    # ========================================================
    # Bounding Box
    # ========================================================

    def draw_detections(
        self,
        frame,
        detections
    ):

        output = frame.copy()

        for detection in detections:

            # detection이 정상적인 dictionary인지 확인
            if not isinstance(
                detection,
                dict
            ):
                continue

            if "box" not in detection:
                continue

            if "label" not in detection:
                continue

            if "confidence" not in detection:
                continue


            x1, y1, x2, y2 = (
                detection["box"]
            )

            label = detection["label"]

            confidence = (
                detection["confidence"]
            )


            cv2.rectangle(
                output,
                (x1, y1),
                (x2, y2),
                (255, 0, 0),
                2
            )


            text = (
                f"{label} "
                f"{confidence:.2f}"
            )


            cv2.putText(
                output,
                text,
                (
                    x1,
                    max(
                        20,
                        y1 - 5
                    )
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 0, 0),
                2
            )


        return output


    # ========================================================
    # 카운터
    # ========================================================

    def draw_counter(self, frame):

        output = frame.copy()

        lines = [
            f"Good: {self.good_count}",
            f"Bent: {self.bent_count}",
            f"Missing: {self.missing_count}",
            f"Solder: {self.solder_count}"
        ]


        y = 30


        for line in lines:

            cv2.putText(
                output,
                line,
                (10, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )

            y += 30


        return output


    # ========================================================
    # 화면 출력
    # ========================================================

    def show(
        self,
        frame,
        detections
    ):

        output = self.draw_detections(
            frame,
            detections
        )

        output = self.draw_counter(
            output
        )

        cv2.imshow(
            self.window_name,
            output
        )


    # ========================================================
    # 키 입력
    # ========================================================

    def get_key(self):

        return cv2.waitKey(1) & 0xFF


    # ========================================================
    # 불량 이미지 표시
    # ========================================================

    def show_defect_image(
        self,
        frame,
        label
    ):

        if frame is None:
            return


        window_name = (
            f"Defect - {label}"
        )


        cv2.imshow(
            window_name,
            frame
        )


    # ========================================================
    # 종료
    # ========================================================

    def close(self):

        cv2.destroyAllWindows()