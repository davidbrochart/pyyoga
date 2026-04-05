import pytest
from pyyoga import Node, YogaValue, Unit, Edge, Gutter

def test_string_percent_width():
    node = Node()
    node.width = "50%"
    assert node.width.unit == Unit.Percent
    assert node.width.value == 50

def test_string_auto_width():
    node = Node()
    node.width = "auto"
    assert node.width.unit == Unit.Auto

def test_yoga_value_width():
    node = Node()
    node.width = YogaValue.percent(25)
    assert node.width.unit == Unit.Percent
    assert node.width.value == 25

def test_copy_style():
    node1 = Node()
    node1.width = 100
    node2 = Node()
    node2.copy_style(node1)
    assert node2.width.value == 100

def test_is_reference_baseline():
    node = Node()
    assert node.is_reference_baseline is False
    node.is_reference_baseline = True
    assert node.is_reference_baseline is True

def test_dirtied_func():
    node = Node()
    node.set_measure_func(lambda w, wm, h, hm: (10, 10))
    node.calculate_layout() # Clean it
    
    dirtied = [False]
    def on_dirtied(n):
        dirtied[0] = True
    
    node.set_dirtied_func(on_dirtied)
    node.mark_dirty()
    assert dirtied[0] is True

def test_computed_layout_aliases():
    node = Node()
    node.width = 100
    node.height = 100
    node.calculate_layout()
    
    assert node.get_computed_width() == 100
    assert node.get_computed_height() == 100
    layout = node.get_computed_layout()
    assert layout["width"] == 100
    assert layout["height"] == 100

def test_set_gap_string():
    node = Node()
    node.set_gap(Gutter.All, "10%")
    assert node.get_gap(Gutter.All) == 10 # get_gap returns float in C++ bindings currently
    # Actually, get_gap in C++ returns float. Yoga says:
    # YG_EXPORT float YGNodeStyleGetGap(YGNodeConstRef node, YGGutter gutter);
    # It doesn't return a YGValue for gap?
    # Let me check Yoga.h for YGNodeStyleGetGap.
