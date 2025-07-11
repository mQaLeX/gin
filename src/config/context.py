import inspect

from .base import GinCfgBase
from .logging import GinLog
from .mockgdb import gdb

class Memory:
    def __getitem__(self, index):
        assert isinstance(index, slice)

        addr = index.start
        length = index.stop - index.start
        
        assert index.step is None or index.step == 1

        return bytes(gdb.selected_inferior().read_memory(addr, length))

class Symbol:
    def __getitem__(self, name):
        if isinstance(name, bytes):
            name = name.decode()
        else:
            name = str(name)
        
        symbol = gdb.lookup_global_symbol(name)
        if symbol is None:
            GinLog.syswarn(f"No symbol {name}")
            return None
        
        return int(symbol.value().address)

class MetaGinCtx(type):
    def __getattr__(cls, name):
        return int(gdb.parse_and_eval(f'${name}'))

class GinCtx(metaclass=MetaGinCtx):
    mem = Memory()
    sym = Symbol()

class GinCfgContext(GinCfgBase):
    def installed(self) -> str:
        return super().installed() + \
                inspect.getsource(Memory) + \
                inspect.getsource(Symbol) + \
                inspect.getsource(MetaGinCtx) + \
                inspect.getsource(GinCtx)

        
    