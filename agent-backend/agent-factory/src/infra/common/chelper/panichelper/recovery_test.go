package panichelper

import (
	"errors"
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/cmp/icmp"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/cmp/icmp/cmpmock"

	//"github.com/kweaver-ai/decision-agent/agent-factory/test/mock_log"
	"go.uber.org/mock/gomock"

	"github.com/stretchr/testify/assert"
)

func ForRecovery(logger icmp.Logger) {
	defer Recovery(logger)
	panic("test Recovery")
}

//func TestRecovery(t *testing.T) {
//	ctl := gomock.NewController(t)
//	logger := cmpmock.NewMockLogger(ctl)
//	logger.EXPECT().Errorln(gomock.Any()).DoAndReturn(func(args ...interface{}) interface{} {
//		t.Log(args...)
//		return nil
//	})
//
//	ForRecovery(logger)
//}

func ForRecoveryAndSetErr(logger icmp.Logger, err *error) {
	defer RecoveryAndSetErr(logger, err)
	panic("test RecoveryAndSetErr")
}

func TestRecoveryAndSetErr(t *testing.T) {
	ctl := gomock.NewController(t)
	logger := cmpmock.NewMockLogger(ctl)
	logger.EXPECT().Errorln(gomock.Any()).DoAndReturn(func(args ...interface{}) interface{} {
		t.Log(args...)
		return nil
	})

	var err error

	ForRecoveryAndSetErr(logger, &err)

	// 1.检查err的值是否是"test RecoveryAndSetErr"
	assert.Equal(t, "test RecoveryAndSetErr", err.Error())
}

type customErr struct {
	msg string
}

func (c *customErr) Error() string {
	return c.msg
}

func ForRecoveryAndSetErrCustomErr(logger icmp.Logger, err *error) {
	defer RecoveryAndSetErr(logger, err)

	_err := &customErr{msg: "test RecoveryAndSetErr2"}
	panic(_err)
}

func TestRecoveryAndSetErrCustomErr(t *testing.T) {
	ctl := gomock.NewController(t)
	logger := cmpmock.NewMockLogger(ctl)
	logger.EXPECT().Errorln(gomock.Any()).DoAndReturn(func(args ...interface{}) interface{} {
		t.Log(args...)
		return nil
	})

	var err error

	ForRecoveryAndSetErrCustomErr(logger, &err)

	// 1.检查err的值是否是"test RecoveryAndSetErr2"
	assert.Equal(t, "test RecoveryAndSetErr2", err.Error())

	// 2.检查err是否是customErr类型
	var _customErr *customErr
	ok := errors.As(err, &_customErr)
	assert.True(t, ok)
	assert.Equal(t, "test RecoveryAndSetErr2", _customErr.msg)
}
