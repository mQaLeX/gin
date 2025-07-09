import inspect
from typing import Dict, Set, Tuple, List

TAB = '    '

class GinCfgBase:
    def required(self) -> Tuple[Set[str], Dict[str, Set[str]]]:
        return ({'gdb'}, dict())
    
    def installed(self) -> str:
        return ''
    
    def executed(self) -> list:
        return list()
