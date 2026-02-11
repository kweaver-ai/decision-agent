package releasesvc

import (
	"testing"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/service"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/idbaccess/idbaccessmock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/ihttpaccess/iauthzacc/authzaccmock"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/port/driven/ihttpaccess/iumacc/httpaccmock"
	"github.com/stretchr/testify/assert"
	"go.uber.org/mock/gomock"
)

func TestNewReleaseService_AdditionalCases(t *testing.T) {
	t.Run("creates service with partial dependencies", func(t *testing.T) {
		ctrl := gomock.NewController(t)
		defer ctrl.Finish()

		dto := &NewReleaseSvcDto{
			SvcBase:             service.NewSvcBase(),
			ReleaseRepo:         idbaccessmock.NewMockIReleaseRepo(ctrl),
			ReleaseHistoryRepo:  idbaccessmock.NewMockIReleaseHistoryRepo(ctrl),
			AgentConfigRepo:     nil,
			ReleaseCategoryRepo: nil,
			ReleasePermissionRepo: nil,
			CategoryRepo:        nil,
			SpaceResourceRepo:   nil,
			UmHttp:              httpaccmock.NewMockUmHttpAcc(ctrl),
			AuthZHttp:           authzaccmock.NewMockAuthZHttpAcc(ctrl),
		}

		svc := NewReleaseService(dto)

		assert.NotNil(t, svc)
		assert.IsType(t, &releaseSvc{}, svc)
	})

	t.Run("creates service with only SvcBase", func(t *testing.T) {
		dto := &NewReleaseSvcDto{
			SvcBase: service.NewSvcBase(),
		}

		svc := NewReleaseService(dto)

		assert.NotNil(t, svc)
		assert.IsType(t, &releaseSvc{}, svc)
	})

	t.Run("creates service with nil SvcBase", func(t *testing.T) {
		dto := &NewReleaseSvcDto{
			SvcBase: nil,
		}

		svc := NewReleaseService(dto)

		assert.NotNil(t, svc)
		assert.IsType(t, &releaseSvc{}, svc)
	})

	t.Run("creates service with all HTTP clients", func(t *testing.T) {
		ctrl := gomock.NewController(t)
		defer ctrl.Finish()

		dto := &NewReleaseSvcDto{
			SvcBase:             service.NewSvcBase(),
			ReleaseRepo:         nil,
			ReleaseHistoryRepo:  nil,
			AgentConfigRepo:     nil,
			ReleaseCategoryRepo: nil,
			ReleasePermissionRepo: nil,
			CategoryRepo:        nil,
			SpaceResourceRepo:   nil,
			UmHttp:              httpaccmock.NewMockUmHttpAcc(ctrl),
			AuthZHttp:           authzaccmock.NewMockAuthZHttpAcc(ctrl),
		}

		svc := NewReleaseService(dto)

		assert.NotNil(t, svc)
		assert.IsType(t, &releaseSvc{}, svc)
	})

	t.Run("creates service with all repository mocks", func(t *testing.T) {
		ctrl := gomock.NewController(t)
		defer ctrl.Finish()

		dto := &NewReleaseSvcDto{
			SvcBase:                service.NewSvcBase(),
			ReleaseRepo:            idbaccessmock.NewMockIReleaseRepo(ctrl),
			ReleaseHistoryRepo:     idbaccessmock.NewMockIReleaseHistoryRepo(ctrl),
			AgentConfigRepo:        idbaccessmock.NewMockIDataAgentConfigRepo(ctrl),
			ReleaseCategoryRepo:    idbaccessmock.NewMockIReleaseCategoryRelRepo(ctrl),
			ReleasePermissionRepo:  idbaccessmock.NewMockIReleasePermissionRepo(ctrl),
			CategoryRepo:           idbaccessmock.NewMockICategoryRepo(ctrl),
			SpaceResourceRepo:      idbaccessmock.NewMockISpaceResourceRepo(ctrl),
		}

		svc := NewReleaseService(dto)

		assert.NotNil(t, svc)
		assert.IsType(t, &releaseSvc{}, svc)
	})
}

func TestReleaseSvc_Interface(t *testing.T) {
	t.Run("implements IReleaseSvc interface", func(t *testing.T) {
		ctrl := gomock.NewController(t)
		defer ctrl.Finish()

		dto := &NewReleaseSvcDto{
			SvcBase: service.NewSvcBase(),
		}

		svc := NewReleaseService(dto)

		// Verify the service is not nil and has the expected type
		assert.NotNil(t, svc)
		assert.IsType(t, &releaseSvc{}, svc)
	})
}

func TestNewReleaseSvcDto_Structure(t *testing.T) {
	t.Run("creates DTO with all fields", func(t *testing.T) {
		ctrl := gomock.NewController(t)
		defer ctrl.Finish()

		dto := &NewReleaseSvcDto{
			SvcBase:                service.NewSvcBase(),
			ReleaseRepo:            idbaccessmock.NewMockIReleaseRepo(ctrl),
			ReleaseHistoryRepo:     idbaccessmock.NewMockIReleaseHistoryRepo(ctrl),
			AgentConfigRepo:        idbaccessmock.NewMockIDataAgentConfigRepo(ctrl),
			ReleaseCategoryRepo:    idbaccessmock.NewMockIReleaseCategoryRelRepo(ctrl),
			ReleasePermissionRepo:  idbaccessmock.NewMockIReleasePermissionRepo(ctrl),
			CategoryRepo:           idbaccessmock.NewMockICategoryRepo(ctrl),
			SpaceResourceRepo:      idbaccessmock.NewMockISpaceResourceRepo(ctrl),
			UmHttp:                 httpaccmock.NewMockUmHttpAcc(ctrl),
			AuthZHttp:              authzaccmock.NewMockAuthZHttpAcc(ctrl),
		}

		assert.NotNil(t, dto)
		assert.NotNil(t, dto.SvcBase)
	})

	t.Run("creates DTO with nil fields", func(t *testing.T) {
		dto := &NewReleaseSvcDto{}

		assert.NotNil(t, dto)
		assert.Nil(t, dto.SvcBase)
		assert.Nil(t, dto.ReleaseRepo)
		assert.Nil(t, dto.ReleaseHistoryRepo)
	})
}
