package bizdomainsvc

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service"
	"github.com/stretchr/testify/assert"
)

func TestNewBizDomainService_NilDTO(t *testing.T) {
	t.Run("handles nil DTO by panicking", func(t *testing.T) {
		// Passing nil DTO will cause a panic when dereferencing
		// This is expected behavior
		assert.Panics(t, func() {
			NewBizDomainService(nil)
		})
	})
}

func TestNewBizDomainService_WithAllDependencies(t *testing.T) {
	t.Run("creates service with all dependencies", func(t *testing.T) {
		dto := &NewBizDomainSvcDto{
			SvcBase:       service.NewSvcBase(),
			Logger:        nil,
			BizDomainHttp: nil,
		}

		svc := NewBizDomainService(dto)

		assert.NotNil(t, svc)
		assert.NotNil(t, svc.SvcBase)
	})
}

func TestNewBizDomainSvcDto_Struct(t *testing.T) {
	t.Run("create DTO struct", func(t *testing.T) {
		dto := &NewBizDomainSvcDto{
			SvcBase:       service.NewSvcBase(),
		}

		assert.NotNil(t, dto)
		assert.NotNil(t, dto.SvcBase)
	})
}

func TestBizDomainSvc_Struct(t *testing.T) {
	t.Run("create service struct directly", func(t *testing.T) {
		svc := &BizDomainSvc{}

		assert.NotNil(t, svc)
	})

	t.Run("create service with SvcBase", func(t *testing.T) {
		svc := &BizDomainSvc{
			SvcBase: service.NewSvcBase(),
		}

		assert.NotNil(t, svc)
		assert.NotNil(t, svc.SvcBase)
	})
}

func TestNewBizDomainService_MultipleInstances(t *testing.T) {
	t.Run("multiple service instances are independent", func(t *testing.T) {
		dto1 := &NewBizDomainSvcDto{
			SvcBase: service.NewSvcBase(),
		}
		dto2 := &NewBizDomainSvcDto{
			SvcBase: service.NewSvcBase(),
		}

		svc1 := NewBizDomainService(dto1)
		svc2 := NewBizDomainService(dto2)

		assert.NotNil(t, svc1)
		assert.NotNil(t, svc2)
		assert.NotSame(t, svc1, svc2)
	})
}

func TestFixMissingAgentTplRelResp_Struct(t *testing.T) {
	t.Run("create response struct", func(t *testing.T) {
		resp := &FixMissingAgentTplRelResp{
			FixedCount: 5,
			FixedIDs:   []int64{1, 2, 3, 4, 5},
		}

		assert.NotNil(t, resp)
		assert.Equal(t, 5, resp.FixedCount)
		assert.Len(t, resp.FixedIDs, 5)
	})

	t.Run("create empty response struct", func(t *testing.T) {
		resp := &FixMissingAgentTplRelResp{
			FixedCount: 0,
			FixedIDs:   []int64{},
		}

		assert.NotNil(t, resp)
		assert.Equal(t, 0, resp.FixedCount)
		assert.Empty(t, resp.FixedIDs)
	})

	t.Run("create response with nil FixedIDs", func(t *testing.T) {
		resp := &FixMissingAgentTplRelResp{
			FixedCount: 0,
			FixedIDs:   nil,
		}

		assert.NotNil(t, resp)
		assert.Equal(t, 0, resp.FixedCount)
		assert.Nil(t, resp.FixedIDs)
	})
}
