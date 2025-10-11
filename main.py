import sys
import asyncio
import logging
import argparse
from battery import BatteryInfo


def commands():
    """
    Command line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "DEVICE_MACS",
        help="Comma-separated Bluetooth device MAC addresses (e.g., '12:34:56:78:AA:CC,AA:BB:CC:DD:EE:FF')",
        type=str,
    )

    parser.add_argument("--bms", help="Get battery BMS info", action="store_true")
    parser.add_argument(
        "-t",
        "--timeout",
        help="Bluetooth response timeout in seconds (default: 10)",
        type=int,
        default=10,
    )
    parser.add_argument(
        "--pair", help="Pair with device before interacting", action="store_true"
    )
    parser.add_argument(
        "-s",
        "--services",
        help="List device GATT services and characteristics (only for the first MAC)",
        action="store_true",
    )
    parser.add_argument("--verbose", help="Verbose logs", action="store_true")

    args = parser.parse_args()
    return args

def fetch_all_bms(macs: list, args, logger=None):
    """
    Read bms info for each device
    """
    error_code = 0

    for mac in macs:
        battery = BatteryInfo(mac, args.pair, True, args.timeout, logger)
        battery.read_bms()
        print(battery.get_json())

        if battery.error_code:
            error_code = battery.error_code

    sys.exit(error_code)

def parse_macs(device_macs: str) -> list:
    """
    Parse string of MAC-addresses to list
    """
    if not device_macs:
        return []

    parsed_macs = [mac.strip() for mac in device_macs.split(',') if mac.strip()]
    return parsed_macs

def main():
    args = commands()

    logger = None

    if args.verbose:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("%(asctime)s [%(funcName)s] %(message)s")
        handler.setFormatter(formatter)
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

    macs = parse_macs(args.DEVICE_MACS)

    if not macs:
        print("Error: No device MAC addresses provided.")
        sys.exit(1)

    if args.services:
        first_mac = macs[0]
        print(f"Fetching services for {first_mac}...")
        battery = BatteryInfo(first_mac, args.pair, True, args.timeout, logger)
        request = battery.get_request()
        asyncio.run(request.print_services())
        sys.exit(0)

    if args.bms:
        fetch_all_bms(macs, args, logger)


if __name__ == "__main__":
    main()
