package sqlhelper2

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestDeleteBuilder(t *testing.T) {
	db := NewDeleteBuilder()
	db.From("table1")
	db.Where("key1", OperatorEq, "value1")
	db.Or("key2", OperatorEq, "value2")
	db.In("key3", []string{"value3", "value4"})

	sql, args, err := db.ToDeleteSQL()
	if err != nil {
		t.Error(err)
	}

	assert.Equal(t, "delete from table1 where key1 = ? and key3 in (?,?) or key2 = ?", sql, "db.ToDeleteSQL() failed")

	assert.Equal(t, []interface{}{"value1", "value3", "value4", "value2"}, args, "db.ToDeleteSQL() failed")
}
