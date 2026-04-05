from pyyoga import Node, Align, Direction

def test_new_layout_can_be_marked_seen():
    root = Node()
    root.mark_layout_seen()
    assert root.has_new_layout is False

def test_new_layout_calculating_layout_marks_layout_as_unseen():
    root = Node()
    root.mark_layout_seen()
    root.calculate_layout()
    assert root.has_new_layout is True

def test_new_layout_calculated_layout_can_be_marked_seen():
    root = Node()
    root.calculate_layout()
    root.mark_layout_seen()
    assert root.has_new_layout is False

def test_new_layout_recalculating_layout_does_mark_as_unseen():
    root = Node()
    root.calculate_layout()
    root.mark_layout_seen()
    root.calculate_layout()
    assert root.has_new_layout is True

def test_new_layout_reset_also_resets_layout_seen():
    root = Node()
    root.mark_layout_seen()
    root.reset()
    assert root.has_new_layout is True

def test_new_layout_children_sets_new_layout():
    root = Node()
    root.align_items = Align.FlexStart
    root.width = 100
    root.height = 100

    root_child0 = Node()
    root_child0.align_items = Align.FlexStart
    root_child0.width = 50
    root_child0.height = 20
    root.add_child(root_child0, 0)

    root_child1 = Node()
    root_child1.align_items = Align.FlexStart
    root_child1.width = 50
    root_child1.height = 20
    root.add_child(root_child1, 0)

    assert root.has_new_layout is True
    assert root_child0.has_new_layout is True
    assert root_child1.has_new_layout is True

    root.mark_layout_seen()
    root_child0.mark_layout_seen()
    root_child1.mark_layout_seen()

    assert root.has_new_layout is False
    assert root_child0.has_new_layout is False
    assert root_child1.has_new_layout is False

    root_child1.height = 30
    root.calculate_layout()

    assert root.has_new_layout is True
    # In Yoga, if a child's layout hasn't changed, it might still be marked as having a new layout 
    # if its parent was recalculated. Let's see what happens.
    assert root_child0.has_new_layout is True
    assert root_child1.has_new_layout is True
