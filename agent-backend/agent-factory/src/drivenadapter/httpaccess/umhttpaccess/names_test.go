package umhttpaccess

import (
	"context"
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/cmp/icmp/cmpmock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/cmp/umcmp"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/cmp/umcmp/dto/umarg"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/cmp/umcmp/umtypes"
	"github.com/pkg/errors"
	"github.com/stretchr/testify/assert"
	"go.uber.org/mock/gomock"
)

// mockUmClient implements umClient for testing.
type mockUmClient struct {
	getOsnNamesSFGFn func(ctx context.Context, args *umarg.GetOsnArgDto) (*umtypes.OsnInfoMapS, error)
}

func (m *mockUmClient) GetOsnNamesSFG(ctx context.Context, args *umarg.GetOsnArgDto) (*umtypes.OsnInfoMapS, error) {
	return m.getOsnNamesSFGFn(ctx, args)
}

func (m *mockUmClient) GetUserDeptIDs(_ context.Context, _ string) ([]string, error) {
	return nil, nil
}

func (m *mockUmClient) GetDeptInfoMap(_ context.Context, _ *umarg.GetDeptInfoArgDto) (map[string]*umtypes.DepartmentInfo, error) {
	return nil, nil
}

func (m *mockUmClient) GetUserDept(_ context.Context, _ string) ([][]umcmp.ObjectBaseInfo, error) {
	return nil, nil
}

func (m *mockUmClient) GetUserInfo(_ context.Context, _ *umarg.GetUserInfoArgDto) (umcmp.UserInfoMap, error) {
	return nil, nil
}

func allowAnyLoggerCalls(mockLogger *cmpmock.MockLogger) {
	mockLogger.EXPECT().Debugf(gomock.Any(), gomock.Any()).AnyTimes()
	mockLogger.EXPECT().Infof(gomock.Any(), gomock.Any()).AnyTimes()
	mockLogger.EXPECT().Warnf(gomock.Any(), gomock.Any()).AnyTimes()
	mockLogger.EXPECT().Errorf(gomock.Any(), gomock.Any()).AnyTimes()
	mockLogger.EXPECT().Infoln(gomock.Any()).AnyTimes()
	mockLogger.EXPECT().Warnln(gomock.Any()).AnyTimes()
	mockLogger.EXPECT().Errorln(gomock.Any()).AnyTimes()
}

func newTestUmHttpAcc(ctrl *gomock.Controller, client umClient) *umHttpAcc {
	mockLogger := cmpmock.NewMockLogger(ctrl)
	allowAnyLoggerCalls(mockLogger)

	return &umHttpAcc{
		um:     client,
		logger: mockLogger,
	}
}

// TestGetUserIDNameMap_NilReturn verifies that GetUserIDNameMap does not panic
// when GetOsnNames returns (nil, nil).
func TestGetUserIDNameMap_NilReturn(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mock := &mockUmClient{
		getOsnNamesSFGFn: func(_ context.Context, _ *umarg.GetOsnArgDto) (*umtypes.OsnInfoMapS, error) {
			return nil, nil // UM returns no data and no error
		},
	}

	acc := newTestUmHttpAcc(ctrl, mock)
	idNameMap, err := acc.GetUserIDNameMap(context.Background(), []string{"user-1"})

	assert.NoError(t, err)
	assert.NotNil(t, idNameMap)
	assert.Empty(t, idNameMap)
}

// TestGetUserIDNameMap_Success verifies normal case.
func TestGetUserIDNameMap_Success(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mock := &mockUmClient{
		getOsnNamesSFGFn: func(_ context.Context, _ *umarg.GetOsnArgDto) (*umtypes.OsnInfoMapS, error) {
			return &umtypes.OsnInfoMapS{
				UserNameMap: map[string]string{
					"user-1": "Alice",
					"user-2": "Bob",
				},
			}, nil
		},
	}

	acc := newTestUmHttpAcc(ctrl, mock)
	idNameMap, err := acc.GetUserIDNameMap(context.Background(), []string{"user-1", "user-2"})

	assert.NoError(t, err)
	assert.Equal(t, "Alice", idNameMap["user-1"])
	assert.Equal(t, "Bob", idNameMap["user-2"])
}

// TestGetUserIDNameMap_Error verifies error propagation.
func TestGetUserIDNameMap_Error(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mock := &mockUmClient{
		getOsnNamesSFGFn: func(_ context.Context, _ *umarg.GetOsnArgDto) (*umtypes.OsnInfoMapS, error) {
			return nil, errors.New("um service unavailable")
		},
	}

	acc := newTestUmHttpAcc(ctrl, mock)
	idNameMap, err := acc.GetUserIDNameMap(context.Background(), []string{"user-1"})

	assert.Error(t, err)
	assert.Nil(t, idNameMap)
	assert.Contains(t, err.Error(), "um service unavailable")
}

// TestGetSingleUserName_NilReturn verifies that GetSingleUserName does not panic
// when the underlying GetUserIDNameMap returns nil map (via nil OsnInfoMapS).
func TestGetSingleUserName_NilReturn(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	mock := &mockUmClient{
		getOsnNamesSFGFn: func(_ context.Context, _ *umarg.GetOsnArgDto) (*umtypes.OsnInfoMapS, error) {
			return nil, nil
		},
	}

	acc := newTestUmHttpAcc(ctrl, mock)
	name, err := acc.GetSingleUserName(context.Background(), "user-1")

	assert.NoError(t, err)
	assert.Empty(t, name)
}
