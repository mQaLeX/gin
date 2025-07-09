import inspect
import textwrap
from typing import Dict, Set, List, Tuple, Callable, Self

from .base import GinCfgBase, TAB

class GinCfgCodeHook(GinCfgBase):
    def __init__(self, bp: int):
        super().__init__()

        assert isinstance(bp, int)

        self._bp = bp
        self._callbacks: Dict[str,Tuple[int, str]] = dict()
    
    def add_callback(self, callback: Callable):
        name = callback.__name__
        source = inspect.getsource(callback)

        if name in self._callbacks:
            print('Hook:', name, 'will be covered')
        
        self._callbacks[name] = (len(self._callbacks), source)

    def installed(self):
        rt = super().installed()
        
        callback_list = sorted(self._callbacks.items(), key=lambda tpl: tpl[1][0])

        rt += f'class BP_{self._bp:X}(gdb.Breakpoint):\n'
        for _, tpl in callback_list:
            rt += textwrap.indent('@staticmethod\n', TAB)
            rt += textwrap.indent(textwrap.dedent(tpl[1]), TAB)
        rt += textwrap.indent('def stop(self):\n', TAB)
        rt += textwrap.indent('try:\n', TAB*2)
        for name, _ in callback_list:
            rt += textwrap.indent(f'self.{name}()\n', TAB*3)
        rt += textwrap.indent('except Exception as e:\n', TAB*2)
        rt += textwrap.indent('GinCtrl.stop(e)\n', TAB*3)
        rt += textwrap.indent('return False\n', TAB*2)

        return rt

    def executed(self) -> list:
        rt = super().executed()
        rt.append(f'bp_{self._bp:x} = BP_{self._bp:X}("*{self._bp:#x}")')
        return rt