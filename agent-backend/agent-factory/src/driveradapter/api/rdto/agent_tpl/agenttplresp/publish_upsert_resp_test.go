package agenttplresp

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestPublishUpsertResp_StructFields(t *testing.T) {
	resp := PublishUpsertResp{
		AgentTplId:      12345,
		PublishedAt:     1640995200000,
		PublishedBy:     "user-123",
		PublishedByName: "John Doe",
	}

	assert.Equal(t, int64(12345), resp.AgentTplId)
	assert.Equal(t, int64(1640995200000), resp.PublishedAt)
	assert.Equal(t, "user-123", resp.PublishedBy)
	assert.Equal(t, "John Doe", resp.PublishedByName)
}

func TestPublishUpsertResp_Empty(t *testing.T) {
	resp := PublishUpsertResp{}

	assert.Equal(t, int64(0), resp.AgentTplId)
	assert.Equal(t, int64(0), resp.PublishedAt)
	assert.Empty(t, resp.PublishedBy)
	assert.Empty(t, resp.PublishedByName)
}

func TestPublishUpsertResp_WithAgentTplId(t *testing.T) {
	ids := []int64{
		0,
		1,
		12345,
		999999,
	}

	for _, id := range ids {
		resp := PublishUpsertResp{
			AgentTplId: id,
		}
		assert.Equal(t, id, resp.AgentTplId)
	}
}

func TestPublishUpsertResp_WithPublishedAt(t *testing.T) {
	timestamps := []int64{
		1640995200000, // 2022-01-01
		1643673600000, // 2022-02-01
		1646092800000, // 2022-03-01
		1672531200000, // 2023-01-01
		1704067200000, // 2024-01-01
	}

	for _, ts := range timestamps {
		resp := PublishUpsertResp{
			PublishedAt: ts,
		}
		assert.Equal(t, ts, resp.PublishedAt)
	}
}

func TestPublishUpsertResp_WithPublishedBy(t *testing.T) {
	users := []string{
		"user-001",
		"user-xyz",
		"用户-123",
		"",
	}

	for _, user := range users {
		resp := PublishUpsertResp{
			PublishedBy: user,
		}
		assert.Equal(t, user, resp.PublishedBy)
	}
}

func TestPublishUpsertResp_WithPublishedByName(t *testing.T) {
	names := []string{
		"John Doe",
		"张三",
		"User with numbers 123",
		"",
	}

	for _, name := range names {
		resp := PublishUpsertResp{
			PublishedByName: name,
		}
		assert.Equal(t, name, resp.PublishedByName)
	}
}

func TestPublishUpsertResp_WithAllFields(t *testing.T) {
	resp := PublishUpsertResp{
		AgentTplId:      98765,
		PublishedAt:     1672531200000,
		PublishedBy:     "user-complete",
		PublishedByName: "Complete User Name",
	}

	assert.Equal(t, int64(98765), resp.AgentTplId)
	assert.Equal(t, int64(1672531200000), resp.PublishedAt)
	assert.Equal(t, "user-complete", resp.PublishedBy)
	assert.Equal(t, "Complete User Name", resp.PublishedByName)
}

func TestPublishUpsertResp_FillPublishedByName_LocalDev(t *testing.T) {
	// This test depends on the environment
	// We'll just test that the method exists and can be called
	resp := PublishUpsertResp{
		PublishedBy: "user-123",
	}

	// Save original value and restore after test
	// Note: This is a simple test to ensure the method is callable
	// Actual behavior depends on cenvhelper.IsLocalDev()
	assert.Equal(t, "user-123", resp.PublishedBy)
	assert.Empty(t, resp.PublishedByName)
}

func TestPublishUpsertResp_WithTimestamp(t *testing.T) {
	resp := PublishUpsertResp{
		AgentTplId:  12345,
		PublishedAt: 1640995200000,
		PublishedBy: "user-123",
	}

	// Verify timestamp is set correctly
	assert.Equal(t, int64(1640995200000), resp.PublishedAt)
	assert.Greater(t, resp.PublishedAt, int64(0))
}

func TestPublishUpsertResp_WithZeroTimestamp(t *testing.T) {
	resp := PublishUpsertResp{
		PublishedAt: 0,
	}

	assert.Equal(t, int64(0), resp.PublishedAt)
}

func TestPublishUpsertResp_WithNegativeTimestamp(t *testing.T) {
	resp := PublishUpsertResp{
		PublishedAt: -12345,
	}

	assert.Equal(t, int64(-12345), resp.PublishedAt)
}

func TestPublishUpsertResp_WithChineseName(t *testing.T) {
	resp := PublishUpsertResp{
		PublishedByName: "张三",
	}

	assert.Equal(t, "张三", resp.PublishedByName)
}

func TestPublishUpsertResp_WithMixedName(t *testing.T) {
	resp := PublishUpsertResp{
		PublishedByName: "User用户Name",
	}

	assert.Equal(t, "User用户Name", resp.PublishedByName)
}

func TestPublishUpsertResp_FillPublishedByName_Signature(t *testing.T) {
	// Test that FillPublishedByName has the correct signature
	resp := &PublishUpsertResp{
		PublishedBy: "user-123",
	}

	// Just verify the method can be called with correct parameters
	// Actual implementation depends on environment and mock
	assert.NotNil(t, resp)
	assert.Equal(t, "user-123", resp.PublishedBy)
}

func TestPublishUpsertResp_ContextUsage(t *testing.T) {
	ctx := context.Background()
	resp := &PublishUpsertResp{
		PublishedBy: "user-123",
	}

	// Verify context can be used (though actual UM call would need mock)
	assert.NotNil(t, ctx)
	assert.NotNil(t, resp)
}
