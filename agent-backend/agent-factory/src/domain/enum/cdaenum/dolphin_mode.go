package cdaenum

import "github.com/pkg/errors"

// DolphinMode 是否是dolphin模式
type DolphinMode int

func (d DolphinMode) EnumCheck() (err error) {
	if d < DolphinModeDisabled || d > DolphinModeEnabled {
		err = errors.New("dolphin模式不合法")
		return
	}

	return
}

func (d DolphinMode) Bool() bool {
	if d == DolphinModeEnabled {
		return true
	}

	return false
}

const (
	// DolphinModeDisabled 禁用dolphin模式
	DolphinModeDisabled DolphinMode = 0

	// DolphinModeEnabled 启用dolphin模式
	DolphinModeEnabled DolphinMode = 1
)
