"""A fake fan that does nothing but to demonstrate optional characteristics."""
import logging

import RPi.GPIO as GPIO

from pyhap.accessory import Accessory, Category
import pyhap.loader as loader

logger = logging.getLogger(__name__)

SPEED_1_PIN = 7
SPEED_2_PIN = 11
SPEED_3_PIN = 12


class Fan(Accessory):
    """A fan accessory that logs changes to its rotation speed."""
    category = Category.FAN

    @classmethod
    def _gpio_setup(_cls):
        if GPIO.getmode() is None:
            GPIO.setmode(GPIO.BOARD)
        GPIO.setup(SPEED_1_PIN, GPIO.OUT)
        GPIO.setup(SPEED_2_PIN, GPIO.OUT)
        GPIO.setup(SPEED_3_PIN, GPIO.OUT)

    def __init__(self, *args, **kwargs):
        super(Fan, self).__init__(*args, **kwargs)
        self.power_on = False
        self.rotation_speed = 100
        self._gpio_setup()

    def __setstate__(self, state):
        self.__dict__.update(state)
        self._gpio_setup()

    def set_fan(self, value):
        if value:
            self.power_on = True
            self._set_speed(self.rotation_speed)
        else:
            self.power_on = False
            self._shutdown_fan()

    def set_rotation_speed(self, value):
        self.rotation_speed = value
        self._set_speed(value)

    def _shutdown_fan(self):
        GPIO.output(SPEED_1_PIN, GPIO.LOW)
        GPIO.output(SPEED_2_PIN, GPIO.LOW)
        GPIO.output(SPEED_3_PIN, GPIO.LOW)

    def _set_speed(self, value):
        if value == 0:
            self._shutdown_fan()
        elif value <= 33:
            self._set_fan_speed_1()
        elif 33 < value <= 66:
            self._set_fan_speed_2()
        else:
            self._set_fan_speed_3()

    def _set_fan_speed_1(self):
        GPIO.output(SPEED_1_PIN, GPIO.HIGH)
        GPIO.output(SPEED_2_PIN, GPIO.LOW)
        GPIO.output(SPEED_3_PIN, GPIO.LOW)

    def _set_fan_speed_2(self):
        GPIO.output(SPEED_1_PIN, GPIO.LOW)
        GPIO.output(SPEED_2_PIN, GPIO.HIGH)
        GPIO.output(SPEED_3_PIN, GPIO.LOW)

    def _set_fan_speed_3(self):
        GPIO.output(SPEED_1_PIN, GPIO.LOW)
        GPIO.output(SPEED_2_PIN, GPIO.LOW)
        GPIO.output(SPEED_3_PIN, GPIO.HIGH)

    def _set_services(self):
        """Add the fan service. Also add optional characteristics to it."""
        super(Fan, self)._set_services()
        service_loader = loader.get_serv_loader()
        fan_service = service_loader.get("Fan")

        # On/Off
        fan_service.get_characteristic("On").setter_callback = self.set_fan

        # Add the optional RotationSpeed characteristic to the Fan
        rotation_speed_char = loader.get_char_loader().get("RotationSpeed")
        fan_service.add_opt_characteristic(rotation_speed_char)
        rotation_speed_char.setter_callback = self.set_rotation_speed

        self.add_service(fan_service)
