package sqlhelper2

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

// TestSelectBuilder_Simple 简单的select示例
func TestSelectBuilder_Simple(t *testing.T) {
	sb := NewSelectBuilder()

	sb.Select([]string{"id", "name"}).From("users").
		Where("id", OperatorEq, 1).
		Or("name", OperatorEq, "John").
		Limit(10).Offset(0)

	sqlStr, args, err := sb.ToSelectSQL()
	assert.Equal(t, nil, err)

	expectedSQL := "select id,name from users where id = ? or name = ? limit 10 offset 0"

	assert.Equal(t, expectedSQL, sqlStr)

	expectedArgs := []interface{}{1, "John"}

	assert.Equal(t, expectedArgs, args)
}

// TestSelectBuilder_Complex 复杂的select示例
func TestSelectBuilder_Complex(t *testing.T) {
	sb := NewSelectBuilder()

	sb.Select([]string{"id", "name"}).From("users").
		Where("id", OperatorEq, 1).
		Or("name", OperatorEq, "John").
		Limit(10).Offset(0)

	sqlStr, args, err := sb.ToSelectSQL()
	assert.Equal(t, nil, err)

	expectedSQL := "select id,name from users where id = ? or name = ? limit 10 offset 0"

	assert.Equal(t, expectedSQL, sqlStr)

	expectedArgs := []interface{}{1, "John"}

	assert.Equal(t, expectedArgs, args)
}
