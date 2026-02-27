package spaceresp

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/entity/spaceeo"
	"github.com/stretchr/testify/assert"
)

func TestNewDetailResp(t *testing.T) {
	t.Parallel()

	resp := NewDetailResp()

	assert.NotNil(t, resp)
	assert.IsType(t, &DetailResp{}, resp)
}

func TestDetailResp_StructFields(t *testing.T) {
	t.Parallel()

	resp := DetailResp{
		ID:        "space-123",
		Name:      "Test Space",
		Key:       "space-key-456",
		Profile:   "Test space profile",
		CreatedAt: 1640995200000,
		UpdatedAt: 1641081600000,
		CreatedBy: "user-001",
		UpdatedBy: "user-002",
	}

	assert.Equal(t, "space-123", resp.ID)
	assert.Equal(t, "Test Space", resp.Name)
	assert.Equal(t, "space-key-456", resp.Key)
	assert.Equal(t, "Test space profile", resp.Profile)
	assert.Equal(t, int64(1640995200000), resp.CreatedAt)
	assert.Equal(t, int64(1641081600000), resp.UpdatedAt)
	assert.Equal(t, "user-001", resp.CreatedBy)
	assert.Equal(t, "user-002", resp.UpdatedBy)
}

func TestDetailResp_Empty(t *testing.T) {
	t.Parallel()

	resp := DetailResp{}

	assert.Empty(t, resp.ID)
	assert.Empty(t, resp.Name)
	assert.Empty(t, resp.Key)
	assert.Empty(t, resp.Profile)
	assert.Equal(t, int64(0), resp.CreatedAt)
	assert.Equal(t, int64(0), resp.UpdatedAt)
	assert.Empty(t, resp.CreatedBy)
	assert.Empty(t, resp.UpdatedBy)
}

func TestDetailResp_WithID(t *testing.T) {
	t.Parallel()

	ids := []string{
		"space-001",
		"space-xyz",
		"空间-123",
		"",
	}

	for _, id := range ids {
		resp := DetailResp{
			ID: id,
		}
		assert.Equal(t, id, resp.ID)
	}
}

func TestDetailResp_WithName(t *testing.T) {
	t.Parallel()

	names := []string{
		"Test Space",
		"测试空间",
		"Space with numbers 123",
		"Space with special chars !@#$%",
		"",
	}

	for _, name := range names {
		resp := DetailResp{
			Name: name,
		}
		assert.Equal(t, name, resp.Name)
	}
}

func TestDetailResp_WithKey(t *testing.T) {
	t.Parallel()

	keys := []string{
		"space-key-001",
		"space-xyz",
		"空间-key-中文",
		"",
	}

	for _, key := range keys {
		resp := DetailResp{
			Key: key,
		}
		assert.Equal(t, key, resp.Key)
	}
}

func TestDetailResp_WithProfile(t *testing.T) {
	t.Parallel()

	profiles := []string{
		"Test space profile",
		"测试空间简介",
		"Profile with numbers 123",
		"Profile with special chars !@#$%",
		"",
	}

	for _, profile := range profiles {
		resp := DetailResp{
			Profile: profile,
		}
		assert.Equal(t, profile, resp.Profile)
	}
}

func TestDetailResp_WithTimestamps(t *testing.T) {
	t.Parallel()

	timestamps := []int64{
		1640995200000, // 2022-01-01
		1643673600000, // 2022-02-01
		1646092800000, // 2022-03-01
		1672531200000, // 2023-01-01
		1704067200000, // 2024-01-01
		0,             // Zero timestamp
	}

	for _, ts := range timestamps {
		resp := DetailResp{
			CreatedAt: ts,
			UpdatedAt: ts,
		}
		assert.Equal(t, ts, resp.CreatedAt)
		assert.Equal(t, ts, resp.UpdatedAt)
	}
}

func TestDetailResp_WithCreatedBy(t *testing.T) {
	t.Parallel()

	users := []string{
		"user-001",
		"user-xyz",
		"用户-123",
		"",
	}

	for _, user := range users {
		resp := DetailResp{
			CreatedBy: user,
		}
		assert.Equal(t, user, resp.CreatedBy)
	}
}

func TestDetailResp_WithUpdatedBy(t *testing.T) {
	t.Parallel()

	users := []string{
		"user-001",
		"user-xyz",
		"用户-123",
		"",
	}

	for _, user := range users {
		resp := DetailResp{
			UpdatedBy: user,
		}
		assert.Equal(t, user, resp.UpdatedBy)
	}
}

func TestDetailResp_LoadFromEo(t *testing.T) {
	t.Parallel()

	eo := &spaceeo.Space{}
	eo.ID = "space-789"
	eo.Name = "Entity Space"
	eo.Key = "entity-key"
	eo.Profile = "Entity profile"
	eo.CreatedAt = 1640995200000
	eo.UpdatedAt = 1641081600000

	resp := NewDetailResp()
	err := resp.LoadFromEo(eo)

	assert.NoError(t, err)
	assert.Equal(t, "space-789", resp.ID)
	assert.Equal(t, "Entity Space", resp.Name)
	assert.Equal(t, "entity-key", resp.Key)
	assert.Equal(t, "Entity profile", resp.Profile)
	assert.Equal(t, int64(1640995200000), resp.CreatedAt)
	assert.Equal(t, int64(1641081600000), resp.UpdatedAt)
}

func TestDetailResp_WithAllFields(t *testing.T) {
	t.Parallel()

	resp := DetailResp{
		ID:        "space-complete",
		Name:      "Complete Space Name",
		Key:       "complete-space-key",
		Profile:   "Complete space profile with description",
		CreatedAt: 1672531200000,
		UpdatedAt: 1704067200000,
		CreatedBy: "user-complete",
		UpdatedBy: "user-updater",
	}

	assert.Equal(t, "space-complete", resp.ID)
	assert.Equal(t, "Complete Space Name", resp.Name)
	assert.Equal(t, "complete-space-key", resp.Key)
	assert.Equal(t, "Complete space profile with description", resp.Profile)
	assert.Equal(t, int64(1672531200000), resp.CreatedAt)
	assert.Equal(t, int64(1704067200000), resp.UpdatedAt)
	assert.Equal(t, "user-complete", resp.CreatedBy)
	assert.Equal(t, "user-updater", resp.UpdatedBy)
}

func TestDetailResp_WithNegativeTimestamps(t *testing.T) {
	t.Parallel()

	resp := DetailResp{
		CreatedAt: -12345,
		UpdatedAt: -67890,
	}

	assert.Equal(t, int64(-12345), resp.CreatedAt)
	assert.Equal(t, int64(-67890), resp.UpdatedAt)
}

func TestDetailResp_WithChineseCharacters(t *testing.T) {
	t.Parallel()

	resp := DetailResp{
		ID:        "空间-中文",
		Name:      "中文空间名称",
		Key:       "中文-key",
		Profile:   "中文空间简介",
		CreatedBy: "用户-中文",
		UpdatedBy: "更新者-中文",
	}

	assert.Equal(t, "空间-中文", resp.ID)
	assert.Equal(t, "中文空间名称", resp.Name)
	assert.Equal(t, "中文-key", resp.Key)
	assert.Equal(t, "中文空间简介", resp.Profile)
	assert.Equal(t, "用户-中文", resp.CreatedBy)
	assert.Equal(t, "更新者-中文", resp.UpdatedBy)
}
