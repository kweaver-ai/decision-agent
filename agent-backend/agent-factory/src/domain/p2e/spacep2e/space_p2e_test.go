package spacep2e

import (
	"context"
	"errors"
	"os"
	"testing"

	"go.uber.org/mock/gomock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/entity/spaceeo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/ihttpaccess/iumacc/httpaccmock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/cmp/umcmp/umtypes"
	"github.com/kweaver-ai/kweaver-go-lib/rest"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestSpace(t *testing.T) {
	ctx := context.WithValue(context.Background(), cenum.VisitLangCtxKey.String(), rest.SimplifiedChinese)

	tests := []struct {
		name    string
		po      *dapo.SpacePo
		wantErr bool
		checkEO func(t *testing.T, eo *spaceeo.Space)
	}{
		{
			name: "valid space PO",
			po: &dapo.SpacePo{
				ID:          "space-1",
				Name:        "Test Space",
				Key:         "test-space",
				Profile:     "Test Description",
				CreatedBy:   "user-1",
				CreatedAt:   1234567890,
				UpdatedBy:   "user-2",
				UpdatedAt:   1234567891,
			},
			wantErr: false,
			checkEO: func(t *testing.T, eo *spaceeo.Space) {
				assert.Equal(t, "space-1", eo.ID)
				assert.Equal(t, "Test Space", eo.Name)
				assert.Equal(t, "test-space", eo.Key)
				assert.Equal(t, "Test Description", eo.Profile)
				assert.Equal(t, "user-1", eo.CreatedBy)
				assert.Equal(t, int64(1234567890), eo.CreatedAt)
			},
		},
		{
			name: "space PO with minimal fields",
			po: &dapo.SpacePo{
				ID:   "space-2",
				Name: "Minimal Space",
			},
			wantErr: false,
			checkEO: func(t *testing.T, eo *spaceeo.Space) {
				assert.Equal(t, "space-2", eo.ID)
				assert.Equal(t, "Minimal Space", eo.Name)
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			eo, err := Space(ctx, tt.po)
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

func TestSpaces_EmptyList(t *testing.T) {
	ctx := context.WithValue(context.Background(), cenum.VisitLangCtxKey.String(), rest.SimplifiedChinese)
	pos := []*dapo.SpacePo{}

	eos, err := Spaces(ctx, pos, nil)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 0)
}

func TestSpaces_SingleItem(t *testing.T) {
	ctx := context.WithValue(context.Background(), cenum.VisitLangCtxKey.String(), rest.SimplifiedChinese)
	pos := []*dapo.SpacePo{
		{ID: "space-1", Name: "Test Space", CreatedBy: "user-1", UpdatedBy: "user-2"},
	}

	eos, err := Spaces(ctx, pos, nil)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 1)
	assert.Equal(t, "space-1", eos[0].ID)
	assert.Contains(t, eos[0].CreatedByName, "user-1")
	assert.Contains(t, eos[0].UpdatedByName, "user-2")
}

func TestSpaces_MultipleItems(t *testing.T) {
	ctx := context.WithValue(context.Background(), cenum.VisitLangCtxKey.String(), rest.SimplifiedChinese)
	pos := []*dapo.SpacePo{
		{ID: "space-1", Name: "Space 1", CreatedBy: "user-1", UpdatedBy: "user-2"},
		{ID: "space-2", Name: "Space 2", CreatedBy: "user-3", UpdatedBy: "user-4"},
		{ID: "space-3", Name: "Space 3", CreatedBy: "user-5", UpdatedBy: "user-6"},
	}

	eos, err := Spaces(ctx, pos, nil)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 3)
	assert.Equal(t, "user-1_name", eos[0].CreatedByName)
	assert.Equal(t, "user-2_name", eos[0].UpdatedByName)
	assert.Equal(t, "user-3_name", eos[1].CreatedByName)
	assert.Equal(t, "user-4_name", eos[1].UpdatedByName)
	assert.Equal(t, "user-5_name", eos[2].CreatedByName)
	assert.Equal(t, "user-6_name", eos[2].UpdatedByName)
}

func TestSpaces_WithEmptyCreatedBy(t *testing.T) {
	ctx := context.WithValue(context.Background(), cenum.VisitLangCtxKey.String(), rest.SimplifiedChinese)
	pos := []*dapo.SpacePo{
		{ID: "space-1", Name: "Space 1", CreatedBy: "", UpdatedBy: "user-1"},
	}

	eos, err := Spaces(ctx, pos, nil)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 1)
	assert.Empty(t, eos[0].CreatedByName)
	assert.Equal(t, "user-1_name", eos[0].UpdatedByName)
}

func TestSpaces_NonLocalDevMode(t *testing.T) {
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

	pos := []*dapo.SpacePo{
		{ID: "space-1", Name: "Test Space", CreatedBy: "user-1", UpdatedBy: "user-2"},
	}

	// Expect GetOsnNames to be called in non-local dev mode
	osnInfoMap := umtypes.NewOsnInfoMapS()
	osnInfoMap.UserNameMap["user-1"] = "Real User 1"
	osnInfoMap.UserNameMap["user-2"] = "Real User 2"
	mockUmHttp.EXPECT().GetOsnNames(ctx, gomock.Any()).Return(osnInfoMap, nil)

	eos, err := Spaces(ctx, pos, mockUmHttp)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 1)
	// In non-local dev mode, real user names should be used
	assert.Equal(t, "Real User 1", eos[0].CreatedByName)
	assert.Equal(t, "Real User 2", eos[0].UpdatedByName)
}

func TestSpaces_UnknownUserName(t *testing.T) {
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

	pos := []*dapo.SpacePo{
		{ID: "space-1", Name: "Test Space", CreatedBy: "unknown_user", UpdatedBy: "user-2"},
	}

	// Return user info map that doesn't include "unknown_user"
	osnInfoMap := umtypes.NewOsnInfoMapS()
	osnInfoMap.UserNameMap["user-2"] = "Real User 2"
	mockUmHttp.EXPECT().GetOsnNames(ctx, gomock.Any()).Return(osnInfoMap, nil)

	eos, err := Spaces(ctx, pos, mockUmHttp)

	assert.NoError(t, err)
	assert.NotNil(t, eos)
	assert.Len(t, eos, 1)
	// Unknown user should get the "unknown" placeholder
	assert.NotEmpty(t, eos[0].CreatedByName)
	assert.Equal(t, "Real User 2", eos[0].UpdatedByName)
}

func TestSpaces_NonLocalDevModeError(t *testing.T) {
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

	pos := []*dapo.SpacePo{
		{ID: "space-1", Name: "Test Space", CreatedBy: "user-1", UpdatedBy: "user-2"},
	}

	// Expect GetOsnNames to return an error
	mockUmHttp.EXPECT().GetOsnNames(ctx, gomock.Any()).Return(nil, errors.New("network error"))

	eos, err := Spaces(ctx, pos, mockUmHttp)

	assert.Error(t, err)
	assert.Contains(t, err.Error(), "network error")
	// eos may be non-nil but empty slice on error
	assert.Empty(t, eos)
}
