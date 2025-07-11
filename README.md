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
    GinLog.reg('rax', GinCtx.rax)

gin = Gin.Local(["...", "arg1", "arg2"])
gin.hook_code(..., hook)
gin.run()
```