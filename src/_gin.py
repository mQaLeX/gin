from typing import Callable, Dict, List, Set, Tuple
from enum import Enum

from .config.code_hook import GinCfgCodeHook
from .config.context import GinCfgContext
from .config.logging import GinCfgLog
from .config.control import GinCfgCtrlLocal, GinCfgCtrlRemote
from .manager.process import GinLocalProcMgr, GinRemoteProcMgr
from .manager.config import GinCfgMgr
from .manager.hook import GinHookMgr

class GinMode(Enum):
    LOCAL = 0
    REMOTE = 1

class Gin:
    def __init__(self, gdb_path: str, mode: GinMode, **kwargs):
        self.mode = mode
        self._hook_mgr = GinHookMgr()
        
        if mode == GinMode.LOCAL:
            target_argv = kwargs['target_argv']
            
            self._proc_mgr = GinLocalProcMgr(gdb_path, target_argv)
            self._cfg_mgr = GinCfgMgr(GinCfgCtrlLocal())
        elif mode == GinMode.REMOTE:
            ip = kwargs['ip']
            port = kwargs['port']
            arch = kwargs['arch']

            self._proc_mgr = GinRemoteProcMgr(gdb_path, ip, port, arch)
            self._cfg_mgr = GinCfgMgr(GinCfgCtrlRemote())
        else:
            raise NotImplementedError()
        
        self._cfg_mgr.add_cfg_items([GinCfgContext(), 
                                     GinCfgLog()])
               
    @classmethod
    def Local(cls, target_argv, gdb_path: str = "gdb"):
        return cls(gdb_path=gdb_path, mode=GinMode.LOCAL, target_argv=target_argv)

    @classmethod
    def Remote(cls, ip, port, arch, gdb_path: str = "gdb"):
        return cls(gdb_path=gdb_path, mode=GinMode.REMOTE, ip=ip, port=port, arch=arch)
    
    def code_hook(self, addr: int, callback: Callable):
        hook = self._hook_mgr.breakpoint(addr)
        hook.add_callback(callback)
        
        self._cfg_mgr.add_cfg_item(hook)

    def mem_hook(self):
        raise NotImplementedError()

    def run(self):
        py_init_path = self._cfg_mgr.gen_py_init()
        self._proc_mgr.add_py_init(py_init_path)
        return self._proc_mgr.run()