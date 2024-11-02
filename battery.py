import json
import asyncio
import logging
from request import Request

class BatteryInfo:
    '''
    Class parse BMS information from PowerQueen LiFePO4 battery over bluetooth

    Attributes:
        logger (str): Instance of python logger.
    '''
    BMS_CHARACTERISTIC_ID = '0000FFE1-0000-1000-8000-00805F9B34FB' ## Bluetooth characteristic for BMS data
    SN_CHARACTERISTIC_ID = "0000FFE2-0000-1000-8000-00805F9B34FB" ## characteristic for reading serial number (seems not implemented)

    pq_commands = {
        'GET_VERSION'      : '00 00 04 01 16 55 AA 1A',
        'GET_BATTERY_INFO' : '00 00 04 01 13 55 AA 17',
        ## Native application does not read internal serial number.
        ## On version 1.1.4 used SN from QR code, during adding battery
        'SERIAL_NUMBER'    : '00 00 04 01 10 55 AA 14'
    }

    def __init__(self, bluetooth_device_mac: str, pair_device: bool=False, logger=None):
        self.packVoltage = None
        self.voltage = None
        self.batteryPack: dict = {}
        self.current = None
        self.watt = None
        self.remainAh = None
        self.factoryAh = None
        self.cellTemperature = None
        self.mosfetTemperature = None
        self.heat = None
        self.protectState = None
        self.failureState = None
        self.equilibriumState = None
        self.batteryState = None
        self.SOC = None
        self.SOH = None
        self.dischargesCount = None
        self.dischargesAHCount = None

        self.firmwareVersion = None
        self.manfactureDate = None
        self.hardwareVersion = None

        ## Human readable battery status
        self.battery_status = None
        self.balance_status = None
        self.cell_status = None
        self.bms_status = None
        self.heat_status = None

        if logger:
            self._logger = logger
        else:
            self._logger = logging.getLogger(__name__)

        self._request = Request(
            bluetooth_device_mac,
            pair_device=pair_device,
            logger=self._logger
        )

    def get_request(self):
        '''
          Return Blutooth request instance
        '''
        return self._request

    def read_bms(self):
        '''
          Function read BMS info via bluetooth using bleak client
        '''
        asyncio.run(self._request.bulk_send(
            characteristic_id = self.BMS_CHARACTERISTIC_ID,
            commands_parsers = {
                self.pq_commands["GET_VERSION"]: self.parse_version,
                self.pq_commands["GET_BATTERY_INFO"]: self.parse_battery_info,
                ## Internal SN not used or not implemented
                ## self.pq_commands["SERIAL_NUMBER"]: self.parse_serial_number
            }
        ))

    def get_json(self):
        '''
          Function return complete JSON string of parsed BMS information
        '''
        state = self.__dict__
        del state['_logger']
        del state['_request']
        state['SOC'] = f"{self.SOC}%"
        state['SOH'] = f"{self.SOH}%"

        return json.dumps(
            state,
            default=lambda o: o.__dict__,
            sort_keys=False,
            indent=4)

    def parse_battery_info(self, data):
        '''
          Parse battery info from bytearray
        '''
        self.packVoltage = int.from_bytes(data[8:12][::-1], byteorder='big')
        self.voltage = int.from_bytes(data[12:16][::-1], byteorder='big')

        cell = 1
        batPack = data[16:48]
        for key, dt in enumerate(batPack):
            if not dt or key % 2:
                continue

            cellVoltage = int.from_bytes([batPack[key + 1], dt], byteorder='big')
            self.batteryPack[cell] = cellVoltage/1000
            cell += 1

        ## Load \ Unload current A
        current = int.from_bytes(data[48:52][::-1], byteorder='big', signed=True)
        self.current = round(current / 1000, 2)

        ## Calculated load \ unload Watt
        self.watt = round((self.voltage * +current) / 10000, 1) / 100

        ## Remain Ah
        remainAh = int.from_bytes(data[62:64][::-1], byteorder='big')
        self.remainAh = round(remainAh/100, 2)

        ## Factory Ah
        fccAh = int.from_bytes(data[64:66][::-1], byteorder='big')
        self.factoryAh = round(fccAh/100, 2)

        ## Temperature
        s = pow(2, 16)
        self.cellTemperature = int.from_bytes(data[52:54][::-1], byteorder='big')
        self.mosfetTemperature = int.from_bytes(data[54:56][::-1], byteorder='big')

        self.heat = list(data[68:72][::-1])

        self.protectState = list(data[76:80][::-1])
        self.failureState = list(data[80:84][::-1])
        self.equilibriumState = int.from_bytes(data[84:88][::-1], byteorder='big')
        self.batteryState = int.from_bytes(data[88:90][::-1], byteorder='big')

        ## Charge level
        self.SOC = int.from_bytes(data[90:92][::-1], byteorder='big')

        ## Battery Status ??
        self.SOH = int.from_bytes(data[92:96][::-1], byteorder='big')

        self.dischargesCount = int.from_bytes(data[96:100][::-1], byteorder='big')

        ## Discharge AH times
        self.dischargesAHCount = int.from_bytes(data[100:104][::-1], byteorder='big')

        ## Additional human readable statuses
        self.battery_status = self.get_battery_status()

        if self.equilibriumState > 0:
            self.balance_status = "Battery cells are being balanced for better performance."
        else:
            self.balance_status = "All cells are well-balanced."

        if self.failureState[0] > 0 or self.failureState[1] > 0:
            self.cell_status = "Fault alert! There may be a problem with cell."
        else:
            self.cell_status = "Battery is in optimal working condition."

        # To fix: Search for bms_status metric
        # if self.failureState[2] > 0:
        #     self.bms_status = "⚠Warning! BMS failure."
        # else:
        #     if self.protectState:
        #         self.bms_status = "Protection mode is on."
        #     else:
        #         self.bms_status = "BMS is running smoothly."


        # To fix: Search for heat metric
        # if self.heat:
        #     self.heat_status = "Self-heating is on"
        # else:
        #     self.heat_status = "Self-heating is off"

    def parse_version(self, data):
        '''
          Parse firmware version from bytearray
        '''
        start = data[8:]
        self.firmwareVersion = (f"{int.from_bytes(start[0:2][::-1], byteorder='big')}"
                                f".{int.from_bytes(start[2:4][::-1], byteorder='big')}"
                                f".{int.from_bytes(start[4:6][::-1], byteorder='big')}")
        self.manfactureDate = (f"{int.from_bytes(start[6:8][::-1], byteorder='big')}"
                               f"-{int(start[8])}"
                               f"-{int(start[9])}")

        vers = ""
        #rawV = data[0:8]
        for ver in start[0::2]:
            if 32 <= ver <= 126:
                vers += chr(ver)

        self.hardwareVersion = vers

    def parse_serial_number(self, data):
        '''
          Parse battery serial number from bytearray
          Seems logic not implemented in BMS
        '''
        print(f"Serial number: ${data}")

    def get_battery_status(self) -> str:
        '''
          Return human readable battery status
        '''
        status = ''
        if self.current == 0:
            status = "Standby"
        elif self.current > 0:
            status = "Charging"
        elif self.current < 0:
            status = "Discharging"

        if self.SOC >= 100 or self.batteryState == 4:
            status = "Full Charge"

        return status
