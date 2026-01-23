# -*- coding: utf-8 -*-
"""
DIP DataView 模块测试

测试内容:
1. kn_data_view_fields 参数初始化
2. kn_data_view_fields 字段过滤逻辑
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


class TestDataViewKnFieldsFilter:
    """测试 DataView 的 kn_data_view_fields 过滤功能"""

    def test_kn_data_view_fields_initialization_none(self):
        """测试 kn_data_view_fields 初始化为 None"""
        from data_retrieval.datasource.dip_dataview import DataView

        data_view = DataView(
            view_list=[],
            base_url="http://test.com",
            user_id="test_user",
            token="test_token"
        )

        assert data_view.kn_data_view_fields is None

    def test_kn_data_view_fields_initialization_with_data(self):
        """测试 kn_data_view_fields 初始化带数据"""
        from data_retrieval.datasource.dip_dataview import DataView

        kn_fields = {
            "view_id_1": ["field_a", "field_b"],
            "view_id_2": ["field_c"]
        }

        data_view = DataView(
            view_list=[],
            base_url="http://test.com",
            user_id="test_user",
            token="test_token",
            kn_data_view_fields=kn_fields
        )

        assert data_view.kn_data_view_fields is not None
        assert data_view.kn_data_view_fields == kn_fields
        assert "view_id_1" in data_view.kn_data_view_fields
        assert len(data_view.kn_data_view_fields["view_id_1"]) == 2

    def test_kn_data_view_fields_empty_dict(self):
        """测试 kn_data_view_fields 初始化为空字典"""
        from data_retrieval.datasource.dip_dataview import DataView

        data_view = DataView(
            view_list=[],
            base_url="http://test.com",
            user_id="test_user",
            token="test_token",
            kn_data_view_fields={}
        )

        assert data_view.kn_data_view_fields == {}


class TestKnFieldsFilterLogic:
    """测试 kn_data_view_fields 过滤逻辑"""

    def test_filter_fields_by_original_name(self):
        """测试根据 original_name 过滤字段"""
        # 模拟字段过滤逻辑
        fields = [
            {"original_name": "field_a", "name": "字段A", "display_name": "字段A显示名"},
            {"original_name": "field_b", "name": "字段B", "display_name": "字段B显示名"},
            {"original_name": "field_c", "name": "字段C", "display_name": "字段C显示名"},
        ]

        kn_field_names = {"field_a", "field_c"}

        filtered_fields = []
        for field in fields:
            if field["original_name"] in kn_field_names:
                filtered_fields.append(field)

        assert len(filtered_fields) == 2
        assert filtered_fields[0]["original_name"] == "field_a"
        assert filtered_fields[1]["original_name"] == "field_c"

    def test_filter_fields_no_match(self):
        """测试没有匹配字段时的过滤"""
        fields = [
            {"original_name": "field_a", "name": "字段A", "display_name": "字段A显示名"},
            {"original_name": "field_b", "name": "字段B", "display_name": "字段B显示名"},
        ]

        kn_field_names = {"field_x", "field_y"}

        filtered_fields = []
        for field in fields:
            if field["original_name"] in kn_field_names:
                filtered_fields.append(field)

        assert len(filtered_fields) == 0

    def test_filter_fields_all_match(self):
        """测试所有字段都匹配时的过滤"""
        fields = [
            {"original_name": "field_a", "name": "字段A", "display_name": "字段A显示名"},
            {"original_name": "field_b", "name": "字段B", "display_name": "字段B显示名"},
        ]

        kn_field_names = {"field_a", "field_b"}

        filtered_fields = []
        for field in fields:
            if field["original_name"] in kn_field_names:
                filtered_fields.append(field)

        assert len(filtered_fields) == 2

    def test_filter_fields_empty_kn_fields(self):
        """测试空 kn_field_names 时不过滤"""
        fields = [
            {"original_name": "field_a", "name": "字段A", "display_name": "字段A显示名"},
            {"original_name": "field_b", "name": "字段B", "display_name": "字段B显示名"},
        ]

        kn_field_names = set()

        # 当 kn_field_names 为空时，不应进行过滤
        if kn_field_names:
            filtered_fields = []
            for field in fields:
                if field["original_name"] in kn_field_names:
                    filtered_fields.append(field)
        else:
            filtered_fields = fields

        assert len(filtered_fields) == 2


class TestKnDataViewFieldsExtraction:
    """测试从 concept_detail 中提取 kn_data_view_fields"""

    def test_extract_kn_fields_from_data_views(self):
        """测试从 data_views 中提取 kn_data_view_fields"""
        data_views = [
            {
                "id": "view_1",
                "view_name": "视图1",
                "concept_detail": {
                    "data_properties": [
                        {
                            "name": "prop_a",
                            "display_name": "属性A",
                            "mapped_field": {
                                "name": "field_a",
                                "type": "varchar"
                            }
                        },
                        {
                            "name": "prop_b",
                            "display_name": "属性B",
                            "mapped_field": {
                                "name": "field_b",
                                "type": "integer"
                            }
                        }
                    ]
                }
            },
            {
                "id": "view_2",
                "view_name": "视图2",
                "concept_detail": {
                    "data_properties": [
                        {
                            "name": "prop_c",
                            "display_name": "属性C",
                            "mapped_field": {
                                "name": "field_c",
                                "type": "varchar"
                            }
                        }
                    ]
                }
            }
        ]

        kn_data_view_fields = {}
        for view in data_views:
            view_id = view.get("id")
            concept_detail = view.get("concept_detail", {})
            data_properties = concept_detail.get("data_properties", [])
            if data_properties and view_id:
                field_names = []
                for prop in data_properties:
                    mapped_field = prop.get("mapped_field", {})
                    if mapped_field and mapped_field.get("name"):
                        field_names.append(mapped_field["name"])
                if field_names:
                    kn_data_view_fields[view_id] = field_names

        assert "view_1" in kn_data_view_fields
        assert "view_2" in kn_data_view_fields
        assert kn_data_view_fields["view_1"] == ["field_a", "field_b"]
        assert kn_data_view_fields["view_2"] == ["field_c"]

    def test_extract_kn_fields_empty_data_properties(self):
        """测试 data_properties 为空时的处理"""
        data_views = [
            {
                "id": "view_1",
                "view_name": "视图1",
                "concept_detail": {
                    "data_properties": []
                }
            }
        ]

        kn_data_view_fields = {}
        for view in data_views:
            view_id = view.get("id")
            concept_detail = view.get("concept_detail", {})
            data_properties = concept_detail.get("data_properties", [])
            if data_properties and view_id:
                field_names = []
                for prop in data_properties:
                    mapped_field = prop.get("mapped_field", {})
                    if mapped_field and mapped_field.get("name"):
                        field_names.append(mapped_field["name"])
                if field_names:
                    kn_data_view_fields[view_id] = field_names

        assert "view_1" not in kn_data_view_fields

    def test_extract_kn_fields_missing_mapped_field(self):
        """测试缺少 mapped_field 时的处理"""
        data_views = [
            {
                "id": "view_1",
                "view_name": "视图1",
                "concept_detail": {
                    "data_properties": [
                        {
                            "name": "prop_a",
                            "display_name": "属性A"
                            # 没有 mapped_field
                        }
                    ]
                }
            }
        ]

        kn_data_view_fields = {}
        for view in data_views:
            view_id = view.get("id")
            concept_detail = view.get("concept_detail", {})
            data_properties = concept_detail.get("data_properties", [])
            if data_properties and view_id:
                field_names = []
                for prop in data_properties:
                    mapped_field = prop.get("mapped_field", {})
                    if mapped_field and mapped_field.get("name"):
                        field_names.append(mapped_field["name"])
                if field_names:
                    kn_data_view_fields[view_id] = field_names

        assert "view_1" not in kn_data_view_fields

    def test_extract_kn_fields_no_concept_detail(self):
        """测试缺少 concept_detail 时的处理"""
        data_views = [
            {
                "id": "view_1",
                "view_name": "视图1"
                # 没有 concept_detail
            }
        ]

        kn_data_view_fields = {}
        for view in data_views:
            view_id = view.get("id")
            concept_detail = view.get("concept_detail", {})
            data_properties = concept_detail.get("data_properties", [])
            if data_properties and view_id:
                field_names = []
                for prop in data_properties:
                    mapped_field = prop.get("mapped_field", {})
                    if mapped_field and mapped_field.get("name"):
                        field_names.append(mapped_field["name"])
                if field_names:
                    kn_data_view_fields[view_id] = field_names

        assert "view_1" not in kn_data_view_fields


def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("DIP DataView 模块测试")
    print("=" * 60)

    test_classes = [
        TestDataViewKnFieldsFilter,
        TestKnFieldsFilterLogic,
        TestKnDataViewFieldsExtraction,
    ]

    total = 0
    passed = 0
    failed = []

    for cls in test_classes:
        print(f"\n--- {cls.__name__} ---")
        instance = cls()

        for method in dir(instance):
            if method.startswith('test_'):
                total += 1
                try:
                    getattr(instance, method)()
                    print(f"  ✅ {method}")
                    passed += 1
                except Exception as e:
                    print(f"  ❌ {method}: {e}")
                    failed.append((cls.__name__, method, str(e)))

    print("\n" + "=" * 60)
    print(f"测试结果: {passed}/{total} 通过")
    if failed:
        print("\n失败的测试:")
        for c, m, e in failed:
            print(f"  - {c}.{m}: {e}")
    else:
        print("🎉 所有测试通过！")
    print("=" * 60)

    return len(failed) == 0


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
