import subprocess
from typing import Dict, Set, Tuple, List
import sys

from ..config.logging import GinLog

class GinProcMgr:
    def __init__(self, gdb_path: str):
        self.head       : List[str] = [gdb_path]
        self.cmd_init   : List[str] = []
        self.py_init    : List[str] = []
        self.tail       : List[str] = []
    
    def add_cmd_init(self, cmd: str):
        self.cmd_init += ['-ex', cmd]

    def add_py_init(self, py_path: str):
        self.py_init += ['-x', py_path]

    def _gdb_argv(self) -> List[str]:
        return self.head + self.cmd_init + self.py_init + self.tail

    def run(self):
        to_run = self._gdb_argv()
        GinLog.sysinfo(f"gdb command: {to_run}")
        proc: subprocess.Popen = None
        try:
            proc = subprocess.Popen(to_run,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=sys.stderr)
            proc.communicate()
        except KeyboardInterrupt:
            if proc is not None:
                proc.kill()
            proc.communicate()
        return None if proc is None else proc.returncode

class GinLocalProcMgr(GinProcMgr):
    def __init__(self, gdb_path: str, target_argv: List[str]):
        super().__init__(gdb_path)
        self.tail += ['--args'] + target_argv
    
class GinRemoteProcMgr(GinProcMgr):
    def __init__(self, gdb_path: str, ip: str, port: int, arch: str):
        super().__init__(gdb_path)
        self.add_cmd_init(f'target remote {ip}:{port}')
        self.add_cmd_init(f'set architecture {arch}')
