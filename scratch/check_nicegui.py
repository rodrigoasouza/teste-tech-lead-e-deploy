from nicegui import ui

inp = ui.input()
print(f"Has on_change: {hasattr(inp, 'on_change')}")
print(f"Has on_value_change: {hasattr(inp, 'on_value_change')}")
print(f"Methods: {[m for m in dir(inp) if 'change' in m]}")
