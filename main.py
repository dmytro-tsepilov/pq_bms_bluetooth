import sys
import asyncio
import logging
import argparse
from battery import BatteryInfo

def commands():
    parser = argparse.ArgumentParser()
    parser.add_argument("DEVICE_MAC",
                        help="Bluetooth device MAC address in format 12:34:56:78:AA:CC",
                        type=str)

    parser.add_argument("--bms", help="Get battery BMS info", action="store_true")
    parser.add_argument("-t", "--timeout", help="Bluetooth response timeout in seconds (default: 4)", type=int, default=4)
    parser.add_argument("--pair", help="Pair with device before interacting", action="store_true")
    parser.add_argument("-s", "--services", help="List device GATT services and characteristics", action="store_true")
    parser.add_argument("--verbose", help="Verbose logs", action="store_true")

    args = parser.parse_args()
    return args

def main():
    args = commands()

    logger = None

    if args.verbose:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s [%(funcName)s] %(message)s')
        handler.setFormatter(formatter)
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

    battery = BatteryInfo(args.DEVICE_MAC, args.pair, args.timeout, logger)

    if args.services:
        request = battery.get_request()
        asyncio.run(request.print_services())
        sys.exit(0)

    if args.bms:
        battery.read_bms()
        print(battery.get_json())


if __name__ == "__main__":
    main()
