import asyncio
import pyatv
import re


class ATVKeyboardInput:
    def __init__ (self, device):
        self.device = device
        self.remote = device.remote_control
        self.context = "letters"
        self.contexts = ["letters", "numbers", "symbols"]
        self.clear_count = 30
        self.command_sleep_s = 0.002
        self.active_term = ""
        self.active_index = -1
        self.current_pos = 0
        self.symbols = """`'";:~=*+-_,.?!@#$%^&|/\\()"""

    def get_context(self, c):
        if re.match("[a-z ]", c):
            return "letters"
        elif re.match("[0-9 ]", c):
            return "numbers"
        elif c in self.symbols:
            return "symbols"
        else:
            return "unknown"

    async def rotate_context(self, n=0):
        tn = 30
        if n > 0:
            tn=4
        for a in range(tn):
            await self.remote.left()
            await asyncio.sleep(self.command_sleep_s)
        await self.remote.select()
        await asyncio.sleep(self.command_sleep_s)

        await self.remote.right()
        await self.remote.right()
        await asyncio.sleep(self.command_sleep_s)

        self.contexts = self.contexts[1:] + self.contexts[:1]
        self.context = self.contexts[0]
        self.current_pos = 0

    async def check_context(self, c):
        target_context = self.get_context(c)
        if target_context == "unknown":
            return
        n=0
        while target_context != self.context:
            await self.rotate_context(n)
            n += 1

    def get_offset(self, x):
        if self.context == "letters":
            ov = ord(x) - 97
            if x == " ":
                ov = -1
        elif self.context == "numbers":
            if isinstance(x, int):
                x = chr(x)
            print (type(x))
            ov = ord(x) - 49
            if x == "0":
                ov = 9
            
        elif self.context == "symbols":
            ov = self.symbols.index(x)
        else:
            ov -1
        print (f"get_offset ({x}) = {ov}")
        return ov

    async def clear_search(self, multi=2):
        print (f"delete count={self.clear_count*multi}")
        for a in range(self.clear_count):
            await self.remote.right()
            await asyncio.sleep(self.command_sleep_s)
        for a in range(self.clear_count*multi):
            await self.remote.select()
            await asyncio.sleep(self.command_sleep_s)
        for a in range(self.clear_count):
            await self.remote.left()
            await asyncio.sleep(self.command_sleep_s)
        
        await self.remote.right()
        await self.remote.right()
        

    async def find_pos(self, target_pos):
        while self.current_pos != target_pos:
            if self.current_pos < target_pos:
                await self.remote.right()
                self.current_pos += 1
            elif self.current_pos > target_pos:
                await self.remote.left()
                self.current_pos -= 1
            await asyncio.sleep(self.command_sleep_s)
        
        await self.remote.select()

    async def next_key(self, c):
        print (f"next_key({c})")
        await self.check_context(c)
        target_pos = self.get_offset(c)
        await self.find_pos(target_pos)

    async def search(self, term):
        term = term.lower()
        print (f"search({term})")
        self.active_index = 0
        self.active_term = term
        for i, c in enumerate(self.active_term):
            self.active_index = i
            await self.next_key(c)