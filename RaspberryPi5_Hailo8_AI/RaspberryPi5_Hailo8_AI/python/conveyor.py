# conveyor.py

import lgpio

from config import (
    MOTOR_GPIO_A,
    MOTOR_GPIO_B,
    MOTOR_PWM
)


class Conveyor:

    def __init__(self):

        self.gpio_handle = None
        self.running = False

        self._setup_gpio()


    def _setup_gpio(self):

        self.gpio_handle = lgpio.gpiochip_open(0)

        lgpio.gpio_claim_output(
            self.gpio_handle,
            MOTOR_GPIO_A,
            0
        )

        lgpio.gpio_claim_output(
            self.gpio_handle,
            MOTOR_GPIO_B,
            0
        )


    def start(self):

        if self.running:
            return

        # 정방향
        lgpio.gpio_write(
            self.gpio_handle,
            MOTOR_GPIO_B,
            0
        )

        # PWM 75%
        lgpio.tx_pwm(
            self.gpio_handle,
            MOTOR_GPIO_A,
            1000,
            MOTOR_PWM
        )

        self.running = True


    def stop(self):

        if not self.running:
            return

        lgpio.tx_pwm(
            self.gpio_handle,
            MOTOR_GPIO_A,
            1000,
            0
        )

        lgpio.gpio_write(
            self.gpio_handle,
            MOTOR_GPIO_B,
            0
        )

        self.running = False


    def close(self):

        try:

            self.stop()

            lgpio.gpio_free(
                self.gpio_handle,
                MOTOR_GPIO_A
            )

            lgpio.gpio_free(
                self.gpio_handle,
                MOTOR_GPIO_B
            )

            lgpio.gpiochip_close(
                self.gpio_handle
            )

        except Exception:
            pass