from typing import Dict, Set, List, Tuple, Callable, Self

from ..config.code_hook import GinCfgCodeHook

class GinHookMgr:
    def __init__(self):
        self._bps: Dict[int, GinCfgCodeHook] = dict()
    
    def breakpoint(self, bp: int) -> GinCfgCodeHook:
        assert isinstance(bp, int)

        if bp in self._bps:
            return self._bps[bp]
        
        instance = GinCfgCodeHook(bp)
        self._bps[bp] = instance
        return instance
