package agentconfigreq

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/enum/cdaenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/enum/cdaenum/agentconfigenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/valueobject/daconfvalobj"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cutil"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestUpdateReq_GetErrMsgMap(t *testing.T) {
	req := &UpdateReq{}

	errMap := req.GetErrMsgMap()

	// Verify the error message map is not nil
	assert.NotNil(t, errMap)
}

func TestUpdateReq_CustomCheck_NonInternalAPI_WithUpdatedBy(t *testing.T) {
	req := &UpdateReq{}
	req.IsInternalAPI = false
	req.UpdatedBy = "user-123"

	err := req.CustomCheck()

	assert.Error(t, err)
	assert.Contains(t, err.Error(), "updated_by is valid when is_private_api is false")
}

func TestUpdateReq_CustomCheck_InternalAPI_WithoutUpdatedBy(t *testing.T) {
	req := &UpdateReq{}
	req.IsInternalAPI = true
	req.UpdatedBy = ""

	err := req.CustomCheck()

	assert.Error(t, err)
	assert.Contains(t, err.Error(), "updated_by is required when is_private_api is true")
}

func TestUpdateReq_CustomCheck_InternalAPI_WithUpdatedBy(t *testing.T) {
	req := &UpdateReq{}
	req.IsInternalAPI = true
	req.UpdatedBy = "user-123"

	err := req.CustomCheck()

	assert.NoError(t, err)
}

func TestUpdateReq_CustomCheck_NonInternalAPI_WithoutUpdatedBy(t *testing.T) {
	req := &UpdateReq{}
	req.IsInternalAPI = false
	req.UpdatedBy = ""

	err := req.CustomCheck()

	assert.NoError(t, err)
}

func TestUpdateReq_D2e_WithAllFields(t *testing.T) {
	req := &UpdateReq{
		Name:       "Test Agent",
		Profile:    "Test Profile",
		AvatarType: cdaenum.AvatarTypeBuiltIn,
		Avatar:     "avatar-123",
		ProductKey: "product-123",
		Config:     daconfvalobj.NewConfig(),
		CreatedBy:  "user-123",
		UpdatedBy:  "user-123",
	}

	eo, err := req.D2e()

	assert.NoError(t, err)
	require.NotNil(t, eo)
	assert.Equal(t, "Test Agent", eo.Name)
	assert.Equal(t, "product-123", eo.ProductKey)
	assert.Equal(t, "Test Profile", eo.GetProfileStr())
	assert.Equal(t, "avatar-123", eo.Avatar)
}

func TestUpdateReq_D2e_WithConfig(t *testing.T) {
	req := &UpdateReq{
		Name:        "Test Agent",
		Profile:     "Test Profile",
		AvatarType:   cdaenum.AvatarTypeBuiltIn,
		Avatar:       "avatar-123",
		ProductKey:  "product-123",
	}

	// Create a valid Config
	config := daconfvalobj.NewConfig()
	config.Metadata.SetConfigTplVersion(agentconfigenum.ConfigTplVersionV1)
	req.Config = config

	eo, err := req.D2e()

	assert.NoError(t, err)
	require.NotNil(t, eo)
	assert.Equal(t, "Test Agent", eo.Name)
	assert.NotNil(t, eo.Config)
}

func TestUpdateReq_D2e_WithIsBuiltIn(t *testing.T) {
	req := &UpdateReq{
		Name:        "Test Agent",
		Profile:     "Test Profile",
		AvatarType:   cdaenum.AvatarTypeBuiltIn,
		Avatar:       "avatar-123",
		ProductKey:  "product-123",
		Config:       daconfvalobj.NewConfig(),
	}

	builtIn := cdaenum.BuiltInYes
	req.IsBuiltIn = &builtIn

	eo, err := req.D2e()

	assert.NoError(t, err)
	require.NotNil(t, eo)
	assert.Equal(t, cdaenum.BuiltInYes, *eo.IsBuiltIn)
}

func TestUpdateReq_D2e_WithCreatedBy(t *testing.T) {
	req := &UpdateReq{
		Name:        "Test Agent",
		Profile:     "Test Profile",
		AvatarType:   cdaenum.AvatarTypeBuiltIn,
		Avatar:       "avatar-123",
		ProductKey:  "product-123",
		Config:       daconfvalobj.NewConfig(),
	}
	req.CreatedBy = "creator-123"

	eo, err := req.D2e()

	assert.NoError(t, err)
	require.NotNil(t, eo)
	assert.Equal(t, "creator-123", eo.CreatedBy)
}

func TestUpdateReq_IsChanged_DifferentName(t *testing.T) {
	req := &UpdateReq{
		Name:       "Updated Agent Name",
		Profile:    "Test Profile",
		AvatarType: cdaenum.AvatarTypeBuiltIn,
		Avatar:     "avatar-123",
		ProductKey: "product-123",
		Config:     daconfvalobj.NewConfig(),
	}

	profile := "Test Profile"
	configStr, _ := cutil.JSON().MarshalToString(req.Config)

	oldPo := &dapo.DataAgentPo{
		Name:       "Original Name",
		Profile:    &profile,
		AvatarType: cdaenum.AvatarTypeBuiltIn,
		Avatar:     "avatar-123",
		ProductKey: "product-123",
		Config:     configStr,
	}

	result := req.IsChanged(oldPo)

	assert.True(t, result)
}

func TestUpdateReq_IsChanged_SameData(t *testing.T) {
	req := &UpdateReq{
		Name:       "Test Agent",
		Profile:    "Test Profile",
		AvatarType: cdaenum.AvatarTypeBuiltIn,
		Avatar:     "avatar-123",
		ProductKey: "product-123",
		Config:     daconfvalobj.NewConfig(),
	}

	profile := "Test Profile"
	configStr, _ := cutil.JSON().MarshalToString(req.Config)

	oldPo := &dapo.DataAgentPo{
		Name:       "Test Agent",
		Profile:    &profile,
		AvatarType: cdaenum.AvatarTypeBuiltIn,
		Avatar:     "avatar-123",
		ProductKey: "product-123",
		Config:     configStr,
	}

	result := req.IsChanged(oldPo)

	// Since we use the same config data, it should be considered not changed
	assert.False(t, result)
}

func TestUpdateReq_D2e_WithStatus(t *testing.T) {
	req := &UpdateReq{
		Name:        "Test Agent",
		Profile:     "Test Profile",
		AvatarType:   cdaenum.AvatarTypeBuiltIn,
		Avatar:       "avatar-123",
		ProductKey:  "product-123",
		Config:       daconfvalobj.NewConfig(),
	}

	// Note: Status is not directly settable in UpdateReq
	// It might come from the Config or be set during D2e conversion

	eo, err := req.D2e()

	assert.NoError(t, err)
	require.NotNil(t, eo)
	// Status might have a default value
}

func TestUpdateReq_D2e_NilConfig_Panics(t *testing.T) {
	req := &UpdateReq{
		Name:       "Test Agent",
		Profile:    "Test Profile",
		AvatarType: cdaenum.AvatarTypeBuiltIn,
		Avatar:     "avatar-123",
		ProductKey: "product-123",
		// Config is nil - should panic
	}

	assert.Panics(t, func() {
		_, _ = req.D2e()
	})
}

func TestUpdateReq_D2e_WithDifferentAvatarTypes(t *testing.T) {
	avatarTypes := []cdaenum.AvatarType{
		cdaenum.AvatarTypeBuiltIn,
		cdaenum.AvatarTypeUserUploaded,
		cdaenum.AvatarTypeAIGenerated,
	}

	for _, avatarType := range avatarTypes {
		req := &UpdateReq{
			Name:        "Test Agent",
			Profile:     "Test Profile",
			AvatarType:  avatarType,
			Avatar:      "avatar-123",
			ProductKey:   "product-123",
			Config:       daconfvalobj.NewConfig(),
		}

		eo, err := req.D2e()

		assert.NoError(t, err)
		require.NotNil(t, eo)
		assert.Equal(t, avatarType, eo.AvatarType)
	}
}
