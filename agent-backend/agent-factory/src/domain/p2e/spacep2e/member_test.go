package spacep2e

import (
	"context"
	"errors"
	"os"
	"testing"

	"go.uber.org/mock/gomock"
	"github.com/kweaver-ai/decision-agent/agent-factory/locale"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/entity/spaceeo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/ihttpaccess/iumacc/httpaccmock"
	"github.com/kweaver-ai/kweaver-go-lib/rest"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestMain(m *testing.M) {
	// Setup environment for local dev mode (only once)
	os.Setenv("SERVICE_NAME", "AGENT_FACTORY")
	os.Setenv("AGENT_FACTORY_LOCAL_DEV", "true")
	os.Setenv("I18N_MODE_UT", "true")

	// Initialize locale (only once)
	locale.Register()

	// Run tests
	code := m.Run()
	os.Exit(code)
}

func TestSpaceMember(t *testing.T) {
	ctx := context.Background()

	tests := []struct {
		name    string
		po      *dapo.SpaceMemberPo
		wantErr bool
		checkEO func(t *testing.T, eo *spaceeo.SpaceMember)
	}{
		{
			name: "valid space member PO",
			po: &dapo.SpaceMemberPo{
				ID:       1,
				SpaceID:  "space-1",
				SpaceKey: "space-key-1",
				ObjType:  cenum.OrgObjTypeUser,
				ObjID:    "user-1",
			},
			wantErr: false,
			checkEO: func(t *testing.T, eo *spaceeo.SpaceMember) {
				assert.Equal(t, int64(1), eo.ID)
				assert.Equal(t, "space-1", eo.SpaceID)
				assert.Equal(t, "space-key-1", eo.SpaceKey)
				assert.Equal(t, cenum.OrgObjTypeUser, eo.ObjType)
				assert.Equal(t, "user-1", eo.ObjID)
			},
		},
		{
			name: "space member with department",
			po: &dapo.SpaceMemberPo{
				ID:       2,
				SpaceID:  "space-1",
				ObjType:  cenum.OrgObjTypeDep,
				ObjID:    "dept-1",
			},
			wantErr: false,
			checkEO: func(t *testing.T, eo *spaceeo.SpaceMember) {
				assert.Equal(t, int64(2), eo.ID)
				assert.Equal(t, cenum.OrgObjTypeDep, eo.ObjType)
			},
		},
		{
			name: "space member with group",
			po: &dapo.SpaceMemberPo{
				ID:       3,
				SpaceID:  "space-1",
				ObjType:  cenum.OrgObjTypeGroup,
				ObjID:    "group-1",
			},
			wantErr: false,
			checkEO: func(t *testing.T, eo *spaceeo.SpaceMember) {
				assert.Equal(t, int64(3), eo.ID)
				assert.Equal(t, cenum.OrgObjTypeGroup, eo.ObjType)
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			eo, err := SpaceMember(ctx, tt.po)
			if tt.wantErr {
				assert.Error(t, err)
			} else {
				require.NoError(t, err)
				if tt.checkEO != nil {
					tt.checkEO(t, eo)
				}
			}
		})
	}
}

func TestSpaceMembers_EmptyList(t *testing.T) {
	ctx := context.WithValue(context.Background(), cenum.VisitLangCtxKey.String(), rest.SimplifiedChinese)
	pos := []*dapo.SpaceMemberPo{}

	eos, err := SpaceMembers(ctx, pos, nil)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 0)
}

func TestSpaceMembers_SingleUser(t *testing.T) {
	ctx := context.WithValue(context.Background(), cenum.VisitLangCtxKey.String(), rest.SimplifiedChinese)
	pos := []*dapo.SpaceMemberPo{
		{ID: 1, SpaceID: "space-1", ObjType: cenum.OrgObjTypeUser, ObjID: "user-1"},
	}

	eos, err := SpaceMembers(ctx, pos, nil)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 1)
	assert.Equal(t, "user-1_name", eos[0].ObjName)
}

func TestSpaceMembers_MultipleUsers(t *testing.T) {
	ctx := context.WithValue(context.Background(), cenum.VisitLangCtxKey.String(), rest.SimplifiedChinese)
	pos := []*dapo.SpaceMemberPo{
		{ID: 1, SpaceID: "space-1", ObjType: cenum.OrgObjTypeUser, ObjID: "user-1"},
		{ID: 2, SpaceID: "space-1", ObjType: cenum.OrgObjTypeUser, ObjID: "user-2"},
		{ID: 3, SpaceID: "space-1", ObjType: cenum.OrgObjTypeUser, ObjID: "user-3"},
	}

	eos, err := SpaceMembers(ctx, pos, nil)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 3)
	assert.Equal(t, "user-1_name", eos[0].ObjName)
	assert.Equal(t, "user-2_name", eos[1].ObjName)
	assert.Equal(t, "user-3_name", eos[2].ObjName)
}

func TestSpaceMembers_DepartmentAndGroup(t *testing.T) {
	ctx := context.WithValue(context.Background(), cenum.VisitLangCtxKey.String(), rest.SimplifiedChinese)
	pos := []*dapo.SpaceMemberPo{
		{ID: 1, SpaceID: "space-1", ObjType: cenum.OrgObjTypeUser, ObjID: "user-1"},
		{ID: 2, SpaceID: "space-1", ObjType: cenum.OrgObjTypeDep, ObjID: "dept-1"},
		{ID: 3, SpaceID: "space-1", ObjType: cenum.OrgObjTypeGroup, ObjID: "group-1"},
	}

	eos, err := SpaceMembers(ctx, pos, nil)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 3)
	assert.Equal(t, "user-1_name", eos[0].ObjName)
	assert.Equal(t, "dept-1_name", eos[1].ObjName)
	assert.Equal(t, "group-1_name", eos[2].ObjName)
}

func TestSpaceMembers_MixedTypes(t *testing.T) {
	ctx := context.WithValue(context.Background(), cenum.VisitLangCtxKey.String(), rest.SimplifiedChinese)
	pos := []*dapo.SpaceMemberPo{
		{ID: 1, SpaceID: "space-1", ObjType: cenum.OrgObjTypeUser, ObjID: "user-1"},
		{ID: 2, SpaceID: "space-1", ObjType: cenum.OrgObjTypeDep, ObjID: "dept-1"},
		{ID: 3, SpaceID: "space-1", ObjType: cenum.OrgObjTypeUser, ObjID: "user-2"},
		{ID: 4, SpaceID: "space-1", ObjType: cenum.OrgObjTypeGroup, ObjID: "group-1"},
	}

	eos, err := SpaceMembers(ctx, pos, nil)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 4)
	assert.Equal(t, "user-1_name", eos[0].ObjName)
	assert.Equal(t, "dept-1_name", eos[1].ObjName)
	assert.Equal(t, "user-2_name", eos[2].ObjName)
	assert.Equal(t, "group-1_name", eos[3].ObjName)
}

func TestSpaceMembers_NonLocalDevModeError(t *testing.T) {
	// Temporarily unset local dev mode for this test
	originalValue := os.Getenv("AGENT_FACTORY_LOCAL_DEV")
	os.Unsetenv("AGENT_FACTORY_LOCAL_DEV")
	defer func() {
		if originalValue != "" {
			os.Setenv("AGENT_FACTORY_LOCAL_DEV", originalValue)
		}
	}()

	ctx := context.WithValue(context.Background(), cenum.VisitLangCtxKey.String(), rest.SimplifiedChinese)
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mockUmHttp := httpaccmock.NewMockUmHttpAcc(ctrl)

	pos := []*dapo.SpaceMemberPo{
		{ID: 1, SpaceID: "space-1", ObjType: cenum.OrgObjTypeUser, ObjID: "user-1"},
	}

	// Expect GetOsnNames to return an error
	mockUmHttp.EXPECT().GetOsnNames(ctx, gomock.Any()).Return(nil, errors.New("network error"))

	eos, err := SpaceMembers(ctx, pos, mockUmHttp)

	assert.Error(t, err)
	assert.Contains(t, err.Error(), "network error")
	// eos may be non-nil but empty slice on error
	assert.Empty(t, eos)
}
