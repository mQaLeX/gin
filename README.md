# GIN - Gdb based INstrumentation framework

## Compared with...
- unicorn/qiling
    - Easier setup
    - Always works
- pin
    - Multiarch support
- frida
    - More stable
- Gdb
    - Less manual work

## Usage
```python
def hook():
    GinCtx.regp.rax

gin = Gin.Local(["...", "arg1", "arg2"])
gin.hook_code(..., hook)
gin.run()
```

## TODO
- [ ] a global database for user data
- [ ] ssh/telnet-attach/run mode
- [ ] module-offset to address
- [ ] support runtime hook
- [ ] support array print