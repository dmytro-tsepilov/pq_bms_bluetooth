# PowerQueen LiFePO4 BMS Bluetooth
Python library for PowerQueen LiFePO4 batteries with BMS Bluetooth connection.
Main purpose is to read battery stats from BMS.

> [!NOTE]  
> The code does not make any changes or change any settings in BMS of battery. Only reading information.

> [!WARNING]  
> **This is unofficial PowerQueen library. Use at your own risk.**  

## Installation

Clone and create python virtual environment

```
git clone https://github.com/dmytro-tsepilov/pq_bms_bluetooth.git
cd pq_bms_bluetooth
python -m venv venv
source venv/bin/activate
```

Install requirements

```
pip install -r requirements.txt
```

## Usage

Find the Bluetooth MAC address of your battery.
On linux it is possible with the `bluez` tool.

```
sudo apt install bluez
```

Start bluetooth tool:\
`bluetoothctl`

Scan for available bluetooth devices:\
 `scan on`

Once it finds some devices and shows the list, stop scanning with command:\
`scan off`

> [!NOTE]  
> There is no need to *Trust*, *Pair* or *Connect* to battery via `bluez`. Just find the MAC address of the battery.

<span style="color:blue">[bluetooth]</span># scan on
<br>Discovery started
<br>[<span style="color:yellow">CHG</span>] Controller 12:34:56:78:AA:CC Discovering: yes
<br>[<span style="color:green">NEW</span>] Device 12:34:56:78:CC:12 Some Sound Device etc.
<br>[<span style="color:green">NEW</span>] Device 12:34:56:78:29:CF P-12100BXXX77-A00123
<br>[<span style="color:green">NEW</span>] Device 12:34:56:78:F8:7C 12-33-44-55-F8-7C
<br>[<span style="color:green">NEW</span>] Device 12:34:56:78:D4:3D 33-44-55-EE-D4-3D
<br><span style="color:blue">[bluetooth]</span># scan off

## CLI

```
# python main.py --help
usage: main.py [-h] [--bms] [--timeout TIMEOUT] [--pair] [-s] [--verbose] DEVICE_MAC

positional arguments:
  DEVICE_MAC         Bluetooth device MAC address in format 12:34:56:78:AA:CC

options:
  -h, --help         show this help message and exit
  --bms              Get battery BMS info
  --timeout TIMEOUT  Bluetooth response timeout in seconds (default: 4)
  --pair             Pair with device before interacting
  -s, --services     List device GATT services and characteristics
  --verbose          Verbose logs
```

### Examples

Get BMS information
```
# python main.py 12:34:56:78:AA:CC --bms
{
    "packVoltage": 12793,
    "voltage": 13338,
    "batteryPack": {
        "1": 3.335,
        "2": 3.335,
        "3": 3.335,
        "4": 3.333
    },
    "current": 15.04,
    "watt": 189.435,
    "remianAh": 105.0,
    "factoryAh": 105.0,
    "cellTemperature": 25,
    "mosfetTemperature": 26,
    "heat": [
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0",
        "0"
    ],
    "protectState": [
        0,
        0,
        0,
        0
    ],
    "failureState": [
        0,
        0,
        0,
        0
    ],
    "equilibriumState": 0,
    "batteryState": 1,
    "SOC": "100%",
    "SOH": "105%",
    "dischargeSwitchState": 0,
    "dischargesCount": 3,
    "dischargesAHCount": 101,
    "firmwareVersion": "1.4.0",
    "manfactureDate": "1980-01-01",
    "hardwareVersion": "T12345678",
    "battery_status": "Charging",
    "balance_status": "All cells are well-balanced.",
    "cell_status": "Battery is in optimal working condition.",
    "bms_status": null,
    "heat_status": null,
    "error_code": 0,
    "error_message": null
}
```

<br><br>
List device GATT services and characteristics
```
# python main.py 12:34:56:78:AA:CC --services
```

## Tested on

Software:
- Python 3.10, 3.11
- Linux Ubuntu 22.04
- Raspberry Pi OS Debian 12 (bookworm) (kernel 6.6+)

Hardware:
- Power Queen LiFePO4 12V 100Ah

## Community tested

Hardware:
- Power Queen LiFePO4 25.6V 100Ah

## Support and donation

- PayPal: dimon.freeman@gmail.com
- Tether (USDT): TUvCxN29Vj5GRVdq4655XaTa9nBNhw6dug
