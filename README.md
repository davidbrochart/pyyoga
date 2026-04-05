# pyyoga

[![Tests](https://github.com/davidbrochart/pyyoga/actions/workflows/test.yml/badge.svg)](https://github.com/davidbrochart/pyyoga/actions/workflows/test.yml)

Python bindings for [Facebook Yoga](https://github.com/facebook/yoga) flexbox layout engine.

`pyyoga` provides a high-level, Pythonic interface to the Yoga layout engine, closely following the patterns and ergonomics of the official JavaScript bindings.

## Installation

```bash
pip install pyyoga
```

## Quick Start

```python
from pyyoga import Node, FlexDirection, Align, Justify, Edge

# Create a root node
root = Node()
root.width = 300
root.height = 400
root.flex_direction = FlexDirection.Column
root.align_items = Align.Center

# Add a child with percentage dimensions
child = Node()
child.width = "50%"  # String percentage support (JS-like)
child.height = 100
root.add_child(child)

# Calculate layout
root.calculate_layout()

# Read results
print(f"Child position: ({child.layout_left}, {child.layout_top})")
print(f"Child size: {child.layout_width}x{child.layout_height}")

# Computed layout dictionary
print(child.get_computed_layout())
```

## Features

- **JS-Aligned API:** High-level wrapper that mirrors the official JavaScript bindings.
- **Flexible Setters:** Dimensions, margins, and padding accept `float` (points), `str` (e.g., `"50%"`, `"auto"`), or `YogaValue` objects.
- **Full Binding:** Complete access to Yoga v3.2.1 core via `pybind11`.
- **Advanced Features:**
    - Custom **Measure Functions** using Python callables.
    - **Dirtied Callbacks** to track layout invalidation.
    - **Baseline Alignment** with reference baseline support.
- **Modern CI/CD:** Cross-platform wheels (Linux, macOS, Windows) and automated PyPI publishing.

## Building from Source

Requirements:
- Python 3.10+
- C++20 compiler (GCC 11+, Clang 14+, MSVC 19.29+)
- CMake 3.18+

```bash
pip install scikit-build-core pybind11 setuptools-scm
pip install .
```

## Running Tests

```bash
pip install pytest
pytest
```

## License

MIT
