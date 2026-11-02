# logger.py

import os
from datetime import datetime

from config import (
    LOG_DIRECTORY,
    DEFECT_IMAGE_DIRECTORY
)


class InspectionLogger:

    def __init__(self):

        os.makedirs(
            LOG_DIRECTORY,
            exist_ok=True
        )

        os.makedirs(
            DEFECT_IMAGE_DIRECTORY,
            exist_ok=True
        )

        self.log_file = os.path.join(
            LOG_DIRECTORY,
            "inspection_log.csv"
        )

        self._create_log_file()


    def _create_log_file(self):

        if not os.path.exists(
            self.log_file
        ):

            with open(
                self.log_file,
                "w",
                encoding="utf-8"
            ) as file:

                file.write(
                    "datetime,result\n"
                )


    # --------------------------------------------------------
    # 결과 기록
    # --------------------------------------------------------

    def write(self, result):

        now = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        with open(
            self.log_file,
            "a",
            encoding="utf-8"
        ) as file:

            file.write(
                f"{now},{result.label}\n"
            )


    # --------------------------------------------------------
    # 불량 이미지 저장
    # --------------------------------------------------------

    def save_defect_image(
        self,
        frame,
        label
    ):

        if frame is None:
            return None

        now = datetime.now().strftime(
            "%Y%m%d_%H%M%S_%f"
        )

        filename = (
            f"{now}_{label.replace(' ', '_')}.jpg"
        )

        filepath = os.path.join(
            DEFECT_IMAGE_DIRECTORY,
            filename
        )

        try:

            import cv2

            cv2.imwrite(
                filepath,
                frame
            )

            return filepath

        except Exception as e:

            print(
                f"[Logger] Image save error: {e}"
            )

            return None