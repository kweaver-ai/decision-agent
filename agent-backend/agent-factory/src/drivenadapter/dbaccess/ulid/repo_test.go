package dbaulid

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestNewUlidRepo(t *testing.T) {
	repo := NewUlidRepo()

	assert.NotNil(t, repo, "NewUlidRepo should return non-nil repo")
}

func TestUniqueID_TableName(t *testing.T) {
	uid := &UniqueID{}

	tableName := uid.TableName()

	assert.Equal(t, "t_stc_unique_id", tableName, "TableName should return correct table name")
}

func TestUniqueID_Fields(t *testing.T) {
	uid := &UniqueID{
		ID:   "test123",
		Flag: 1,
	}

	assert.Equal(t, "test123", uid.ID, "ID field should be set")
	assert.Equal(t, 1, uid.Flag, "Flag field should be set")
}
