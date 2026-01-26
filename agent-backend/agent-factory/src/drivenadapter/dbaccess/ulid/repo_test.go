package dbaulid

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestNewUlidRepo(t *testing.T) {
	repo := NewUlidRepo()

	assert.NotNil(t, repo, "NewUlidRepo should return non-nil repo")
}

func TestGenSnowID(t *testing.T) {
	ctx := context.Background()

	repo := NewUlidRepo()
	id, err := repo.GenSnowID(ctx)

	assert.NoError(t, err, "GenSnowID should not return error")
	assert.NotEmpty(t, id, "GenSnowID should return non-empty id")
	assert.Len(t, id, 19, "Snowflake ID should be 19 characters")
	assert.Regexp(t, `^\d{19}$`, id, "Snowflake ID should be numeric")
}

func TestGenSnowID_Unique(t *testing.T) {
	ctx := context.Background()

	repo := NewUlidRepo()

	id1, _ := repo.GenSnowID(ctx)
	id2, _ := repo.GenSnowID(ctx)

	assert.NotEqual(t, id1, id2, "GenSnowID should generate unique IDs")
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

func TestUlidMake(t *testing.T) {
	ulid := UlidMake()

	assert.NotEmpty(t, ulid, "UlidMake should return non-empty ulid")
	assert.Len(t, ulid, 26, "ULID should be 26 characters")
	assert.Regexp(t, `^[0-9A-Za-z_-]{26}$`, ulid, "ULID should match pattern")
}

func TestUlidMake_Unique(t *testing.T) {
	ulid1 := UlidMake()
	ulid2 := UlidMake()

	assert.NotEqual(t, ulid1, ulid2, "UlidMake should generate unique ULIDs")
}
}
