import asyncio
import logging
from typing import Callable
from bleak import BleakClient, BleakGATTCharacteristic


class Request:
    def __init__(self,
                 bluetooth_device_mac: str,
                 pair_device: bool = False,
                 timeout: int = 2,
                 logger=None):
        self.bluetooth_device_mac = bluetooth_device_mac
        self.pair = pair_device
        self.callback_func = None
        self.bluetooth_timeout = timeout

        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)

    async def send(self, characteristic_id: str, command: str, callback_func: Callable) -> None:
        '''
          Send single command to device
        '''
        await self.bulk_send(characteristic_id, commands_parsers={ command: callback_func })

    async def bulk_send(self, characteristic_id: str, commands_parsers: dict) -> None:
        '''
          Bulk send commands to device
        '''
        self.logger.info("Connecting to %s... (timeout: %s)", self.bluetooth_device_mac, self.bluetooth_timeout)
        async with BleakClient(self.bluetooth_device_mac, timeout=self.bluetooth_timeout) as client:
            if self.pair:
                self.logger.info("Pairing %s...", self.bluetooth_device_mac)
                await client.pair()

            for commandStr, parser in commands_parsers.items():
                command = self._create_command(commandStr)
                self.callback_func = parser

                await client.start_notify(characteristic_id, self._data_callback)
                self.logger.info("Sending command: %s", command)
                result = await client.write_gatt_char(characteristic_id, data=command, response=True)
                await asyncio.sleep(1.0)

                self.logger.info("Raw result: %s", result)
                await client.stop_notify(characteristic_id)

        self.logger.info("Disconnecting %s...", self.bluetooth_device_mac)
        if self.pair:
            client.unpair()
        await client.disconnect()
        self.logger.info("Disconnected %s", self.bluetooth_device_mac)


    async def print_services(self):
        '''
          Print bluetooth device serivces and characteristics
        '''
        async with BleakClient(self.bluetooth_device_mac, timeout=self.bluetooth_timeout) as client:
            if self.pair:
                self.logger.info("Pairing %s...", self.bluetooth_device_mac)
                await client.pair()
            await self.parse_services(client, client.services)

        self.logger.info("Disconnecting %s...", self.bluetooth_device_mac)
        if self.pair:
            await client.unpair()
        await client.disconnect()
        self.logger.info("Disconnected %s", self.bluetooth_device_mac)

    async def parse_services(self, client, services):
        '''
          Parse and print bleak serivces and characteristics
        '''
        for service in services:
            print(service)
            for charc in service.characteristics:
                print(f"\tcharacteristic: ${charc}")
                try:
                    result = await client.read_gatt_char(charc)
                    print(f"\t{result}")
                    ## print("Model Number: {0}".format("".join(map(chr, model_number))))
                except Exception as e:
                    print(f"\tError: {e}")

    def _set_callback(self, callback_func: Callable) -> None:
        self.callback_func = callback_func

    def _create_command(self, command: str) -> bytearray:
        '''
          Conver string of hex numbers to bytearray BMS command
        '''
        command_bytes = [int(el, 16) for el in command.split(" ")]
        message_bytes = bytearray(command_bytes)

        return message_bytes

    async def _data_callback(self, sender: BleakGATTCharacteristic, data: bytearray):
        self.logger.info("Function: %s\n characteristic_id: %s\n Raw data: %s",
                         self.callback_func.__name__, sender, data)
        self.callback_func(data)
