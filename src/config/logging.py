import inspect
import sys
import traceback

from .base import GinCfgBase
from .mockgdb import gdb

class GinLog:
    def __init__(self, log_fn: str = None, std: bool = True):
        self.log_fn = log_fn
        self.std = True if log_fn is None else std

    def syserror(self, e: Exception):
        tb_list = traceback.extract_tb(e.__traceback__)

        chain_str = ' -> '.join(tb.line for tb in tb_list)
        self._base_print('ERROR', 'magenta', f"{chain_str}: {e}")
    
    def syswarn(self, content: str):
        self._base_print('WARN', 'yellow', content)

    def sysdone(self):
        self._base_print('DONE', 'cyan', "Exec Done")

    def fail(self, content: str):
        self._base_print('x', 'red', content)

    def success(self, content: str):
        self._base_print('-', 'green', content)

    def info(self, content: str):
        self._base_print('*', 'blue', content)

    def reg(self, name: str, value: int):
        self.info(f'{name}: {value:#x}')

    def addr(self, name: str, addr: int):
        self.info(f'{name} addr: {addr:#x}')

    def string(self, name: str, s: bytes):
        self.info(f'{name}: {s}')
    
    def hexdump(self, name: str, s: bytes):
        self.info(f'{name}: {s.hex()}')

    def _colored(self, text, color, bold = False) -> str:
        colors = {
            "default": "0",
            "red": "31",
            "green": "32",
            "yellow": "33",
            "blue": "34",
            "magenta": "35",
            "cyan": "36",
            "white": "37"
        }
        color_code = colors.get(color, "0")
        prefix = "\033[1;" if bold else "\033["
        suffix = "\033[0m"
        return f"{prefix}{color_code}m{text}{suffix}"  

    def _base_print(self, prefix: str, color: str, content: str):
        if self.std:
            print(f"[{self._colored(prefix, color)}] {content}", file=sys.stderr)  
        
        if self.log_fn is not None:
            with open(self.log_fn, 'a') as log_f:
                log_f.write(f"[{prefix}] {content}\n")

class GinCfgLog(GinCfgBase):
    def required(self):
        x, y = super().required()
        return x | {'sys', 'traceback'}, y
    
    def installed(self):
        return super().installed() + \
                inspect.getsource(GinLog)
