"""Pythonic wrapper for Facebook Yoga layout engine."""

import math
from typing import Optional, List, Tuple, Any, Callable
from ._pyyoga import (
    Node as _Node,
    Config as _Config,
    Value as _Value,
    UNDEFINED,
    VALUE_AUTO,
    VALUE_UNDEFINED,
    VALUE_ZERO,
    Align,
    BoxSizing,
    Dimension,
    Direction,
    Display,
    Edge,
    FlexDirection,
    Gutter,
    Justify,
    MeasureMode,
    NodeType,
    Overflow,
    PositionType,
    Unit,
    Wrap,
    float_is_undefined,
)


class YogaValue:
    """Represents a dimension value (points, percent, auto, etc.)."""

    __slots__ = ("value", "unit")

    def __init__(self, value: float = 0.0, unit: Unit = Unit.Undefined):
        self.value = value
        self.unit = unit

    @classmethod
    def points(cls, value: float) -> "YogaValue":
        return cls(value, Unit.Point)

    @classmethod
    def percent(cls, value: float) -> "YogaValue":
        return cls(value, Unit.Percent)

    @classmethod
    def auto(cls) -> "YogaValue":
        return cls(0.0, Unit.Auto)

    @classmethod
    def undefined(cls) -> "YogaValue":
        return cls(0.0, Unit.Undefined)

    def is_auto(self) -> bool:
        return self.unit == Unit.Auto

    def is_undefined(self) -> bool:
        return self.unit == Unit.Undefined

    def is_percent(self) -> bool:
        return self.unit == Unit.Percent

    def is_point(self) -> bool:
        return self.unit == Unit.Point

    def __repr__(self) -> str:
        if self.is_auto():
            return "YogaValue.auto()"
        if self.is_undefined():
            return "YogaValue.undefined()"
        if self.is_percent():
            return f"YogaValue.percent({self.value})"
        return f"YogaValue.points({self.value})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, YogaValue):
            return False
        return self.value == other.value and self.unit == other.unit


def _to_yoga_value(val: Optional[float]) -> float:
    """Convert Python value to Yoga float (using NaN for undefined)."""
    if val is None:
        return UNDEFINED
    return val


def _from_yoga_value(yg_val: _Value) -> YogaValue:
    """Convert Yoga YGValue to Python YogaValue."""
    return YogaValue(yg_val.value, yg_val.unit)


class Config:
    """Configuration for Yoga nodes."""

    def __init__(self, use_web_defaults: bool = False):
        self._config = _Config.new()
        self._config.set_use_web_defaults(use_web_defaults)

    @classmethod
    def default(cls) -> "Config":
        """Get the default config (not owned, do not free)."""
        config = object.__new__(cls)
        config._config = _Config.get_default()
        return config

    @property
    def use_web_defaults(self) -> bool:
        return self._config.get_use_web_defaults()

    @use_web_defaults.setter
    def use_web_defaults(self, value: bool):
        self._config.set_use_web_defaults(value)

    @property
    def point_scale_factor(self) -> float:
        return self._config.get_point_scale_factor()

    @point_scale_factor.setter
    def point_scale_factor(self, value: float):
        self._config.set_point_scale_factor(value)

    @property
    def errata(self) -> int:
        return self._config.get_errata()

    @errata.setter
    def errata(self, value: int):
        self._config.set_errata(value)

    def set_experimental_feature(self, feature, enabled: bool):
        self._config.set_experimental_feature_enabled(feature, enabled)

    def is_experimental_feature_enabled(self, feature) -> bool:
        return self._config.is_experimental_feature_enabled(feature)


class Node:
    """A Yoga layout node."""

    def __init__(self, config: Optional[Config] = None):
        if config is not None:
            self._node = _Node.new_with_config(config._config)
        else:
            self._node = _Node.new()
        self._children: List[Node] = []
        self._parent: Optional[Node] = None
        self._measure_func: Optional[Callable] = None

    @property
    def parent(self) -> Optional["Node"]:
        return self._parent

    @property
    def children(self) -> List["Node"]:
        return list(self._children)

    @property
    def child_count(self) -> int:
        return self._node.get_child_count()

    def add_child(self, child: "Node", index: Optional[int] = None):
        if child._parent is not None:
            child._parent.remove_child(child)
        if index is not None:
            self._node.insert_child(child._node, index)
            self._children.insert(index, child)
        else:
            self._node.insert_child(child._node, len(self._children))
            self._children.append(child)
        child._parent = self

    def remove_child(self, child: "Node"):
        self._node.remove_child(child._node)
        if child in self._children:
            self._children.remove(child)
        child._parent = None

    def remove_all_children(self):
        self._node.remove_all_children()
        for child in self._children:
            child._parent = None
        self._children.clear()

    def clone(self) -> "Node":
        new_node = object.__new__(Node)
        new_node._node = self._node.clone()
        new_node._children = []
        new_node._parent = None
        new_node._measure_func = None
        return new_node

    def reset(self):
        self._node.reset()
        self._children.clear()
        self._parent = None

    def calculate_layout(
        self,
        width: Optional[float] = None,
        height: Optional[float] = None,
        direction: Direction = Direction.LTR,
    ):
        self._node.calculate_layout(
            _to_yoga_value(width),
            _to_yoga_value(height),
            direction,
        )

    def mark_dirty(self):
        self._node.mark_dirty()

    @property
    def is_dirty(self) -> bool:
        return self._node.is_dirty()

    @property
    def has_new_layout(self) -> bool:
        return self._node.get_has_new_layout()

    @has_new_layout.setter
    def has_new_layout(self, value: bool):
        self._node.set_has_new_layout(value)

    @property
    def layout_left(self) -> float:
        return self._node.get_layout_left()

    @property
    def layout_top(self) -> float:
        return self._node.get_layout_top()

    @property
    def layout_right(self) -> float:
        return self._node.get_layout_right()

    @property
    def layout_bottom(self) -> float:
        return self._node.get_layout_bottom()

    @property
    def layout_width(self) -> float:
        return self._node.get_layout_width()

    @property
    def layout_height(self) -> float:
        return self._node.get_layout_height()

    @property
    def layout_direction(self) -> Direction:
        return self._node.get_layout_direction()

    @property
    def layout_had_overflow(self) -> bool:
        return self._node.get_layout_had_overflow()

    def layout_margin(self, edge: Edge) -> float:
        return self._node.get_layout_margin(edge)

    def layout_border(self, edge: Edge) -> float:
        return self._node.get_layout_border(edge)

    def layout_padding(self, edge: Edge) -> float:
        return self._node.get_layout_padding(edge)

    # Style properties

    @property
    def flex_direction(self) -> FlexDirection:
        return self._node.get_flex_direction()

    @flex_direction.setter
    def flex_direction(self, value: FlexDirection):
        self._node.set_flex_direction(value)

    @property
    def justify_content(self) -> Justify:
        return self._node.get_justify_content()

    @justify_content.setter
    def justify_content(self, value: Justify):
        self._node.set_justify_content(value)

    @property
    def align_items(self) -> Align:
        return self._node.get_align_items()

    @align_items.setter
    def align_items(self, value: Align):
        self._node.set_align_items(value)

    @property
    def align_self(self) -> Align:
        return self._node.get_align_self()

    @align_self.setter
    def align_self(self, value: Align):
        self._node.set_align_self(value)

    @property
    def align_content(self) -> Align:
        return self._node.get_align_content()

    @align_content.setter
    def align_content(self, value: Align):
        self._node.set_align_content(value)

    @property
    def position_type(self) -> PositionType:
        return self._node.get_position_type()

    @position_type.setter
    def position_type(self, value: PositionType):
        self._node.set_position_type(value)

    @property
    def flex_wrap(self) -> Wrap:
        return self._node.get_flex_wrap()

    @flex_wrap.setter
    def flex_wrap(self, value: Wrap):
        self._node.set_flex_wrap(value)

    @property
    def overflow(self) -> Overflow:
        return self._node.get_overflow()

    @overflow.setter
    def overflow(self, value: Overflow):
        self._node.set_overflow(value)

    @property
    def display(self) -> Display:
        return self._node.get_display()

    @display.setter
    def display(self, value: Display):
        self._node.set_display(value)

    @property
    def flex(self) -> float:
        return self._node.get_flex()

    @flex.setter
    def flex(self, value: float):
        self._node.set_flex(value)

    @property
    def flex_grow(self) -> float:
        return self._node.get_flex_grow()

    @flex_grow.setter
    def flex_grow(self, value: float):
        self._node.set_flex_grow(value)

    @property
    def flex_shrink(self) -> float:
        return self._node.get_flex_shrink()

    @flex_shrink.setter
    def flex_shrink(self, value: float):
        self._node.set_flex_shrink(value)

    @property
    def flex_basis(self) -> YogaValue:
        return _from_yoga_value(self._node.get_flex_basis())

    @flex_basis.setter
    def flex_basis(self, value: float):
        self._node.set_flex_basis(value)

    @property
    def width(self) -> YogaValue:
        return _from_yoga_value(self._node.get_width())

    @width.setter
    def width(self, value: float):
        self._node.set_width(value)

    @property
    def height(self) -> YogaValue:
        return _from_yoga_value(self._node.get_height())

    @height.setter
    def height(self, value: float):
        self._node.set_height(value)

    @property
    def min_width(self) -> YogaValue:
        return _from_yoga_value(self._node.get_min_width())

    @min_width.setter
    def min_width(self, value: float):
        self._node.set_min_width(value)

    @property
    def min_height(self) -> YogaValue:
        return _from_yoga_value(self._node.get_min_height())

    @min_height.setter
    def min_height(self, value: float):
        self._node.set_min_height(value)

    @property
    def max_width(self) -> YogaValue:
        return _from_yoga_value(self._node.get_max_width())

    @max_width.setter
    def max_width(self, value: float):
        self._node.set_max_width(value)

    @property
    def max_height(self) -> YogaValue:
        return _from_yoga_value(self._node.get_max_height())

    @max_height.setter
    def max_height(self, value: float):
        self._node.set_max_height(value)

    def set_position(self, edge: Edge, value: float):
        self._node.set_position(edge, value)

    def set_position_percent(self, edge: Edge, value: float):
        self._node.set_position_percent(edge, value)

    def set_position_auto(self, edge: Edge):
        self._node.set_position_auto(edge)

    def get_position(self, edge: Edge) -> YogaValue:
        return _from_yoga_value(self._node.get_position(edge))

    def set_margin(self, edge: Edge, value: float):
        self._node.set_margin(edge, value)

    def set_margin_percent(self, edge: Edge, value: float):
        self._node.set_margin_percent(edge, value)

    def set_margin_auto(self, edge: Edge):
        self._node.set_margin_auto(edge)

    def get_margin(self, edge: Edge) -> YogaValue:
        return _from_yoga_value(self._node.get_margin(edge))

    def set_padding(self, edge: Edge, value: float):
        self._node.set_padding(edge, value)

    def set_padding_percent(self, edge: Edge, value: float):
        self._node.set_padding_percent(edge, value)

    def get_padding(self, edge: Edge) -> YogaValue:
        return _from_yoga_value(self._node.get_padding(edge))

    def set_border(self, edge: Edge, value: float):
        self._node.set_border(edge, value)

    def get_border(self, edge: Edge) -> float:
        return self._node.get_border(edge)

    def set_gap(self, gutter: Gutter, value: float):
        self._node.set_gap(gutter, value)

    def set_gap_percent(self, gutter: Gutter, value: float):
        self._node.set_gap_percent(gutter, value)

    def get_gap(self, gutter: Gutter) -> float:
        return self._node.get_gap(gutter)

    @property
    def aspect_ratio(self) -> float:
        return self._node.get_aspect_ratio()

    @aspect_ratio.setter
    def aspect_ratio(self, value: float):
        self._node.set_aspect_ratio(value)

    @property
    def direction(self) -> Direction:
        return self._node.get_direction()

    @direction.setter
    def direction(self, value: Direction):
        self._node.set_direction(value)

    @property
    def box_sizing(self) -> BoxSizing:
        return self._node.get_box_sizing()

    @box_sizing.setter
    def box_sizing(self, value: BoxSizing):
        self._node.set_box_sizing(value)

    @property
    def node_type(self) -> NodeType:
        return self._node.get_node_type()

    @node_type.setter
    def node_type(self, value: NodeType):
        self._node.set_node_type(value)

    def set_measure_func(
        self,
        func: Optional[Callable[[float, int, float, int], Tuple[float, float]]],
    ):
        self._measure_func = func
        if func is not None:

            def adapter(width, width_mode, height, height_mode):
                return func(width, width_mode, height, height_mode)

            self._measure_adapter = adapter
            self._node.set_measure_func(adapter)
        else:
            self._measure_adapter = None
            self._node.set_measure_func(None)

    def has_measure_func(self) -> bool:
        return self._node.has_measure_func()

    def __repr__(self) -> str:
        return (
            f"<Node {self.layout_width:.1f}x{self.layout_height:.1f} "
            f"at ({self.layout_left:.1f}, {self.layout_top:.1f})>"
        )


__all__ = [
    "Node",
    "Config",
    "YogaValue",
    "UNDEFINED",
    "VALUE_AUTO",
    "VALUE_UNDEFINED",
    "VALUE_ZERO",
    "Align",
    "BoxSizing",
    "Dimension",
    "Direction",
    "Display",
    "Edge",
    "FlexDirection",
    "Gutter",
    "Justify",
    "MeasureMode",
    "NodeType",
    "Overflow",
    "PositionType",
    "Unit",
    "Wrap",
    "float_is_undefined",
]
