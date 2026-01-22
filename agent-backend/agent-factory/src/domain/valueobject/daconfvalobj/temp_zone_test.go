package daconfvalobj

import (
	"strings"
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/enum/cdaenum"
)

func TestValidate(t *testing.T) {
	// 测试用例：成功验证
	t.Run("Valid Config", func(t *testing.T) {
		maxFileCount := 10
		singleChatMaxSelectFileCount := 3
		config := &TempZoneConfig{
			Name:                         "临时区",
			TmpFileUseType:               cdaenum.TmpFileUseTypeUpload,
			MaxFileCount:                 &maxFileCount,
			SingleChatMaxSelectFileCount: &singleChatMaxSelectFileCount,
			SingleFileSizeLimit:          50,
			SingleFileSizeLimitUnit:      cdaenum.MB,
			SupportDataType:              cdaenum.SupportDataTypes{"file"},
			AllowedFileCategories:        cdaenum.AllowedFileCategories{"document"},
		}

		if err := config.Validate(); err != nil {
			t.Fatalf("预期验证通过，但得到错误: %v", err)
		}
	})

	// 测试用例：TmpFileUseType 缺失
	t.Run("Missing TmpFileUseType", func(t *testing.T) {
		maxFileCount := 10
		singleChatMaxSelectFileCount := 3
		config := &TempZoneConfig{
			Name:                         "临时区",
			MaxFileCount:                 &maxFileCount,
			SingleChatMaxSelectFileCount: &singleChatMaxSelectFileCount,
			SingleFileSizeLimit:          50,
			SingleFileSizeLimitUnit:      cdaenum.MB,
			SupportDataType:              cdaenum.SupportDataTypes{"file"},
			AllowedFileCategories:        cdaenum.AllowedFileCategories{"document"},
		}

		err := config.Validate()
		if err == nil {
			t.Fatal("预期验证失败，但没有得到错误")
		}

		if !strings.Contains(err.Error(), "TmpFileUseType") {
			t.Fatalf("预期错误包含 'TmpFileUseType'，但得到: %v", err)
		}
	})

	// 测试用例：MaxFileCount 超过最大值
	// 注意：Validate()方法只检查required字段，不检查数值范围，所以这个测试应该通过
	t.Run("MaxFileCount Exceeds Maximum", func(t *testing.T) {
		maxFileCount := 51 // 超过最大值50，但Validate()不会检查这个
		singleChatMaxSelectFileCount := 3
		config := &TempZoneConfig{
			Name:                         "临时区",
			TmpFileUseType:               cdaenum.TmpFileUseTypeUpload,
			MaxFileCount:                 &maxFileCount,
			SingleChatMaxSelectFileCount: &singleChatMaxSelectFileCount,
			SingleFileSizeLimit:          50,
			SingleFileSizeLimitUnit:      cdaenum.MB,
			SupportDataType:              cdaenum.SupportDataTypes{"file"},
			AllowedFileCategories:        cdaenum.AllowedFileCategories{"document"},
		}

		err := config.Validate()
		// Validate()只检查required字段，不检查数值范围，所以应该通过
		if err != nil {
			t.Fatalf("预期验证通过，但得到错误: %v", err)
		}
	})

	// 测试用例：MaxFileCount 低于最小值
	// 注意：Validate()方法只检查required字段，不检查数值范围
	t.Run("MaxFileCount Below Minimum", func(t *testing.T) {
		maxFileCount := 0 // 低于最小值1，但Validate()不会检查这个
		singleChatMaxSelectFileCount := 3
		config := &TempZoneConfig{
			Name:                         "临时区",
			TmpFileUseType:               cdaenum.TmpFileUseTypeUpload,
			MaxFileCount:                 &maxFileCount,
			SingleChatMaxSelectFileCount: &singleChatMaxSelectFileCount,
			SingleFileSizeLimit:          50,
			SingleFileSizeLimitUnit:      cdaenum.MB,
			SupportDataType:              cdaenum.SupportDataTypes{"file"},
			AllowedFileCategories:        cdaenum.AllowedFileCategories{"document"},
		}

		err := config.Validate()
		// Validate()只检查required字段，不检查数值范围，所以应该通过
		if err != nil {
			t.Fatalf("预期验证通过，但得到错误: %v", err)
		}
	})

	// 测试用例：SingleChatMaxSelectFileCount 超过最大值
	// 注意：Validate()方法只检查required字段，不检查数值范围
	t.Run("SingleChatMaxSelectFileCount Exceeds Maximum", func(t *testing.T) {
		maxFileCount := 10
		singleChatMaxSelectFileCount := 6 // 超过最大值5，但Validate()不会检查这个
		config := &TempZoneConfig{
			Name:                         "临时区",
			TmpFileUseType:               cdaenum.TmpFileUseTypeUpload,
			MaxFileCount:                 &maxFileCount,
			SingleChatMaxSelectFileCount: &singleChatMaxSelectFileCount,
			SingleFileSizeLimit:          50,
			SingleFileSizeLimitUnit:      cdaenum.MB,
			SupportDataType:              cdaenum.SupportDataTypes{"file"},
			AllowedFileCategories:        cdaenum.AllowedFileCategories{"document"},
		}

		err := config.Validate()
		// Validate()只检查required字段，不检查数值范围，所以应该通过
		if err != nil {
			t.Fatalf("预期验证通过，但得到错误: %v", err)
		}
	})

	// 测试用例：SingleChatMaxSelectFileCount 低于最小值
	// 注意：Validate()方法只检查required字段，不检查数值范围
	t.Run("SingleChatMaxSelectFileCount Below Minimum", func(t *testing.T) {
		maxFileCount := 10
		singleChatMaxSelectFileCount := 0 // 低于最小值1，但Validate()不会检查这个
		config := &TempZoneConfig{
			Name:                         "临时区",
			TmpFileUseType:               cdaenum.TmpFileUseTypeUpload,
			MaxFileCount:                 &maxFileCount,
			SingleChatMaxSelectFileCount: &singleChatMaxSelectFileCount,
			SingleFileSizeLimit:          50,
			SingleFileSizeLimitUnit:      cdaenum.MB,
			SupportDataType:              cdaenum.SupportDataTypes{"file"},
			AllowedFileCategories:        cdaenum.AllowedFileCategories{"document"},
		}

		err := config.Validate()
		// Validate()只检查required字段，不检查数值范围，所以应该通过
		if err != nil {
			t.Fatalf("预期验证通过，但得到错误: %v", err)
		}
	})

	// 测试用例：SingleFileSizeLimit 缺失
	t.Run("Missing SingleFileSizeLimit", func(t *testing.T) {
		maxFileCount := 10
		singleChatMaxSelectFileCount := 3
		config := &TempZoneConfig{
			Name:                         "临时区",
			TmpFileUseType:               cdaenum.TmpFileUseTypeUpload,
			MaxFileCount:                 &maxFileCount,
			SingleChatMaxSelectFileCount: &singleChatMaxSelectFileCount,
			SingleFileSizeLimitUnit:      cdaenum.MB,
			SupportDataType:              cdaenum.SupportDataTypes{"file"},
			AllowedFileCategories:        cdaenum.AllowedFileCategories{"document"},
		}

		err := config.Validate()
		if err == nil {
			t.Fatal("预期验证失败，但没有得到错误")
		}

		if !strings.Contains(err.Error(), "SingleFileSizeLimit") {
			t.Fatalf("预期错误包含 'SingleFileSizeLimit'，但得到: %v", err)
		}
	})

	// 测试用例：SingleFileSizeLimitUnit 缺失
	t.Run("Missing SingleFileSizeLimitUnit", func(t *testing.T) {
		maxFileCount := 10
		singleChatMaxSelectFileCount := 3
		config := &TempZoneConfig{
			Name:                         "临时区",
			TmpFileUseType:               cdaenum.TmpFileUseTypeUpload,
			MaxFileCount:                 &maxFileCount,
			SingleChatMaxSelectFileCount: &singleChatMaxSelectFileCount,
			SingleFileSizeLimit:          50,
			SupportDataType:              cdaenum.SupportDataTypes{"file"},
			AllowedFileCategories:        cdaenum.AllowedFileCategories{"document"},
		}

		err := config.Validate()
		if err == nil {
			t.Fatal("预期验证失败，但没有得到错误")
		}

		if !strings.Contains(err.Error(), "SingleFileSizeLimitUnit") {
			t.Fatalf("预期错误包含 'SingleFileSizeLimitUnit'，但得到: %v", err)
		}
	})

	// 测试用例：SupportDataType 缺失
	t.Run("Missing SupportDataType", func(t *testing.T) {
		maxFileCount := 10
		singleChatMaxSelectFileCount := 3
		config := &TempZoneConfig{
			Name:                         "临时区",
			TmpFileUseType:               cdaenum.TmpFileUseTypeUpload,
			MaxFileCount:                 &maxFileCount,
			SingleChatMaxSelectFileCount: &singleChatMaxSelectFileCount,
			SingleFileSizeLimit:          50,
			SingleFileSizeLimitUnit:      cdaenum.MB,
			AllowedFileCategories:        cdaenum.AllowedFileCategories{"document"},
		}

		err := config.Validate()
		if err == nil {
			t.Fatal("预期验证失败，但没有得到错误")
		}

		if !strings.Contains(err.Error(), "SupportDataType") {
			t.Fatalf("预期错误包含 'SupportDataType'，但得到: %v", err)
		}
	})

	// 测试用例：AllowedFileCategories 缺失
	t.Run("Missing AllowedFileCategories", func(t *testing.T) {
		maxFileCount := 10
		singleChatMaxSelectFileCount := 3
		config := &TempZoneConfig{
			Name:                         "临时区",
			TmpFileUseType:               cdaenum.TmpFileUseTypeUpload,
			MaxFileCount:                 &maxFileCount,
			SingleChatMaxSelectFileCount: &singleChatMaxSelectFileCount,
			SingleFileSizeLimit:          50,
			SingleFileSizeLimitUnit:      cdaenum.MB,
			SupportDataType:              cdaenum.SupportDataTypes{"file"},
		}

		err := config.Validate()
		if err == nil {
			t.Fatal("预期验证失败，但没有得到错误")
		}

		if !strings.Contains(err.Error(), "AllowedFileCategories") {
			t.Fatalf("预期错误包含 'AllowedFileCategories'，但得到: %v", err)
		}
	})
}

func TestValObjCheck(t *testing.T) {
	// 测试用例：成功验证
	t.Run("Valid Config", func(t *testing.T) {
		maxFileCount := 10
		singleChatMaxSelectFileCount := 3
		config := &TempZoneConfig{
			Name:                         "临时区",
			TmpFileUseType:               cdaenum.TmpFileUseTypeUpload,
			MaxFileCount:                 &maxFileCount,
			SingleChatMaxSelectFileCount: &singleChatMaxSelectFileCount,
			SingleFileSizeLimit:          50,
			SingleFileSizeLimitUnit:      cdaenum.MB,
			SupportDataType:              cdaenum.SupportDataTypes{"file"},
			AllowedFileCategories:        cdaenum.AllowedFileCategories{"document"},
		}

		err := config.ValObjCheck()
		if err != nil {
			t.Fatalf("预期验证通过，但得到错误: %v", err)
		}
	})

	// 测试用例：基本参数校验失败
	t.Run("Basic Validation Fails", func(t *testing.T) {
		maxFileCount := 51 // 超过最大值50
		singleChatMaxSelectFileCount := 3
		config := &TempZoneConfig{
			Name:                         "临时区",
			TmpFileUseType:               cdaenum.TmpFileUseTypeUpload,
			MaxFileCount:                 &maxFileCount,
			SingleChatMaxSelectFileCount: &singleChatMaxSelectFileCount,
			SingleFileSizeLimit:          50,
			SingleFileSizeLimitUnit:      cdaenum.MB,
			SupportDataType:              cdaenum.SupportDataTypes{"file"},
			AllowedFileCategories:        cdaenum.AllowedFileCategories{"document"},
		}

		err := config.ValObjCheck()
		if err == nil {
			t.Fatal("预期验证失败，但没有得到错误")
		}

		// 修正：检查实际的错误消息内容
		if !strings.Contains(err.Error(), "max_file_count must be between 1 and 50") {
			t.Fatalf("预期错误包含 'max_file_count must be between 1 and 50'，但得到: %v", err)
		}
	})

	// 测试用例：临时文件使用类型无效
	t.Run("Invalid TmpFileUseType", func(t *testing.T) {
		maxFileCount := 10
		singleChatMaxSelectFileCount := 3
		config := &TempZoneConfig{
			Name:                         "临时区",
			TmpFileUseType:               cdaenum.TmpFileUseType("invalid_type"), // 无效的枚举值
			MaxFileCount:                 &maxFileCount,
			SingleChatMaxSelectFileCount: &singleChatMaxSelectFileCount,
			SingleFileSizeLimit:          50,
			SingleFileSizeLimitUnit:      cdaenum.MB,
			SupportDataType:              cdaenum.SupportDataTypes{"file"},
			AllowedFileCategories:        cdaenum.AllowedFileCategories{"document"},
		}

		err := config.ValObjCheck()
		if err == nil {
			t.Fatal("预期验证失败，但没有得到错误")
		}

		if !strings.Contains(err.Error(), "tmp_file_use_type") {
			t.Fatalf("预期错误包含 'tmp_file_use_type'，但得到: %v", err)
		}
	})

	// 测试用例：支持的数据类型无效
	t.Run("Invalid SupportDataType", func(t *testing.T) {
		maxFileCount := 10
		singleChatMaxSelectFileCount := 3
		config := &TempZoneConfig{
			Name:                         "临时区",
			TmpFileUseType:               cdaenum.TmpFileUseTypeUpload,
			MaxFileCount:                 &maxFileCount,
			SingleChatMaxSelectFileCount: &singleChatMaxSelectFileCount,
			SingleFileSizeLimit:          50,
			SingleFileSizeLimitUnit:      cdaenum.MB,
			SupportDataType:              cdaenum.SupportDataTypes{"invalid_type"}, // 无效的枚举值
			AllowedFileCategories:        cdaenum.AllowedFileCategories{"document"},
		}

		err := config.ValObjCheck()
		if err == nil {
			t.Fatal("预期验证失败，但没有得到错误")
		}

		if !strings.Contains(err.Error(), "support_data_type") {
			t.Fatalf("预期错误包含 'support_data_type'，但得到: %v", err)
		}
	})

	// 测试用例：允许的文件类别无效
	t.Run("Invalid AllowedFileCategories", func(t *testing.T) {
		maxFileCount := 10
		singleChatMaxSelectFileCount := 3
		config := &TempZoneConfig{
			Name:                         "临时区",
			TmpFileUseType:               cdaenum.TmpFileUseTypeUpload,
			MaxFileCount:                 &maxFileCount,
			SingleChatMaxSelectFileCount: &singleChatMaxSelectFileCount,
			SingleFileSizeLimit:          50,
			SingleFileSizeLimitUnit:      cdaenum.MB,
			SupportDataType:              cdaenum.SupportDataTypes{"file"},
			AllowedFileCategories:        cdaenum.AllowedFileCategories{"invalid_category"}, // 无效的枚举值
		}

		err := config.ValObjCheck()
		if err == nil {
			t.Fatal("预期验证失败，但没有得到错误")
		}

		if !strings.Contains(err.Error(), "allowed_file_categories") {
			t.Fatalf("预期错误包含 'allowed_file_categories'，但得到: %v", err)
		}
	})

	// 测试用例：单文件大小限制单位无效
	t.Run("Invalid SingleFileSizeLimitUnit", func(t *testing.T) {
		maxFileCount := 10
		singleChatMaxSelectFileCount := 3
		config := &TempZoneConfig{
			Name:                         "临时区",
			TmpFileUseType:               cdaenum.TmpFileUseTypeUpload,
			MaxFileCount:                 &maxFileCount,
			SingleChatMaxSelectFileCount: &singleChatMaxSelectFileCount,
			SingleFileSizeLimit:          50,
			SingleFileSizeLimitUnit:      cdaenum.BitUnit("invalid_unit"), // 无效的枚举值
			SupportDataType:              cdaenum.SupportDataTypes{"file"},
			AllowedFileCategories:        cdaenum.AllowedFileCategories{"document"},
		}

		err := config.ValObjCheck()
		if err == nil {
			t.Fatal("预期验证失败，但没有得到错误")
		}

		if !strings.Contains(err.Error(), "single_file_size_limit_unit") {
			t.Fatalf("预期错误包含 'single_file_size_limit_unit'，但得到: %v", err)
		}
	})

	// 测试用例：单文件大小超出最大限制（100MB）
	t.Run("SingleFileSizeLimit Exceeds Maximum", func(t *testing.T) {
		maxFileCount := 10
		singleChatMaxSelectFileCount := 3
		config := &TempZoneConfig{
			Name:                         "临时区",
			TmpFileUseType:               cdaenum.TmpFileUseTypeUpload,
			MaxFileCount:                 &maxFileCount,
			SingleChatMaxSelectFileCount: &singleChatMaxSelectFileCount,
			SingleFileSizeLimit:          200, // 超过最大限制100MB
			SingleFileSizeLimitUnit:      cdaenum.MB,
			SupportDataType:              cdaenum.SupportDataTypes{"file"},
			AllowedFileCategories:        cdaenum.AllowedFileCategories{"document"},
		}

		err := config.ValObjCheck()
		if err == nil {
			t.Fatal("预期验证失败，但没有得到错误")
		}

		if !strings.Contains(err.Error(), "exceeds maximum allowed") {
			t.Fatalf("预期错误包含 'exceeds maximum allowed'，但得到: %v", err)
		}
	})
}
