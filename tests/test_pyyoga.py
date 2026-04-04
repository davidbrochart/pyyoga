import pytest
from pyyoga import (
    Node,
    Config,
    YogaValue,
    Align,
    Direction,
    Edge,
    FlexDirection,
    Gutter,
    Justify,
    Overflow,
    PositionType,
    Unit,
    Wrap,
    Display,
    UNDEFINED,
    float_is_undefined,
)


class TestNodeCreation:
    def test_create_node(self):
        node = Node()
        assert node is not None

    def test_create_node_with_config(self):
        config = Config()
        node = Node(config=config)
        assert node is not None

    def test_clone_node(self):
        node = Node()
        node.width = 100
        cloned = node.clone()
        assert cloned is not node
        assert cloned.width.value == 100


class TestConfig:
    def test_default_config(self):
        config = Config.default()
        assert config is not None

    def test_custom_config(self):
        config = Config(use_web_defaults=True)
        assert config.use_web_defaults is True

    def test_point_scale_factor(self):
        config = Config()
        config.point_scale_factor = 2.0
        assert config.point_scale_factor == 2.0


class TestFlexDirection:
    def test_column(self):
        node = Node()
        node.flex_direction = FlexDirection.Column
        assert node.flex_direction == FlexDirection.Column

    def test_row(self):
        node = Node()
        node.flex_direction = FlexDirection.Row
        assert node.flex_direction == FlexDirection.Row


class TestJustifyContent:
    def test_center(self):
        node = Node()
        node.justify_content = Justify.Center
        assert node.justify_content == Justify.Center

    def test_space_between(self):
        node = Node()
        node.justify_content = Justify.SpaceBetween
        assert node.justify_content == Justify.SpaceBetween


class TestAlignItems:
    def test_center(self):
        node = Node()
        node.align_items = Align.Center
        assert node.align_items == Align.Center

    def test_stretch(self):
        node = Node()
        node.align_items = Align.Stretch
        assert node.align_items == Align.Stretch


class TestDimensions:
    def test_set_width_height(self):
        node = Node()
        node.width = 100
        node.height = 200
        assert node.width.value == 100
        assert node.height.value == 200

    def test_width_unit(self):
        node = Node()
        node.width = 100
        assert node.width.unit == Unit.Point

    def test_percent_width(self):
        node = Node()
        node.width = 50  # This sets points
        # Check that we can read it back
        assert node.width.value == 50


class TestFlex:
    def test_flex_grow(self):
        node = Node()
        node.flex_grow = 1.0
        assert node.flex_grow == 1.0

    def test_flex_shrink(self):
        node = Node()
        node.flex_shrink = 2.0
        assert node.flex_shrink == 2.0


class TestMargin:
    def test_set_margin(self):
        node = Node()
        node.set_margin(Edge.All, 10)
        assert node.get_margin(Edge.All).value == 10

    def test_set_margin_auto(self):
        node = Node()
        node.set_margin_auto(Edge.All)
        margin = node.get_margin(Edge.All)
        assert margin.unit == Unit.Auto


class TestPadding:
    def test_set_padding(self):
        node = Node()
        node.set_padding(Edge.All, 15)
        assert node.get_padding(Edge.All).value == 15


class TestChildren:
    def test_add_child(self):
        parent = Node()
        child = Node()
        parent.add_child(child)
        assert parent.child_count == 1
        assert child.parent is parent

    def test_remove_child(self):
        parent = Node()
        child = Node()
        parent.add_child(child)
        parent.remove_child(child)
        assert parent.child_count == 0
        assert child.parent is None

    def test_remove_all_children(self):
        parent = Node()
        for _ in range(3):
            parent.add_child(Node())
        parent.remove_all_children()
        assert parent.child_count == 0


class TestLayout:
    def test_basic_layout(self):
        root = Node()
        root.width = 100
        root.height = 100
        root.calculate_layout()
        assert root.layout_width == 100
        assert root.layout_height == 100

    def test_child_layout(self):
        root = Node()
        root.width = 100
        root.height = 100

        child = Node()
        child.width = 50
        child.height = 50
        root.add_child(child)

        root.calculate_layout()

        assert child.layout_width == 50
        assert child.layout_height == 50
        assert child.layout_left == 0
        assert child.layout_top == 0

    def test_flex_grow_layout(self):
        root = Node()
        root.width = 100
        root.height = 100
        root.flex_direction = FlexDirection.Column

        child = Node()
        child.flex_grow = 1.0
        root.add_child(child)

        root.calculate_layout()

        assert abs(child.layout_height - 100) < 0.01

    def test_align_items_center(self):
        root = Node()
        root.width = 100
        root.height = 100
        root.align_items = Align.Center

        child = Node()
        child.width = 50
        child.height = 50
        root.add_child(child)

        root.calculate_layout()

        # Child should be centered horizontally
        assert abs(child.layout_left - 25) < 0.01

    def test_justify_content_center(self):
        root = Node()
        root.width = 100
        root.height = 100
        root.flex_direction = FlexDirection.Column
        root.justify_content = Justify.Center

        child = Node()
        child.width = 50
        child.height = 50
        root.add_child(child)

        root.calculate_layout()

        # Child should be centered vertically
        assert abs(child.layout_top - 25) < 0.01

    def test_rtl_direction(self):
        root = Node()
        root.width = 100
        root.height = 100
        root.flex_direction = FlexDirection.Row

        child = Node()
        child.width = 50
        child.height = 50
        root.add_child(child)

        root.calculate_layout(direction=Direction.RTL)

        # In RTL, child should be on the right side
        assert abs(child.layout_left - 50) < 0.01

    def test_layout_with_constraints(self):
        root = Node()
        root.flex_direction = FlexDirection.Column
        root.flex_grow = 1.0

        child = Node()
        child.width = 50
        child.height = 50
        root.add_child(child)

        root.calculate_layout(width=200, height=200)

        assert root.layout_width == 200
        assert root.layout_height == 200


class TestPosition:
    def test_absolute_position(self):
        root = Node()
        root.width = 100
        root.height = 100

        child = Node()
        child.position_type = PositionType.Absolute
        child.set_position(Edge.Left, 10)
        child.set_position(Edge.Top, 20)
        child.width = 50
        child.height = 50
        root.add_child(child)

        root.calculate_layout()

        assert abs(child.layout_left - 10) < 0.01
        assert abs(child.layout_top - 20) < 0.01


class TestOverflow:
    def test_overflow_hidden(self):
        node = Node()
        node.overflow = Overflow.Hidden
        assert node.overflow == Overflow.Hidden


class TestDisplay:
    def test_display_none(self):
        root = Node()
        root.width = 100
        root.height = 100

        child = Node()
        child.display = getattr(Display, "None")
        child.width = 50
        child.height = 50
        root.add_child(child)

        root.calculate_layout()

        assert child.layout_width == 0
        assert child.layout_height == 0


class TestGap:
    def test_set_gap(self):
        node = Node()
        node.set_gap(Gutter.All, 10)
        assert node.get_gap(Gutter.All) == 10


class TestAspectRatio:
    def test_set_aspect_ratio(self):
        node = Node()
        node.aspect_ratio = 2.0
        assert node.aspect_ratio == 2.0


class TestYogaValue:
    def test_points(self):
        val = YogaValue.points(100)
        assert val.value == 100
        assert val.is_point()

    def test_percent(self):
        val = YogaValue.percent(50)
        assert val.value == 50
        assert val.is_percent()

    def test_auto(self):
        val = YogaValue.auto()
        assert val.is_auto()

    def test_undefined(self):
        val = YogaValue.undefined()
        assert val.is_undefined()


class TestFloatIsUndefined:
    def test_undefined(self):
        assert float_is_undefined(UNDEFINED) is True

    def test_defined(self):
        assert float_is_undefined(100.0) is False


class TestComplexLayout:
    def test_nested_flex(self):
        """Test a nested flex layout similar to a real UI."""
        root = Node()
        root.width = 300
        root.height = 400
        root.flex_direction = FlexDirection.Column
        root.set_padding(Edge.All, 16)

        header = Node()
        header.height = 50
        header.set_margin(Edge.Bottom, 10)
        root.add_child(header)

        content = Node()
        content.flex_grow = 1.0
        content.flex_direction = FlexDirection.Row
        content.set_gap(Gutter.All, 10)
        root.add_child(content)

        sidebar = Node()
        sidebar.width = 80
        content.add_child(sidebar)

        main = Node()
        main.flex_grow = 1.0
        content.add_child(main)

        footer = Node()
        footer.height = 40
        footer.set_margin(Edge.Top, 10)
        root.add_child(footer)

        root.calculate_layout()

        # Verify layout
        assert abs(root.layout_width - 300) < 0.01
        assert abs(root.layout_height - 400) < 0.01
        assert abs(header.layout_height - 50) < 0.01
        assert abs(footer.layout_height - 40) < 0.01
        # Content should fill remaining space: 400 - 50 - 40 - 10 - 10 - 16*2 = 258
        assert abs(content.layout_height - 258) < 0.01
        # Sidebar should be 80 wide
        assert abs(sidebar.layout_width - 80) < 0.01
        # Main should fill remaining: 300 - 16*2 - 10 - 80 = 178
        assert abs(main.layout_width - 178) < 0.01


class TestMeasureFunc:
    def test_measure_func(self):
        """Test that a custom measure function is called during layout."""
        root = Node()
        root.width = 200
        root.height = 200
        root.flex_direction = FlexDirection.Column
        root.align_items = Align.FlexStart

        child = Node()

        def measure(width, width_mode, height, height_mode):
            return (80.0, 60.0)

        child.set_measure_func(measure)
        assert child.has_measure_func()

        root.add_child(child)
        root.calculate_layout()

        assert abs(child.layout_width - 80) < 0.01
        assert abs(child.layout_height - 60) < 0.01

    def test_measure_func_respects_constraints(self):
        """Test that measure func receives correct constraints."""
        root = Node()
        root.width = 100
        root.height = 100

        child = Node()
        constraints_received = {}

        def measure(width, width_mode, height, height_mode):
            constraints_received["width"] = width
            constraints_received["width_mode"] = width_mode
            constraints_received["height"] = height
            constraints_received["height_mode"] = height_mode
            return (50.0, 50.0)

        child.set_measure_func(measure)
        root.add_child(child)
        root.calculate_layout()

        assert constraints_received["width"] == 100
        assert constraints_received["width_mode"] == 1  # Exactly
        assert constraints_received["height"] == 100
        assert constraints_received["height_mode"] == 2  # AtMost

    def test_clear_measure_func(self):
        """Test that measure func can be cleared."""
        node = Node()

        def measure(width, width_mode, height, height_mode):
            return type("Size", (), {"width": 10.0, "height": 10.0})()

        node.set_measure_func(measure)
        assert node.has_measure_func()

        node.set_measure_func(None)
        assert not node.has_measure_func()
