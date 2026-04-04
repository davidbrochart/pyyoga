# pyyoga

Python bindings for [Facebook Yoga](https://github.com/facebook/yoga) flexbox layout engine.

## Installation

```bash
pip install .
```

## Quick Start

```python
from pyyoga import Node, FlexDirection, Align, Justify

# Create a root node
root = Node()
root.width = 300
root.height = 400
root.flex_direction = FlexDirection.Column
root.align_items = Align.Center

# Add a child
child = Node()
child.width = 100
child.height = 100
root.add_child(child)

# Calculate layout
root.calculate_layout()

# Read results
print(f"Child position: ({child.layout_left}, {child.layout_top})")
print(f"Child size: {child.layout_width}x{child.layout_height}")
```

## Features

- Full binding to Yoga C++ API via pybind11
- Pythonic wrapper with properties and idiomatic API
- All Yoga enums exposed as Python enums
- Support for custom configurations
- Child management with Python list semantics

## Building from Source

Requirements:
- Python 3.10+
- C++20 compiler
- CMake 3.18+

```bash
pip install scikit-build-core pybind11
pip install -e .
```

## Running Tests

```bash
pip install pytest
pytest tests/
```

## License

MIT
