package ctype

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cenum"
)

func TestVisitorInfo(t *testing.T) {
	t.Run("create visitor info", func(t *testing.T) {
		info := &VisitorInfo{
			XAccountID:        "account-123",
			XAccountType:      cenum.AccountTypeUser,
			XBusinessDomainID: "kweaver",
		}

		if info.XAccountID != "account-123" {
			t.Errorf("Expected XAccountID to be 'account-123', got '%s'", info.XAccountID)
		}
		if info.XAccountType != cenum.AccountTypeUser {
			t.Errorf("Expected XAccountType to be User, got %v", info.XAccountType)
		}
		if info.XBusinessDomainID != "kweaver" {
			t.Errorf("Expected XBusinessDomainID to be 'kweaver', got %v", info.XBusinessDomainID)
		}
	})

	t.Run("zero value visitor info", func(t *testing.T) {
		var info VisitorInfo

		if info.XAccountID != "" {
			t.Errorf("Expected XAccountID to be empty, got '%s'", info.XAccountID)
		}
		if info.XAccountType != "" {
			t.Errorf("Expected XAccountType to be empty, got '%s'", info.XAccountType)
		}
		if info.XBusinessDomainID != "" {
			t.Errorf("Expected XBusinessDomainID to be empty, got '%s'", info.XBusinessDomainID)
		}
	})

	t.Run("visitor info with anonymous account", func(t *testing.T) {
		info := &VisitorInfo{
			XAccountID:        "",
			XAccountType:      cenum.AccountTypeAnonymous,
			XBusinessDomainID: "",
		}

		if info.XAccountType != cenum.AccountTypeAnonymous {
			t.Errorf("Expected XAccountType to be Anonymous, got %v", info.XAccountType)
		}
	})

	t.Run("visitor info with app account", func(t *testing.T) {
		info := &VisitorInfo{
			XAccountID:        "app-123",
			XAccountType:      cenum.AccountTypeApp,
			XBusinessDomainID: "custom",
		}

		if info.XAccountType != cenum.AccountTypeApp {
			t.Errorf("Expected XAccountType to be App, got %v", info.XAccountType)
		}
		if info.XBusinessDomainID != "custom" {
			t.Errorf("Expected XBusinessDomainID to be 'custom', got %v", info.XBusinessDomainID)
		}
	})
}

