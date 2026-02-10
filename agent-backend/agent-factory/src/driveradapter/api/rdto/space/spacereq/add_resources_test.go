package spacereq

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/constant/csconstant"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/enum/cdaenum"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestAddResourcesReq_GetErrMsgMap(t *testing.T) {
	req := &AddResourcesReq{}
	errMap := req.GetErrMsgMap()

	assert.NotEmpty(t, errMap)
	assert.Equal(t, `"resources"不能为空`, errMap["Resources.required"])
	assert.Equal(t, `"resources"至少需要一个资源`, errMap["Resources.min"])
}

func TestAddResourcesReq_TmpHandleResourceType(t *testing.T) {
	req := &AddResourcesReq{
		Resources: []*SpaceResourceReq{
			{
				ResourceType: "data_agent",
				ResourceID:   "agent-1",
			},
			{
				ResourceType: cdaenum.ResourceTypeDataAgent,
				ResourceID:   "agent-2",
			},
		},
	}

	req.TmpHandleResourceType()

	// Both should be ResourceTypeDataAgent now
	assert.Equal(t, cdaenum.ResourceTypeDataAgent, req.Resources[0].ResourceType)
	assert.Equal(t, cdaenum.ResourceTypeDataAgent, req.Resources[1].ResourceType)
}

func TestAddResourcesReq_CustomCheck(t *testing.T) {
	tests := []struct {
		name    string
		req     *AddResourcesReq
		wantErr bool
		errMsg  string
	}{
		{
			name: "empty resources",
			req: &AddResourcesReq{
				Resources: []*SpaceResourceReq{},
			},
			wantErr: true,
			errMsg:  "资源列表不能为空",
		},
		{
			name: "valid single resource",
			req: &AddResourcesReq{
				Resources: []*SpaceResourceReq{
					{
						ResourceType: cdaenum.ResourceTypeDataAgent,
						ResourceID:   "agent-1",
					},
				},
			},
			wantErr: false,
		},
		{
			name: "valid multiple resources",
			req: &AddResourcesReq{
				Resources: []*SpaceResourceReq{
					{
						ResourceType: cdaenum.ResourceTypeDataAgent,
						ResourceID:   "agent-1",
					},
					{
						ResourceType: cdaenum.ResourceTypeDataAgent,
						ResourceID:   "agent-2",
					},
				},
			},
			wantErr: false,
		},
		{
			name: "invalid resource type",
			req: &AddResourcesReq{
				Resources: []*SpaceResourceReq{
					{
						ResourceType: "invalid",
						ResourceID:   "agent-1",
					},
				},
			},
			wantErr: true,
			errMsg:  "无效的资源类型",
		},
		{
			name: "exceeds max resources",
			req: func() *AddResourcesReq {
				resources := make([]*SpaceResourceReq, csconstant.MaxResourceNumInOneSpace+1)
				for i := range resources {
					resources[i] = &SpaceResourceReq{
						ResourceType: cdaenum.ResourceTypeDataAgent,
						ResourceID:   "agent-" + string(rune(i)),
					}
				}
				return &AddResourcesReq{Resources: resources}
			}(),
			wantErr: true,
			errMsg:  "资源数量超过最大限制",
		},
		{
			name: "duplicate resources - should be deduplicated",
			req: &AddResourcesReq{
				Resources: []*SpaceResourceReq{
					{
						ResourceType: cdaenum.ResourceTypeDataAgent,
						ResourceID:   "agent-1",
					},
					{
						ResourceType: cdaenum.ResourceTypeDataAgent,
						ResourceID:   "agent-1",
					},
				},
			},
			wantErr: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := tt.req.CustomCheck()
			if tt.wantErr {
				require.Error(t, err)
				if tt.errMsg != "" {
					assert.Contains(t, err.Error(), tt.errMsg)
				}
			} else {
				require.NoError(t, err)
			}
		})
	}
}

func TestAddResourcesReq_ToResourceEos(t *testing.T) {
	tests := []struct {
		name        string
		resources   []*SpaceResourceReq
		spaceID     string
		spaceKey    string
		wantErr     bool
		expectedLen int
	}{
		{
			name: "convert single resource",
			resources: []*SpaceResourceReq{
				{
					ResourceType: cdaenum.ResourceTypeDataAgent,
					ResourceID:   "agent-1",
				},
			},
			spaceID:     "space-1",
			spaceKey:    "space-key-1",
			wantErr:     false,
			expectedLen: 1,
		},
		{
			name: "convert multiple resources",
			resources: []*SpaceResourceReq{
				{
					ResourceType: cdaenum.ResourceTypeDataAgent,
					ResourceID:   "agent-1",
				},
				{
					ResourceType: cdaenum.ResourceTypeDataAgent,
					ResourceID:   "agent-2",
				},
			},
			spaceID:     "space-2",
			spaceKey:    "space-key-2",
			wantErr:     false,
			expectedLen: 2,
		},
		{
			name:        "empty resources",
			resources:   []*SpaceResourceReq{},
			spaceID:     "space-3",
			spaceKey:    "space-key-3",
			wantErr:     false,
			expectedLen: 0,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			req := &AddResourcesReq{}
			eos, err := req.ToResourceEos(tt.resources, tt.spaceID, tt.spaceKey)

			if tt.wantErr {
				require.Error(t, err)
			} else {
				require.NoError(t, err)
				assert.Len(t, eos, tt.expectedLen)
			}

			// Verify space ID and key are set correctly
			for _, eo := range eos {
				assert.Equal(t, tt.spaceID, eo.SpaceID)
				assert.Equal(t, tt.spaceKey, eo.SpaceKey)
			}
		})
	}
}

func TestAddResourcesReq_StructFields(t *testing.T) {
	req := &AddResourcesReq{
		Resources: []*SpaceResourceReq{
			{
				ResourceType: cdaenum.ResourceTypeDataAgent,
				ResourceID:   "agent-1",
			},
		},
	}

	assert.NotNil(t, req.Resources)
	assert.Len(t, req.Resources, 1)
	assert.Equal(t, cdaenum.ResourceTypeDataAgent, req.Resources[0].ResourceType)
	assert.Equal(t, "agent-1", req.Resources[0].ResourceID)
}

func TestAddResourcesReq_Deduplication(t *testing.T) {
	req := &AddResourcesReq{
		Resources: []*SpaceResourceReq{
			{
				ResourceType: cdaenum.ResourceTypeDataAgent,
				ResourceID:   "agent-1",
			},
			{
				ResourceType: cdaenum.ResourceTypeDataAgent,
				ResourceID:   "agent-1",
			},
			{
				ResourceType: cdaenum.ResourceTypeDataAgent,
				ResourceID:   "agent-2",
			},
		},
	}

	originalLen := len(req.Resources)
	err := req.CustomCheck()
	require.NoError(t, err)

	// After deduplication, should have 2 unique resources
	assert.Less(t, len(req.Resources), originalLen)
}

func TestAddResourcesReq_AllResourceTypes(t *testing.T) {
	req := &AddResourcesReq{
		Resources: []*SpaceResourceReq{
			{
				ResourceType: cdaenum.ResourceTypeDataAgent,
				ResourceID:   "agent-1",
			},
			{
				ResourceType: cdaenum.ResourceTypeDataAgentTpl,
				ResourceID:   "tpl-1",
			},
		},
	}

	err := req.CustomCheck()
	require.NoError(t, err)
	assert.Len(t, req.Resources, 2)
}
