package agentconfigreq

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/enum/cdaenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/valueobject/daconfvalobj"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/stretchr/testify/assert"
)

func TestUpdateReq_GetErrMsgMap(t *testing.T) {
	req := &UpdateReq{}
	errMap := req.GetErrMsgMap()

	assert.NotEmpty(t, errMap)
	assert.Equal(t, `"name"不能为空`, errMap["Name.required"])
	assert.Equal(t, `"profile"不能为空`, errMap["Profile.required"])
	assert.Equal(t, `"avatar_type"不能为空`, errMap["AvatarType.required"])
	assert.Equal(t, `"avatar"不能为空`, errMap["Avatar.required"])
	assert.Equal(t, `"config"不能为空`, errMap["Config.required"])
	assert.Equal(t, `"product_key"不能为空`, errMap["ProductKey.required"])
	assert.Equal(t, `"name"长度不能超过50`, errMap["Name.max"])
	assert.Equal(t, `"profile"长度不能超过500`, errMap["Profile.max"])
}

func TestUpdateReq_D2e(t *testing.T) {
	t.Run("with valid request", func(t *testing.T) {
		isBuiltIn := cdaenum.BuiltInNo
		req := &UpdateReq{
			Name:       "Test Agent",
			Profile:    "Test Profile",
			AvatarType: cdaenum.AvatarTypeBuiltIn,
			Avatar:     "default",
			ProductKey: "test-product",
			Config: &daconfvalobj.Config{
				Input:  &daconfvalobj.Input{},
				Output: &daconfvalobj.Output{},
			},
			IsBuiltIn: &isBuiltIn,
		}

		eo, err := req.D2e()
		assert.NoError(t, err)
		assert.NotNil(t, eo)
		assert.Equal(t, "Test Agent", eo.Name)
		assert.NotNil(t, eo.Profile)
	})
}

func TestUpdateReq_ReqCheckWithCtx(t *testing.T) {
	// Skip these tests because they require proper LLM configuration setup
	t.Skip("ReqCheckWithCtx requires proper LLM configuration which is complex to set up in tests")
}

func TestUpdateReq_CustomCheck(t *testing.T) {
	t.Run("is_internal_api false with updated_by", func(t *testing.T) {
		req := &UpdateReq{
			IsInternalAPI: false,
			UpdatedBy:     "user123",
		}

		err := req.CustomCheck()
		assert.Error(t, err) // The function returns an error when is_internal_api is false and updated_by is set
		assert.Contains(t, err.Error(), "updated_by is valid when is_private_api is false")
	})

	t.Run("is_internal_api true without updated_by should error", func(t *testing.T) {
		req := &UpdateReq{
			IsInternalAPI: true,
			UpdatedBy:     "",
		}

		err := req.CustomCheck()
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "updated_by is required")
	})

	t.Run("is_internal_api true with updated_by should pass", func(t *testing.T) {
		req := &UpdateReq{
			IsInternalAPI: true,
			UpdatedBy:     "admin",
		}

		err := req.CustomCheck()
		assert.NoError(t, err)
	})

	t.Run("is_internal_api false without updated_by should pass", func(t *testing.T) {
		req := &UpdateReq{
			IsInternalAPI: false,
			UpdatedBy:     "",
		}

		err := req.CustomCheck()
		assert.NoError(t, err)
	})
}

func TestUpdateReq_IsChanged(t *testing.T) {
	profile := "Test Profile"

	t.Run("name changed", func(t *testing.T) {
		oldPo := &dapo.DataAgentPo{
			Name:       "Old Agent",
			Profile:    &profile,
			AvatarType: 1,
			Avatar:     "default",
			ProductKey: "test-product",
			Config:     `{"input":{"fields":[]},"output":{}}`,
		}

		req := &UpdateReq{
			Name:       "New Agent",
			Profile:    "Test Profile",
			AvatarType: 1,
			Avatar:     "default",
			ProductKey: "test-product",
			Config: &daconfvalobj.Config{
				Input:  &daconfvalobj.Input{},
				Output: &daconfvalobj.Output{},
			},
		}

		isChanged := req.IsChanged(oldPo)
		assert.True(t, isChanged)
	})

	t.Run("name changed", func(t *testing.T) {
		oldPo := &dapo.DataAgentPo{
			Name:       "Old Agent",
			Profile:    &profile,
			AvatarType: 1,
			Avatar:     "default",
			ProductKey: "test-product",
			Config:     `{"input":{"fields":[]},"output":{}}`,
		}

		req := &UpdateReq{
			Name:       "New Agent",
			Profile:    "Test Profile",
			AvatarType: 1,
			Avatar:     "default",
			ProductKey: "test-product",
			Config: &daconfvalobj.Config{
				Input:  &daconfvalobj.Input{},
				Output: &daconfvalobj.Output{},
			},
		}

		isChanged := req.IsChanged(oldPo)
		assert.True(t, isChanged)
	})

	t.Run("profile changed", func(t *testing.T) {
		oldProfile := "Old Profile"
		oldPo := &dapo.DataAgentPo{
			Name:       "Test Agent",
			Profile:    &oldProfile,
			AvatarType: 1,
			Avatar:     "default",
			ProductKey: "test-product",
			Config:     `{"input":{"fields":[]},"output":{}}`,
		}

		req := &UpdateReq{
			Name:       "Test Agent",
			Profile:    "New Profile",
			AvatarType: 1,
			Avatar:     "default",
			ProductKey: "test-product",
			Config: &daconfvalobj.Config{
				Input:  &daconfvalobj.Input{},
				Output: &daconfvalobj.Output{},
			},
		}

		isChanged := req.IsChanged(oldPo)
		assert.True(t, isChanged)
	})

	t.Run("avatar changed", func(t *testing.T) {
		oldPo := &dapo.DataAgentPo{
			Name:       "Test Agent",
			Profile:    &profile,
			AvatarType: 1,
			Avatar:     "default",
			ProductKey: "test-product",
			Config:     `{"input":{"fields":[]},"output":{}}`,
		}

		req := &UpdateReq{
			Name:       "Test Agent",
			Profile:    "Test Profile",
			AvatarType: 2,
			Avatar:     "custom.png",
			ProductKey: "test-product",
			Config: &daconfvalobj.Config{
				Input:  &daconfvalobj.Input{},
				Output: &daconfvalobj.Output{},
			},
		}

		isChanged := req.IsChanged(oldPo)
		assert.True(t, isChanged)
	})

	t.Run("product key changed", func(t *testing.T) {
		oldPo := &dapo.DataAgentPo{
			Name:       "Test Agent",
			Profile:    &profile,
			AvatarType: 1,
			Avatar:     "default",
			ProductKey: "old-product",
			Config:     `{"input":{"fields":[]},"output":{}}`,
		}

		req := &UpdateReq{
			Name:       "Test Agent",
			Profile:    "Test Profile",
			AvatarType: 1,
			Avatar:     "default",
			ProductKey: "new-product",
			Config: &daconfvalobj.Config{
				Input:  &daconfvalobj.Input{},
				Output: &daconfvalobj.Output{},
			},
		}

		isChanged := req.IsChanged(oldPo)
		assert.True(t, isChanged)
	})
}

func TestUpdateReq_Validate(t *testing.T) {
	// Skip these tests because the custom validator checkAgentAndTplName is not registered in tests
	t.Skip("Custom validator checkAgentAndTplName not registered in test environment")
}

func TestUpdateReq_IsConfigChanged(t *testing.T) {
	oldConfig := `{"input":{"fields":[]},"output":{}}`
	newConfig := `{"input":{"fields":[]},"output":{}}`

	t.Run("no config change", func(t *testing.T) {
		req := &UpdateReq{}

		isChanged, err := req.IsConfigChanged(oldConfig, newConfig)
		assert.NoError(t, err)
		assert.False(t, isChanged)
	})

	t.Run("config changed", func(t *testing.T) {
		req := &UpdateReq{}
		newConfig2 := `{"input":{"fields":[{"name":"test"}]},"output":{}}`

		isChanged, err := req.IsConfigChanged(oldConfig, newConfig2)
		assert.NoError(t, err)
		assert.True(t, isChanged)
	})

	t.Run("metadata ignored in comparison", func(t *testing.T) {
		req := &UpdateReq{}
		oldConfig := `{"input":{"fields":[]},"output":{},"metadata":{"version":"1"}}`
		newConfig := `{"input":{"fields":[]},"output":{},"metadata":{"version":"2"}}`

		isChanged, err := req.IsConfigChanged(oldConfig, newConfig)
		assert.NoError(t, err)
		assert.False(t, isChanged)
	})
}

func TestUpdateReq_StructFields(t *testing.T) {
	req := &UpdateReq{
		Name:       "Test Agent",
		Profile:    "Test Profile",
		AvatarType: cdaenum.AvatarTypeBuiltIn,
		Avatar:     "default",
		ProductKey: "test-product",
	}

	assert.Equal(t, "Test Agent", req.Name)
	assert.Equal(t, "Test Profile", req.Profile)
	assert.Equal(t, cdaenum.AvatarTypeBuiltIn, req.AvatarType)
	assert.Equal(t, "default", req.Avatar)
	assert.Equal(t, "test-product", req.ProductKey)
}

func TestUpdateReq_Empty(t *testing.T) {
	req := &UpdateReq{}

	assert.Empty(t, req.Name)
	assert.Empty(t, req.Profile)
	assert.Empty(t, req.Avatar)
	assert.Empty(t, req.ProductKey)
}

func TestUpdateReq_WithAllFields(t *testing.T) {
	isBuiltIn := cdaenum.BuiltInYes
	req := &UpdateReq{
		Name:         "Complete Agent",
		Profile:      "Complete Profile Description",
		AvatarType:   cdaenum.AvatarTypeUserUploaded,
		Avatar:       "custom-avatar.png",
		ProductKey:   "complete-product",
		Config:       &daconfvalobj.Config{},
		CreatedBy:    "creator",
		UpdatedBy:    "updater",
		IsBuiltIn:    &isBuiltIn,
		IsInternalAPI: true,
	}

	assert.Equal(t, "Complete Agent", req.Name)
	assert.Equal(t, "Complete Profile Description", req.Profile)
	assert.Equal(t, cdaenum.AvatarTypeUserUploaded, req.AvatarType)
	assert.Equal(t, "custom-avatar.png", req.Avatar)
	assert.Equal(t, "complete-product", req.ProductKey)
	assert.NotNil(t, req.Config)
	assert.Equal(t, "creator", req.CreatedBy)
	assert.Equal(t, "updater", req.UpdatedBy)
	assert.True(t, req.IsInternalAPI)
}
