package cenum

import (
	"testing"
)

func TestPmsTargetObjType_String(t *testing.T) {
	t.Run("string conversion", func(t *testing.T) {
		targetType := PmsTargetObjType("test-type")
		result := targetType.String()

		if result != "test-type" {
			t.Errorf("Expected 'test-type', got '%s'", result)
		}
	})
}

func TestPmsTargetObjType_EnumCheck(t *testing.T) {
	t.Run("valid department", func(t *testing.T) {
		err := PmsTargetObjTypeDep.EnumCheck()
		if err != nil {
			t.Errorf("Expected no error for Department, got %v", err)
		}
	})

	t.Run("valid user", func(t *testing.T) {
		err := PmsTargetObjTypeUser.EnumCheck()
		if err != nil {
			t.Errorf("Expected no error for User, got %v", err)
		}
	})

	t.Run("valid user group", func(t *testing.T) {
		err := PmsTargetObjTypeUserGroup.EnumCheck()
		if err != nil {
			t.Errorf("Expected no error for UserGroup, got %v", err)
		}
	})

	t.Run("valid role", func(t *testing.T) {
		err := PmsTargetObjTypeRole.EnumCheck()
		if err != nil {
			t.Errorf("Expected no error for Role, got %v", err)
		}
	})

	t.Run("valid app account", func(t *testing.T) {
		err := PmsTargetObjTypeAppAccount.EnumCheck()
		if err != nil {
			t.Errorf("Expected no error for AppAccount, got %v", err)
		}
	})

	t.Run("invalid type", func(t *testing.T) {
		targetType := PmsTargetObjType("invalid")
		err := targetType.EnumCheck()

		if err == nil {
			t.Error("Expected error for invalid target type")
		}
	})

	t.Run("empty type", func(t *testing.T) {
		targetType := PmsTargetObjType("")
		err := targetType.EnumCheck()

		if err == nil {
			t.Error("Expected error for empty target type")
		}
	})
}

func TestPmsTargetObjType_Constants(t *testing.T) {
	t.Run("PmsTargetObjTypeDep constant", func(t *testing.T) {
		if PmsTargetObjTypeDep != "department" {
			t.Errorf("Expected PmsTargetObjTypeDep to be 'department', got '%s'", PmsTargetObjTypeDep)
		}
	})

	t.Run("PmsTargetObjTypeUser constant", func(t *testing.T) {
		if PmsTargetObjTypeUser != "user" {
			t.Errorf("Expected PmsTargetObjTypeUser to be 'user', got '%s'", PmsTargetObjTypeUser)
		}
	})

	t.Run("PmsTargetObjTypeUserGroup constant", func(t *testing.T) {
		if PmsTargetObjTypeUserGroup != "group" {
			t.Errorf("Expected PmsTargetObjTypeUserGroup to be 'group', got '%s'", PmsTargetObjTypeUserGroup)
		}
	})

	t.Run("PmsTargetObjTypeRole constant", func(t *testing.T) {
		if PmsTargetObjTypeRole != "role" {
			t.Errorf("Expected PmsTargetObjTypeRole to be 'role', got '%s'", PmsTargetObjTypeRole)
		}
	})

	t.Run("PmsTargetObjTypeAppAccount constant", func(t *testing.T) {
		if PmsTargetObjTypeAppAccount != "app" {
			t.Errorf("Expected PmsTargetObjTypeAppAccount to be 'app', got '%s'", PmsTargetObjTypeAppAccount)
		}
	})
}
