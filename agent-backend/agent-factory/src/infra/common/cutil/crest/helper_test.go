package crest

import (
	"context"
	"errors"
	"net/http"
	"testing"

	"github.com/kweaver-ai/kweaver-go-lib/rest"
	"github.com/stretchr/testify/assert"
)

func TestGetRestHttpErr(t *testing.T) {
	t.Run("nil错误", func(t *testing.T) {
		httpError, b := GetRestHttpErr(nil)
		assert.Nil(t, httpError)
		assert.False(t, b)
	})

	t.Run("普通错误", func(t *testing.T) {
		err := errors.New("normal error")
		httpError, b := GetRestHttpErr(err)
		assert.Nil(t, httpError)
		assert.False(t, b)
	})

	t.Run("HTTP错误", func(t *testing.T) {
		err := rest.NewHTTPError(context.Background(), http.StatusBadRequest, rest.PublicError_BadRequest)
		httpError, b := GetRestHttpErr(err)
		assert.NotNil(t, httpError)
		assert.True(t, b)
		assert.Equal(t, err, httpError, "should return same error")
	})
}
