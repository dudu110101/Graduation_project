# main.py

import time

from camera import Camera
from detector import HailoDetector
from conveyor import Conveyor
from arduino import ArduinoController
from inspector import Inspector
from display import Display
from logger import InspectionLogger


def main():

    print("=" * 60)
    print("PCB Inspection System")
    print("=" * 60)

    camera = None
    detector = None
    conveyor = None
    arduino = None
    inspector = None
    display = None
    logger = None

    try:

        # ====================================================
        # 객체 생성
        # ====================================================

        print("[System] Initializing camera...")

        camera = Camera()


        print("[System] Initializing Hailo...")

        detector = HailoDetector()


        print("[System] Initializing conveyor...")

        conveyor = Conveyor()


        print("[System] Initializing Arduino...")

        arduino = ArduinoController()


        print("[System] Initializing inspector...")

        inspector = Inspector(
            detector
        )


        print("[System] Initializing display...")

        display = Display()


        print("[System] Initializing logger...")

        logger = InspectionLogger()


        # ====================================================
        # Camera start
        # ====================================================

        camera.start()

        time.sleep(1)


        # ====================================================
        # Conveyor start
        # ====================================================

        conveyor.start()

        print(
            "[System] Conveyor started."
        )

        print(
            "[System] Inspection started."
        )


        # ====================================================
        # Main loop
        # ====================================================

        while True:

            frame = camera.capture()


            # ------------------------------------------------
            # 검사 처리
            # ------------------------------------------------

            result = inspector.process(
                frame,
                conveyor_running=conveyor.running
            )


            detections = result.detections


            # ------------------------------------------------
            # PCB 감지 후 컨베이어 정지
            # ------------------------------------------------

            if result.should_stop:

                print(
                    "[System] PCB detected."
                )

                print(
                    "[System] Conveyor stopped."
                )

                conveyor.stop()


            # ------------------------------------------------
            # 화면 출력
            # ------------------------------------------------

            display.show(
                frame,
                detections
            )


            # ------------------------------------------------
            # 검사 완료
            # ------------------------------------------------

            if result.is_finished:

                label = result.label


                print(
                    f"[Inspection] Result: {label}"
                )


                # ------------------------------------------------
                # 카운터 증가
                # ------------------------------------------------

                display.update_count(
                    label
                )


                # ------------------------------------------------
                # 검사 로그
                # ------------------------------------------------

                logger.write(
                    result
                )


                # ------------------------------------------------
                # 불량 처리
                # ------------------------------------------------

                if result.is_defect:

                    print(
                        f"[Inspection] Defect: {label}"
                    )


                    # 마지막 검사 이미지
                    defect_frame = (
                        inspector
                        .get_last_inspection_frame()
                    )


                    # 불량 이미지 저장
                    logger.save_defect_image(
                        defect_frame,
                        label
                    )


                    # 불량 이미지 표시
                    display.show_defect_image(
                        defect_frame,
                        label
                    )


                    # Arduino 서보 제어
                    arduino.send_result(
                        label
                    )


                else:

                    print(
                        "[Inspection] Good PCB"
                    )


                # ------------------------------------------------
                # 컨베이어 재가동
                # ------------------------------------------------

                time.sleep(0.2)

                conveyor.start()

                print(
                    "[System] Conveyor restarted."
                )


            # ------------------------------------------------
            # 종료 키
            # ------------------------------------------------

            key = display.get_key()


            if key == ord("q"):

                print(
                    "[System] Quit requested."
                )

                break


    # ========================================================
    # KeyboardInterrupt
    # ========================================================

    except KeyboardInterrupt:

        print(
            "\n[System] Keyboard interrupt."
        )


    # ========================================================
    # Exception
    # ========================================================

    except Exception as e:

        print(
            f"[System] Error: {e}"
        )


    # ========================================================
    # 종료 처리
    # ========================================================

    finally:

        print(
            "[System] Shutting down..."
        )


        # ----------------------------------------------------
        # Conveyor
        # ----------------------------------------------------

        if conveyor is not None:

            try:

                conveyor.stop()

                conveyor.close()

            except Exception:
                pass


        # ----------------------------------------------------
        # Camera
        # ----------------------------------------------------

        if camera is not None:

            try:

                camera.stop()

            except Exception:
                pass


        # ----------------------------------------------------
        # Arduino
        # ----------------------------------------------------

        if arduino is not None:

            try:

                arduino.close()

            except Exception:
                pass


        # ----------------------------------------------------
        # Hailo
        # ----------------------------------------------------

        if detector is not None:

            try:

                detector.close()

            except Exception:
                pass


        # ----------------------------------------------------
        # Display
        # ----------------------------------------------------

        if display is not None:

            try:

                display.close()

            except Exception:
                pass


        print(
            "[System] Shutdown complete."
        )


if __name__ == "__main__":

    main()