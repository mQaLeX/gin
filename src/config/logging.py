import inspect
import sys
import traceback

from datetime import datetime

from .base import GinCfgBase
from .mockgdb import gdb

class GinLog:
    std = True
    log_fn = None

    def sysfail(e: Exception):
        tb_list = traceback.extract_tb(e.__traceback__)

        chain_str = ' -> '.join(tb.line for tb in tb_list)
        GinLog._console_print('SYS_FAIL', 'magenta', f"{chain_str}: {e}")
    
    def sysinfo(content: str):
        GinLog._console_print('SYS_INFO', 'cyan', content)

    def syswarn(content: str):
        GinLog._console_print('SYS_WARN', 'yellow', content)

    def fail(content: str):
        GinLog._mix_print('FAIL', 'red', content)

    def success(content: str):
        GinLog._mix_print('SUCC', 'green', content)

    def info(content: str):
        GinLog._mix_print('INFO', 'blue', content)

    def reg(name: str, value: int):
        GinLog.info(f'{name}: {value:#x}')

    def addr(name: str, addr: int):
        GinLog.info(f'{name} addr: {addr:#x}')

    def string(name: str, s: bytes):
        GinLog.info(f'{name}: {s}')
    
    def hexdump(name: str, s: bytes):
        GinLog.info(f'{name}: {s.hex()}')

    def _colored(text, color, bold = False) -> str:
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

    def _console_print(prefix: str, color: str, content: str):
        if GinLog.std:
            print(f"[{GinLog._colored(prefix, color)}] {content}", file=sys.stderr)

    def _file_print(prefix: str, content: str):
        if GinLog.log_fn is not None:
            with open(GinLog.log_fn, 'a') as log_f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]
                log_f.write(f"{timestamp} - {prefix} - {content}\n")

    def _mix_print(prefix: str, color: str, content: str):
        GinLog._console_print(prefix, color, content)
        GinLog._file_print(prefix, content)

class GinCfgLog(GinCfgBase):
    def __init__(self, filename: str = None, std: bool = True):
        super().__init__()
        self.filename = filename
        self.std = std if filename is not None else True
    
    def __repr__(self):
        return f"({self.filename}, {self.std})"
    
    def required(self):
        x, y = super().required()
        x.update({'sys', 'traceback'})
        y.update({'datetime': {'datetime'}})
        return x, y
    
    def installed(self):
        return super().installed() + \
                inspect.getsource(GinLog)

    def executed(self):
        rt = super().executed()
        rt.append(f"GinLog.std = \"{self.std}\"")
        rt.append(f"GinLog.log_fn = \"{self.filename}\"")
        return rt