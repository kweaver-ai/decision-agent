package ctype

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cenum"
	"github.com/stretchr/testify/assert"
)

func TestVisitorInfo_StructFields(t *testing.T) {
	info := &VisitorInfo{
		XAccountID:        "account-123",
		XAccountType:      cenum.AccountTypeUser,
		XBusinessDomainID: cenum.BizDomainPublic,
	}

	assert.Equal(t, "account-123", info.XAccountID)
	assert.Equal(t, cenum.AccountTypeUser, info.XAccountType)
	assert.Equal(t, cenum.BizDomainPublic, info.XBusinessDomainID)
}

func TestVisitorInfo_EmptyValues(t *testing.T) {
	info := &VisitorInfo{}

	assert.Empty(t, info.XAccountID)
	assert.Equal(t, cenum.AccountType(""), info.XAccountType)
	assert.Equal(t, cenum.BizDomainID(""), info.XBusinessDomainID)
}

func TestVisitorInfo_WithOnlyAccountID(t *testing.T) {
	info := &VisitorInfo{
		XAccountID: "account-456",
	}

	assert.Equal(t, "account-456", info.XAccountID)
	assert.Empty(t, string(info.XAccountType))
	assert.Empty(t, string(info.XBusinessDomainID))
}

func TestVisitorInfo_WithAppAccountType(t *testing.T) {
	info := &VisitorInfo{
		XAccountID:   "app-account",
		XAccountType: cenum.AccountTypeApp,
	}

	assert.Equal(t, "app-account", info.XAccountID)
	assert.Equal(t, cenum.AccountTypeApp, info.XAccountType)
}

func TestVisitorInfo_WithAnonymousAccountType(t *testing.T) {
	info := &VisitorInfo{
		XAccountID:   "anonymous",
		XAccountType: cenum.AccountTypeAnonymous,
	}

	assert.Equal(t, "anonymous", info.XAccountID)
	assert.Equal(t, cenum.AccountTypeAnonymous, info.XAccountType)
}
