import inspect

from .base import GinCfgBase
from .logging import GinLog
from .mockgdb import gdb

class GinCtrl:
    @staticmethod
    def stop(e: Exception):
        if e is None:
            GinLog().sysdone()
            retcode = 0
        else:
            GinLog().syserror(e)
            retcode = 1
        
        gdb.execute(f"quit {retcode}")

class GinCfgCtrl(GinCfgBase):
    def installed(self):
        return super().installed() + \
                inspect.getsource(GinCtrl)

class GinCfgCtrlLocal(GinCfgCtrl):
    def executed(self):
        rt = super().executed()
        rt.append("gdb.execute('run')")
        return rt

class GinCfgCtrlRemote(GinCfgCtrl):
    def executed(self):
        rt = super().executed()
        rt.append("gdb.execute('continue')")
        return rt