#include <pybind11/functional.h>
#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <yoga/Yoga.h>

#include <mutex>
#include <unordered_map>

namespace py = pybind11;

static std::mutex g_measure_mutex;
static std::unordered_map<YGNodeRef, py::object> g_measure_funcs;

static YGSize measure_adapter(
    YGNodeConstRef node,
    float width,
    YGMeasureMode widthMode,
    float height,
    YGMeasureMode heightMode) {
    py::gil_scoped_acquire acquire;
    std::lock_guard<std::mutex> lock(g_measure_mutex);
    auto it = g_measure_funcs.find(const_cast<YGNodeRef>(node));
    if (it != g_measure_funcs.end()) {
        py::object result = it->second(width, static_cast<int>(widthMode), height, static_cast<int>(heightMode));
        YGSize size;
        if (py::isinstance<py::tuple>(result)) {
            py::tuple t = result.cast<py::tuple>();
            size.width = t[0].cast<float>();
            size.height = t[1].cast<float>();
        } else if (py::hasattr(result, "width") && py::hasattr(result, "height")) {
            size.width = result.attr("width").cast<float>();
            size.height = result.attr("height").cast<float>();
        } else {
            size.width = 0;
            size.height = 0;
        }
        return size;
    }
    YGSize size = {0, 0};
    return size;
}

struct NodeHolder {
    YGNodeRef ptr;
    bool owned;

    NodeHolder() : ptr(YGNodeNew()), owned(true) {}
    explicit NodeHolder(YGConfigRef config) : ptr(YGNodeNewWithConfig(config)), owned(true) {}
    NodeHolder(YGNodeRef p, bool o) : ptr(p), owned(o) {}
    ~NodeHolder() {
        if (owned && ptr) {
            std::lock_guard<std::mutex> lock(g_measure_mutex);
            g_measure_funcs.erase(ptr);
            YGNodeFree(ptr);
        }
    }
    NodeHolder(const NodeHolder&) = delete;
    NodeHolder& operator=(const NodeHolder&) = delete;
    NodeHolder(NodeHolder&& other) noexcept : ptr(other.ptr), owned(other.owned) {
        other.ptr = nullptr;
        other.owned = false;
    }
    NodeHolder& operator=(NodeHolder&& other) noexcept {
        if (this != &other) {
            if (owned && ptr) YGNodeFree(ptr);
            ptr = other.ptr;
            owned = other.owned;
            other.ptr = nullptr;
            other.owned = false;
        }
        return *this;
    }
};

struct ConfigHolder {
    YGConfigRef ptr;
    bool owned;

    ConfigHolder() : ptr(YGConfigNew()), owned(true) {}
    explicit ConfigHolder(YGConfigConstRef p, bool o) : ptr(const_cast<YGConfigRef>(p)), owned(o) {}
    ~ConfigHolder() {
        if (owned && ptr) {
            YGConfigFree(ptr);
        }
    }
    ConfigHolder(const ConfigHolder&) = delete;
    ConfigHolder& operator=(const ConfigHolder&) = delete;
    ConfigHolder(ConfigHolder&& other) noexcept : ptr(other.ptr), owned(other.owned) {
        other.ptr = nullptr;
        other.owned = false;
    }
    ConfigHolder& operator=(ConfigHolder&& other) noexcept {
        if (this != &other) {
            if (owned && ptr) YGConfigFree(ptr);
            ptr = other.ptr;
            owned = other.owned;
            other.ptr = nullptr;
            other.owned = false;
        }
        return *this;
    }
};

PYBIND11_MODULE(_pyyoga, m) {
    m.doc() = "Python bindings for Facebook Yoga layout engine";

    py::enum_<YGAlign>(m, "Align")
        .value("Auto", YGAlignAuto)
        .value("FlexStart", YGAlignFlexStart)
        .value("Center", YGAlignCenter)
        .value("FlexEnd", YGAlignFlexEnd)
        .value("Stretch", YGAlignStretch)
        .value("Baseline", YGAlignBaseline)
        .value("SpaceBetween", YGAlignSpaceBetween)
        .value("SpaceAround", YGAlignSpaceAround);

    py::enum_<YGBoxSizing>(m, "BoxSizing")
        .value("BorderBox", YGBoxSizingBorderBox)
        .value("ContentBox", YGBoxSizingContentBox);

    py::enum_<YGDimension>(m, "Dimension")
        .value("Width", YGDimensionWidth)
        .value("Height", YGDimensionHeight);

    py::enum_<YGDirection>(m, "Direction")
        .value("Inherit", YGDirectionInherit)
        .value("LTR", YGDirectionLTR)
        .value("RTL", YGDirectionRTL);

    py::enum_<YGDisplay>(m, "Display")
        .value("Flex", YGDisplayFlex)
        .value("None", YGDisplayNone)
        .value("Contents", YGDisplayContents);

    py::enum_<YGEdge>(m, "Edge")
        .value("Left", YGEdgeLeft)
        .value("Top", YGEdgeTop)
        .value("Right", YGEdgeRight)
        .value("Bottom", YGEdgeBottom)
        .value("Start", YGEdgeStart)
        .value("End", YGEdgeEnd)
        .value("Horizontal", YGEdgeHorizontal)
        .value("Vertical", YGEdgeVertical)
        .value("All", YGEdgeAll);

    py::enum_<YGFlexDirection>(m, "FlexDirection")
        .value("Column", YGFlexDirectionColumn)
        .value("ColumnReverse", YGFlexDirectionColumnReverse)
        .value("Row", YGFlexDirectionRow)
        .value("RowReverse", YGFlexDirectionRowReverse);

    py::enum_<YGGutter>(m, "Gutter")
        .value("Column", YGGutterColumn)
        .value("Row", YGGutterRow)
        .value("All", YGGutterAll);

    py::enum_<YGJustify>(m, "Justify")
        .value("FlexStart", YGJustifyFlexStart)
        .value("Center", YGJustifyCenter)
        .value("FlexEnd", YGJustifyFlexEnd)
        .value("SpaceBetween", YGJustifySpaceBetween)
        .value("SpaceAround", YGJustifySpaceAround)
        .value("SpaceEvenly", YGJustifySpaceEvenly);

    py::enum_<YGMeasureMode>(m, "MeasureMode")
        .value("Undefined", YGMeasureModeUndefined)
        .value("Exactly", YGMeasureModeExactly)
        .value("AtMost", YGMeasureModeAtMost);

    py::enum_<YGNodeType>(m, "NodeType")
        .value("Default", YGNodeTypeDefault)
        .value("Text", YGNodeTypeText);

    py::enum_<YGOverflow>(m, "Overflow")
        .value("Visible", YGOverflowVisible)
        .value("Hidden", YGOverflowHidden)
        .value("Scroll", YGOverflowScroll);

    py::enum_<YGPositionType>(m, "PositionType")
        .value("Static", YGPositionTypeStatic)
        .value("Relative", YGPositionTypeRelative)
        .value("Absolute", YGPositionTypeAbsolute);

    py::enum_<YGUnit>(m, "Unit")
        .value("Undefined", YGUnitUndefined)
        .value("Point", YGUnitPoint)
        .value("Percent", YGUnitPercent)
        .value("Auto", YGUnitAuto);

    py::enum_<YGWrap>(m, "Wrap")
        .value("NoWrap", YGWrapNoWrap)
        .value("Wrap", YGWrapWrap)
        .value("WrapReverse", YGWrapWrapReverse);

    py::enum_<YGExperimentalFeature>(m, "ExperimentalFeature")
        .value("WebFlexBasis", YGExperimentalFeatureWebFlexBasis);

    py::class_<YGValue>(m, "Value")
        .def(py::init<>())
        .def(py::init<float, YGUnit>(), py::arg("value"), py::arg("unit"))
        .def_readwrite("value", &YGValue::value)
        .def_readwrite("unit", &YGValue::unit)
        .def("__repr__", [](const YGValue& v) {
            return "<YGValue value=" + std::to_string(v.value) + " unit=" + std::to_string(v.unit) + ">";
        });

    m.attr("VALUE_AUTO") = YGValueAuto;
    m.attr("VALUE_UNDEFINED") = YGValueUndefined;
    m.attr("VALUE_ZERO") = YGValueZero;
    m.attr("UNDEFINED") = YGUndefined;

    py::class_<ConfigHolder>(m, "Config")
        .def_static("new", []() {
            return new ConfigHolder();
        })
        .def_static("get_default", []() {
            return new ConfigHolder(YGConfigGetDefault(), false);
        })
        .def("set_use_web_defaults", [](ConfigHolder* self, bool enabled) {
            YGConfigSetUseWebDefaults(self->ptr, enabled);
        })
        .def("get_use_web_defaults", [](ConfigHolder* self) {
            return YGConfigGetUseWebDefaults(self->ptr);
        })
        .def("set_point_scale_factor", [](ConfigHolder* self, float factor) {
            YGConfigSetPointScaleFactor(self->ptr, factor);
        })
        .def("get_point_scale_factor", [](ConfigHolder* self) {
            return YGConfigGetPointScaleFactor(self->ptr);
        })
        .def("set_errata", [](ConfigHolder* self, YGErrata errata) {
            YGConfigSetErrata(self->ptr, errata);
        })
        .def("get_errata", [](ConfigHolder* self) {
            return YGConfigGetErrata(self->ptr);
        })
        .def("set_experimental_feature_enabled",
             [](ConfigHolder* self, YGExperimentalFeature feature, bool enabled) {
                 YGConfigSetExperimentalFeatureEnabled(self->ptr, feature, enabled);
             })
        .def("is_experimental_feature_enabled",
             [](ConfigHolder* self, YGExperimentalFeature feature) {
                 return YGConfigIsExperimentalFeatureEnabled(self->ptr, feature);
             });

    py::class_<NodeHolder>(m, "Node")
        .def_static("new", []() {
            return new NodeHolder();
        })
        .def_static("new_with_config", [](ConfigHolder* config) {
            return new NodeHolder(config->ptr);
        })
        .def("clone", [](NodeHolder* self) {
            return new NodeHolder(YGNodeClone(self->ptr), true);
        })
        .def("free", [](NodeHolder* self) {
            if (self->ptr) {
                YGNodeFree(self->ptr);
                self->ptr = nullptr;
                self->owned = false;
            }
        })
        .def("free_recursive", [](NodeHolder* self) {
            if (self->ptr) {
                YGNodeFreeRecursive(self->ptr);
                self->ptr = nullptr;
                self->owned = false;
            }
        })
        .def("reset", [](NodeHolder* self) {
            YGNodeReset(self->ptr);
        })
        .def("calculate_layout",
             [](NodeHolder* self, float width, float height, YGDirection direction) {
                 YGNodeCalculateLayout(self->ptr, width, height, direction);
             },
             py::arg("width") = YGUndefined,
             py::arg("height") = YGUndefined,
             py::arg("direction") = YGDirectionLTR)
        .def("get_has_new_layout", [](NodeHolder* self) {
            return YGNodeGetHasNewLayout(self->ptr);
        })
        .def("set_has_new_layout", [](NodeHolder* self, bool has_new_layout) {
            YGNodeSetHasNewLayout(self->ptr, has_new_layout);
        })
        .def("is_dirty", [](NodeHolder* self) {
            return YGNodeIsDirty(self->ptr);
        })
        .def("mark_dirty", [](NodeHolder* self) {
            YGNodeMarkDirty(self->ptr);
        })
        .def("insert_child", [](NodeHolder* self, NodeHolder* child, size_t index) {
            YGNodeInsertChild(self->ptr, child->ptr, index);
        })
        .def("remove_child", [](NodeHolder* self, NodeHolder* child) {
            YGNodeRemoveChild(self->ptr, child->ptr);
        })
        .def("remove_all_children", [](NodeHolder* self) {
            YGNodeRemoveAllChildren(self->ptr);
        })
        .def("get_child", [](NodeHolder* self, size_t index) -> NodeHolder* {
            return new NodeHolder(YGNodeGetChild(self->ptr, index), false);
        })
        .def("get_child_count", [](NodeHolder* self) {
            return YGNodeGetChildCount(self->ptr);
        })
        .def("get_parent", [](NodeHolder* self) -> NodeHolder* {
            YGNodeRef parent = YGNodeGetParent(self->ptr);
            if (!parent) return nullptr;
            return new NodeHolder(parent, false);
        })
        .def("set_config", [](NodeHolder* self, ConfigHolder* config) {
            YGNodeSetConfig(self->ptr, config->ptr);
        })
        .def("get_config", [](NodeHolder* self) -> ConfigHolder* {
            return new ConfigHolder(YGNodeGetConfig(self->ptr), false);
        })
        .def("set_node_type", [](NodeHolder* self, YGNodeType node_type) {
            YGNodeSetNodeType(self->ptr, node_type);
        })
        .def("get_node_type", [](NodeHolder* self) {
            return YGNodeGetNodeType(self->ptr);
        })
        .def("set_always_forms_containing_block",
             [](NodeHolder* self, bool always) {
                 YGNodeSetAlwaysFormsContainingBlock(self->ptr, always);
             })
        .def("get_always_forms_containing_block",
             [](NodeHolder* self) {
                 return YGNodeGetAlwaysFormsContainingBlock(self->ptr);
             })
        .def("set_flex_direction", [](NodeHolder* self, YGFlexDirection direction) {
            YGNodeStyleSetFlexDirection(self->ptr, direction);
        })
        .def("set_justify_content", [](NodeHolder* self, YGJustify justify) {
            YGNodeStyleSetJustifyContent(self->ptr, justify);
        })
        .def("set_align_items", [](NodeHolder* self, YGAlign align) {
            YGNodeStyleSetAlignItems(self->ptr, align);
        })
        .def("set_align_self", [](NodeHolder* self, YGAlign align) {
            YGNodeStyleSetAlignSelf(self->ptr, align);
        })
        .def("set_align_content", [](NodeHolder* self, YGAlign align) {
            YGNodeStyleSetAlignContent(self->ptr, align);
        })
        .def("set_position_type", [](NodeHolder* self, YGPositionType position) {
            YGNodeStyleSetPositionType(self->ptr, position);
        })
        .def("set_flex_wrap", [](NodeHolder* self, YGWrap wrap) {
            YGNodeStyleSetFlexWrap(self->ptr, wrap);
        })
        .def("set_overflow", [](NodeHolder* self, YGOverflow overflow) {
            YGNodeStyleSetOverflow(self->ptr, overflow);
        })
        .def("set_display", [](NodeHolder* self, YGDisplay display) {
            YGNodeStyleSetDisplay(self->ptr, display);
        })
        .def("set_flex", [](NodeHolder* self, float flex) {
            YGNodeStyleSetFlex(self->ptr, flex);
        })
        .def("set_flex_grow", [](NodeHolder* self, float grow) {
            YGNodeStyleSetFlexGrow(self->ptr, grow);
        })
        .def("set_flex_shrink", [](NodeHolder* self, float shrink) {
            YGNodeStyleSetFlexShrink(self->ptr, shrink);
        })
        .def("set_flex_basis", [](NodeHolder* self, float basis) {
            YGNodeStyleSetFlexBasis(self->ptr, basis);
        })
        .def("set_flex_basis_percent", [](NodeHolder* self, float basis) {
            YGNodeStyleSetFlexBasisPercent(self->ptr, basis);
        })
        .def("set_flex_basis_auto", [](NodeHolder* self) {
            YGNodeStyleSetFlexBasisAuto(self->ptr);
        })
        .def("set_width", [](NodeHolder* self, float width) {
            YGNodeStyleSetWidth(self->ptr, width);
        })
        .def("set_width_percent", [](NodeHolder* self, float width) {
            YGNodeStyleSetWidthPercent(self->ptr, width);
        })
        .def("set_width_auto", [](NodeHolder* self) {
            YGNodeStyleSetWidthAuto(self->ptr);
        })
        .def("set_height", [](NodeHolder* self, float height) {
            YGNodeStyleSetHeight(self->ptr, height);
        })
        .def("set_height_percent", [](NodeHolder* self, float height) {
            YGNodeStyleSetHeightPercent(self->ptr, height);
        })
        .def("set_height_auto", [](NodeHolder* self) {
            YGNodeStyleSetHeightAuto(self->ptr);
        })
        .def("set_min_width", [](NodeHolder* self, float width) {
            YGNodeStyleSetMinWidth(self->ptr, width);
        })
        .def("set_min_width_percent", [](NodeHolder* self, float width) {
            YGNodeStyleSetMinWidthPercent(self->ptr, width);
        })
        .def("set_min_height", [](NodeHolder* self, float height) {
            YGNodeStyleSetMinHeight(self->ptr, height);
        })
        .def("set_min_height_percent", [](NodeHolder* self, float height) {
            YGNodeStyleSetMinHeightPercent(self->ptr, height);
        })
        .def("set_max_width", [](NodeHolder* self, float width) {
            YGNodeStyleSetMaxWidth(self->ptr, width);
        })
        .def("set_max_width_percent", [](NodeHolder* self, float width) {
            YGNodeStyleSetMaxWidthPercent(self->ptr, width);
        })
        .def("set_max_height", [](NodeHolder* self, float height) {
            YGNodeStyleSetMaxHeight(self->ptr, height);
        })
        .def("set_max_height_percent", [](NodeHolder* self, float height) {
            YGNodeStyleSetMaxHeightPercent(self->ptr, height);
        })
        .def("set_position", [](NodeHolder* self, YGEdge edge, float position) {
            YGNodeStyleSetPosition(self->ptr, edge, position);
        })
        .def("set_position_percent", [](NodeHolder* self, YGEdge edge, float position) {
            YGNodeStyleSetPositionPercent(self->ptr, edge, position);
        })
        .def("set_position_auto", [](NodeHolder* self, YGEdge edge) {
            YGNodeStyleSetPositionAuto(self->ptr, edge);
        })
        .def("set_margin", [](NodeHolder* self, YGEdge edge, float margin) {
            YGNodeStyleSetMargin(self->ptr, edge, margin);
        })
        .def("set_margin_percent", [](NodeHolder* self, YGEdge edge, float margin) {
            YGNodeStyleSetMarginPercent(self->ptr, edge, margin);
        })
        .def("set_margin_auto", [](NodeHolder* self, YGEdge edge) {
            YGNodeStyleSetMarginAuto(self->ptr, edge);
        })
        .def("set_padding", [](NodeHolder* self, YGEdge edge, float padding) {
            YGNodeStyleSetPadding(self->ptr, edge, padding);
        })
        .def("set_padding_percent", [](NodeHolder* self, YGEdge edge, float padding) {
            YGNodeStyleSetPaddingPercent(self->ptr, edge, padding);
        })
        .def("set_border", [](NodeHolder* self, YGEdge edge, float border) {
            YGNodeStyleSetBorder(self->ptr, edge, border);
        })
        .def("set_gap", [](NodeHolder* self, YGGutter gutter, float gap) {
            YGNodeStyleSetGap(self->ptr, gutter, gap);
        })
        .def("set_gap_percent", [](NodeHolder* self, YGGutter gutter, float gap) {
            YGNodeStyleSetGapPercent(self->ptr, gutter, gap);
        })
        .def("set_aspect_ratio", [](NodeHolder* self, float ratio) {
            YGNodeStyleSetAspectRatio(self->ptr, ratio);
        })
        .def("set_direction", [](NodeHolder* self, YGDirection direction) {
            YGNodeStyleSetDirection(self->ptr, direction);
        })
        .def("set_box_sizing", [](NodeHolder* self, YGBoxSizing box_sizing) {
            YGNodeStyleSetBoxSizing(self->ptr, box_sizing);
        })
        .def("get_flex_direction", [](NodeHolder* self) {
            return YGNodeStyleGetFlexDirection(self->ptr);
        })
        .def("get_justify_content", [](NodeHolder* self) {
            return YGNodeStyleGetJustifyContent(self->ptr);
        })
        .def("get_align_items", [](NodeHolder* self) {
            return YGNodeStyleGetAlignItems(self->ptr);
        })
        .def("get_align_self", [](NodeHolder* self) {
            return YGNodeStyleGetAlignSelf(self->ptr);
        })
        .def("get_align_content", [](NodeHolder* self) {
            return YGNodeStyleGetAlignContent(self->ptr);
        })
        .def("get_position_type", [](NodeHolder* self) {
            return YGNodeStyleGetPositionType(self->ptr);
        })
        .def("get_flex_wrap", [](NodeHolder* self) {
            return YGNodeStyleGetFlexWrap(self->ptr);
        })
        .def("get_overflow", [](NodeHolder* self) {
            return YGNodeStyleGetOverflow(self->ptr);
        })
        .def("get_display", [](NodeHolder* self) {
            return YGNodeStyleGetDisplay(self->ptr);
        })
        .def("get_flex", [](NodeHolder* self) {
            return YGNodeStyleGetFlex(self->ptr);
        })
        .def("get_flex_grow", [](NodeHolder* self) {
            return YGNodeStyleGetFlexGrow(self->ptr);
        })
        .def("get_flex_shrink", [](NodeHolder* self) {
            return YGNodeStyleGetFlexShrink(self->ptr);
        })
        .def("get_flex_basis", [](NodeHolder* self) {
            return YGNodeStyleGetFlexBasis(self->ptr);
        })
        .def("get_width", [](NodeHolder* self) {
            return YGNodeStyleGetWidth(self->ptr);
        })
        .def("get_height", [](NodeHolder* self) {
            return YGNodeStyleGetHeight(self->ptr);
        })
        .def("get_min_width", [](NodeHolder* self) {
            return YGNodeStyleGetMinWidth(self->ptr);
        })
        .def("get_min_height", [](NodeHolder* self) {
            return YGNodeStyleGetMinHeight(self->ptr);
        })
        .def("get_max_width", [](NodeHolder* self) {
            return YGNodeStyleGetMaxWidth(self->ptr);
        })
        .def("get_max_height", [](NodeHolder* self) {
            return YGNodeStyleGetMaxHeight(self->ptr);
        })
        .def("get_position", [](NodeHolder* self, YGEdge edge) {
            return YGNodeStyleGetPosition(self->ptr, edge);
        })
        .def("get_margin", [](NodeHolder* self, YGEdge edge) {
            return YGNodeStyleGetMargin(self->ptr, edge);
        })
        .def("get_padding", [](NodeHolder* self, YGEdge edge) {
            return YGNodeStyleGetPadding(self->ptr, edge);
        })
        .def("get_border", [](NodeHolder* self, YGEdge edge) {
            return YGNodeStyleGetBorder(self->ptr, edge);
        })
        .def("get_gap", [](NodeHolder* self, YGGutter gutter) {
            return YGNodeStyleGetGap(self->ptr, gutter);
        })
        .def("get_aspect_ratio", [](NodeHolder* self) {
            return YGNodeStyleGetAspectRatio(self->ptr);
        })
        .def("get_direction", [](NodeHolder* self) {
            return YGNodeStyleGetDirection(self->ptr);
        })
        .def("get_box_sizing", [](NodeHolder* self) {
            return YGNodeStyleGetBoxSizing(self->ptr);
        })
        .def("get_layout_left", [](NodeHolder* self) {
            return YGNodeLayoutGetLeft(self->ptr);
        })
        .def("get_layout_top", [](NodeHolder* self) {
            return YGNodeLayoutGetTop(self->ptr);
        })
        .def("get_layout_right", [](NodeHolder* self) {
            return YGNodeLayoutGetRight(self->ptr);
        })
        .def("get_layout_bottom", [](NodeHolder* self) {
            return YGNodeLayoutGetBottom(self->ptr);
        })
        .def("get_layout_width", [](NodeHolder* self) {
            return YGNodeLayoutGetWidth(self->ptr);
        })
        .def("get_layout_height", [](NodeHolder* self) {
            return YGNodeLayoutGetHeight(self->ptr);
        })
        .def("get_layout_direction", [](NodeHolder* self) {
            return YGNodeLayoutGetDirection(self->ptr);
        })
        .def("get_layout_had_overflow", [](NodeHolder* self) {
            return YGNodeLayoutGetHadOverflow(self->ptr);
        })
        .def("get_layout_margin", [](NodeHolder* self, YGEdge edge) {
            return YGNodeLayoutGetMargin(self->ptr, edge);
        })
        .def("get_layout_border", [](NodeHolder* self, YGEdge edge) {
            return YGNodeLayoutGetBorder(self->ptr, edge);
        })
        .def("get_layout_padding", [](NodeHolder* self, YGEdge edge) {
            return YGNodeLayoutGetPadding(self->ptr, edge);
        })
        .def("set_measure_func", [](NodeHolder* self, py::object func) {
            if (func.is_none()) {
                std::lock_guard<std::mutex> lock(g_measure_mutex);
                g_measure_funcs.erase(self->ptr);
                YGNodeSetMeasureFunc(self->ptr, nullptr);
            } else {
                std::lock_guard<std::mutex> lock(g_measure_mutex);
                g_measure_funcs[self->ptr] = func;
                YGNodeSetMeasureFunc(self->ptr, measure_adapter);
            }
        })
        .def("has_measure_func", [](NodeHolder* self) {
            return YGNodeHasMeasureFunc(self->ptr);
        });

    m.def("float_is_undefined", [](float value) {
        return YGFloatIsUndefined(value);
    });
}
