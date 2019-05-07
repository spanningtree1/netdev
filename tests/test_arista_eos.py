import asyncio
import logging
import unittest

import yaml

import netdev

logging.basicConfig(filename='unittest.log', level=logging.DEBUG)
config_path = 'config.yaml'


class TestArista(unittest.TestCase):
    @staticmethod
    def load_credits():
        with open(config_path, 'r') as conf:
            config = yaml.safe_load(conf)
            with open(config['device_list'], 'r') as devs:
                devices = yaml.safe_load(devs)
                params = [p for p in devices if p['device_type'] == 'arista_eos']
                return params

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        self.loop.set_debug(False)
        asyncio.set_event_loop(self.loop)
        self.devices = self.load_credits()
        self.assertFalse(len(self.devices) == 0)

    def test_show_run_hostname(self):
        async def task():
            for dev in self.devices:
                async with netdev.create(**dev) as arista:
                    out = await arista.send_command('show run | i hostname')
                    self.assertIn("hostname", out)

        self.loop.run_until_complete(task())

    def test_show_several_commands(self):
        async def task():
            for dev in self.devices:
                async with netdev.create(**dev) as arista:
                    commands = ["dir", "show ver", "show run"]
                    for cmd in commands:
                        out = await arista.send_command(cmd, strip_command=False)
                        self.assertIn(cmd, out)

        self.loop.run_until_complete(task())

    def test_config_set(self):
        async def task():
            for dev in self.devices:
                async with netdev.create(**dev) as arista:
                    commands = ["vlan 1", "exit"]
                    out = await arista.send_config_set(commands)
                    self.assertIn("vlan 1", out)
                    self.assertIn("exit", out)

        self.loop.run_until_complete(task())

    def test_base_prompt(self):
        async def task():
            for dev in self.devices:
                async with netdev.create(**dev) as arista:
                    out = await arista.send_command('sh run | i hostname')
                    self.assertIn(arista.base_prompt, out)

        self.loop.run_until_complete(task())

    def test_timeout(self):
        async def task():
            for dev in self.devices:
                with self.assertRaises(netdev.TimeoutError):
                    async with netdev.create(**dev, timeout=0.1) as arista:
                        await arista.send_command('sh run | i hostname')

        self.loop.run_until_complete(task())

    def test_interactive_commands(self):
        async def task():
            for dev in self.devices:
                async with netdev.create(**dev) as arista:
                    out = await arista.send_command("erase startup", pattern=r'\[confirm\]', strip_command=False)
                    out += await arista.send_command("no", strip_command=False)
                    out += await arista.send_command("show startup", strip_command=False)
                    self.assertIn('Startup-config last modified', out)

        self.loop.run_until_complete(task())