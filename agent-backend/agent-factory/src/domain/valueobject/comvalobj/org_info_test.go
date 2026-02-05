package comvalobj

import (
	"testing"
)

func TestRoleInfo(t *testing.T) {
	tests := []struct {
		name     string
		roleInfo RoleInfo
	}{
		{
			name: "完整角色信息",
			roleInfo: RoleInfo{
				RoleID:   "role-123",
				RoleName: "管理员",
			},
		},
		{
			name: "空角色信息",
			roleInfo: RoleInfo{
				RoleID:   "",
				RoleName: "",
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if tt.roleInfo.RoleID != tt.roleInfo.RoleID {
				t.Errorf("RoleID = %s", tt.roleInfo.RoleID)
			}
			if tt.roleInfo.RoleName != tt.roleInfo.RoleName {
				t.Errorf("RoleName = %s", tt.roleInfo.RoleName)
			}
		})
	}
}

func TestUserInfo(t *testing.T) {
	tests := []struct {
		name     string
		userInfo UserInfo
	}{
		{
			name: "完整用户信息",
			userInfo: UserInfo{
				UserID:   "user-123",
				Username: "testuser",
			},
		},
		{
			name: "空用户信息",
			userInfo: UserInfo{
				UserID:   "",
				Username: "",
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if tt.userInfo.UserID != tt.userInfo.UserID {
				t.Errorf("UserID = %s", tt.userInfo.UserID)
			}
			if tt.userInfo.Username != tt.userInfo.Username {
				t.Errorf("Username = %s", tt.userInfo.Username)
			}
		})
	}
}

func TestUserGroupInfo(t *testing.T) {
	tests := []struct {
		name          string
		userGroupInfo UserGroupInfo
	}{
		{
			name: "完整用户组信息",
			userGroupInfo: UserGroupInfo{
				UserGroupID:   "group-123",
				UserGroupName: "测试组",
			},
		},
		{
			name: "空用户组信息",
			userGroupInfo: UserGroupInfo{
				UserGroupID:   "",
				UserGroupName: "",
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if tt.userGroupInfo.UserGroupID != tt.userGroupInfo.UserGroupID {
				t.Errorf("UserGroupID = %s", tt.userGroupInfo.UserGroupID)
			}
			if tt.userGroupInfo.UserGroupName != tt.userGroupInfo.UserGroupName {
				t.Errorf("UserGroupName = %s", tt.userGroupInfo.UserGroupName)
			}
		})
	}
}

func TestDepartmentInfo(t *testing.T) {
	tests := []struct {
		name           string
		departmentInfo DepartmentInfo
	}{
		{
			name: "完整部门信息",
			departmentInfo: DepartmentInfo{
				DepartmentID:   "dept-123",
				DepartmentName: "技术部",
			},
		},
		{
			name: "空部门信息",
			departmentInfo: DepartmentInfo{
				DepartmentID:   "",
				DepartmentName: "",
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if tt.departmentInfo.DepartmentID != tt.departmentInfo.DepartmentID {
				t.Errorf("DepartmentID = %s", tt.departmentInfo.DepartmentID)
			}
			if tt.departmentInfo.DepartmentName != tt.departmentInfo.DepartmentName {
				t.Errorf("DepartmentName = %s", tt.departmentInfo.DepartmentName)
			}
		})
	}
}

func TestAppAccountInfo(t *testing.T) {
	tests := []struct {
		name           string
		appAccountInfo AppAccountInfo
	}{
		{
			name: "完整应用账号信息",
			appAccountInfo: AppAccountInfo{
				AppAccountID:   "account-123",
				AppAccountName: "测试应用",
			},
		},
		{
			name: "空应用账号信息",
			appAccountInfo: AppAccountInfo{
				AppAccountID:   "",
				AppAccountName: "",
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if tt.appAccountInfo.AppAccountID != tt.appAccountInfo.AppAccountID {
				t.Errorf("AppAccountID = %s", tt.appAccountInfo.AppAccountID)
			}
			if tt.appAccountInfo.AppAccountName != tt.appAccountInfo.AppAccountName {
				t.Errorf("AppAccountName = %s", tt.appAccountInfo.AppAccountName)
			}
		})
	}
}
