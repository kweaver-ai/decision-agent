package bizdomainsvc

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/httpaccess/bizdomainhttp/bizdomainhttpreq"
	"github.com/stretchr/testify/assert"
)

func TestNewInitAllAgentToPublicBusinessDomainReq(t *testing.T) {
	t.Run("creates request with agent IDs", func(t *testing.T) {
		agentIDs := []string{"agent-1", "agent-2", "agent-3"}

		req := bizdomainhttpreq.NewInitAllAgentToPublicBusinessDomainReq(agentIDs)

		assert.NotNil(t, req)
		assert.NotEmpty(t, req)
		assert.Len(t, req, 3)

		// Verify each item in the slice has the correct agent ID
		for i, item := range req {
			assert.Equal(t, agentIDs[i], item.ID)
		}
	})

	t.Run("creates request with empty agent IDs", func(t *testing.T) {
		agentIDs := []string{}

		req := bizdomainhttpreq.NewInitAllAgentToPublicBusinessDomainReq(agentIDs)

		assert.NotNil(t, req)
		assert.Empty(t, req)
	})
}
