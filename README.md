## Hardware preparations

This has only been tested on a Raspberry Pi 1 Model B using latest Raspbian as
of time of writing.

The door lock is opened by raising a single pin. The GPIO pin on the Raspberry Pi
should be defined as `GPIO_PIN_DOOR`. Pins are counted with the [wiringPi scheme][1] and
by default set to 0 ([physical pin #11](https://pinout.xyz/pinout/pin11_gpio17))

[Lookup table for all Raspberry Pi GPIO pins](https://pinout.xyz/)

## Installing

    # apt install wiringpi
    # curl -sSfo /usr/bin/opendoor <link to opendoor script>

## Usage

    $ GPIO_PIN_DOOR=0 STAY_UNLOCKED_SEC=3 opendoor

## References

- https://projects.drogon.net/raspberry-pi/wiringpi/the-gpio-utility/
- https://pinout.xyz/pinout/wiringpi
- http://redsymbol.net/articles/bash-exit-traps/

[1]: https://pinout.xyz/pinout/wiringpi
