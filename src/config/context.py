import inspect

from .base import GinCfgBase
from .logging import GinLog
from .mockgdb import gdb

class GinCtxItem:
    def __init__(self, log: bool = False):
        self._log = log

class GinMemory(GinCtxItem):
    def _hexdump(self, base: int, data: bytes, width: int = 16):
        data_len = len(data)

        start_offset = base - (base % width)
        end_offset = base + data_len

        GinLog.info("-"*28 + f" Hexdump: {base:#018x} " + "-"*28)
        header = '                  ' + ' '.join(f'{i:02x}' for i in range(width))
        GinLog.info(header)

        for offset in range(start_offset, end_offset, width):
            hex_bytes = []
            ascii_chars = []

            for i in range(width):
                addr = offset + i
                data_index = addr - base
                if 0 <= data_index < data_len:
                    byte = data[data_index]
                    hex_bytes.append(f'{byte:02x}')
                    ascii_chars.append(chr(byte) if 32 <= byte <= 126 else '.')
                else:
                    hex_bytes.append('  ')
                    ascii_chars.append(' ')

            hex_part = ' '.join(hex_bytes)
            ascii_part = ''.join(ascii_chars)

            GinLog.info(f'{offset:016x}  {hex_part}  |{ascii_part}|')
        GinLog.info("-"*85)

    def _string(self, base: int, data: bytes):
        GinLog.info(f'{base:016x}: {data}')

    def __getitem__(self, index):
        assert isinstance(index, slice)

        addr = index.start
        length = index.stop - index.start
        step = index.step

        rt = bytes(gdb.selected_inferior().read_memory(addr, length))
        if self._log:
            if step is None:
                self._string(addr, rt)
            else:
                self._hexdump(addr, rt)
        return rt

class GinSymbol(GinCtxItem):
    def __getitem__(self, name):
        if isinstance(name, bytes):
            name = name.decode()
        else:
            name = str(name)
        
        symbol = gdb.lookup_global_symbol(name)
        if symbol is None:
            GinLog.syswarn(f"No symbol {name}")
            return None
        
        rt = int(symbol.value().address)
        if self._log:
            GinLog.info(f'&({name}) = {rt:#x}')
        return rt

class GinRegister(GinCtxItem):
    def __getattr__(self, name):
        rt = int(gdb.parse_and_eval(f'${name}'))
        if self._log:
            GinLog.info(f'${name}: {rt:#x}')
        return rt

class GinCtx:
    mem = GinMemory()
    sym = GinSymbol()
    reg = GinRegister()
    memp = GinMemory(True)
    symp = GinSymbol(True)
    regp = GinRegister(True)

class GinCfgContext(GinCfgBase):
    def installed(self) -> str:
        return super().installed() + \
                inspect.getsource(GinCtxItem) + \
                inspect.getsource(GinMemory) + \
                inspect.getsource(GinSymbol) + \
                inspect.getsource(GinRegister) + \
                inspect.getsource(GinCtx)

        
    