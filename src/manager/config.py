import textwrap
import tempfile
from typing import Callable, Dict, List, Set, Tuple

from ..config.base import GinCfgBase, TAB
from ..config.logging import GinCfgLog
from ..config.control import GinCfgCtrl

class GinCfgMgr:
    def __init__(self, ctrler: GinCfgCtrl):
        self.ctrler = ctrler

        self.config_set: Set[GinCfgBase] = set()
        self.config_list: List[GinCfgBase] = list()
    
    def add_cfg_item(self, cfg_item: GinCfgBase):
        if cfg_item not in self.config_set:
            self.config_set.add(cfg_item)
            self.config_list.append(cfg_item)

    def add_cfg_items(self, cfg_list: List[GinCfgBase]):
        for cfg_item in cfg_list:
            self.add_cfg_item(cfg_item)

    def _gdb_init_py_content(self) -> str:
        import_set: Set[str] = set()
        from_import_dict: Dict[str, Set[str]] = dict()
        installed = ''
        executed = []

        def py_head():
            rt = ''
            for imp in import_set:
                rt += f'import {imp}\n'
            for frm, imps in from_import_dict.items():
                rt += f'from {frm} import {", ".join(imps)}\n'
            return rt

        def execute_zone():
            return 'if __name__ == "__main__":\n' + \
                    textwrap.indent('try:\n', TAB) + \
                        textwrap.indent('\n'.join(executed) + '\n', TAB*2) + \
                        textwrap.indent('GinCtrl.stop(None)\n', TAB*2) + \
                    textwrap.indent('except Exception as e:\n', TAB) + \
                        textwrap.indent('GinCtrl.stop(e)\n', TAB*2)

        for cfg in self.config_list + [self.ctrler]:
            x, y = cfg.required()
            import_set.update(x)
            from_import_dict.update(y)

            installed += cfg.installed()
            executed += cfg.executed()

        return py_head() + installed + execute_zone()
    
    def _check_necessary(self) -> bool:
        has_log = False
        for cfg_item in self.config_list:
            if isinstance(cfg_item, GinCfgLog):
                has_log = True
        return has_log

    def gen_py_init(self) -> str:
        assert self._check_necessary()

        with tempfile.NamedTemporaryFile(suffix='_gdbinit.py', mode='w', delete=False) as gdb_init_py:
            gdb_init_py.write(self._gdb_init_py_content())
            return gdb_init_py.name