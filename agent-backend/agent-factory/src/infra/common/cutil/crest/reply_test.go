package crest

import (
	"errors"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/kweaver-ai/kweaver-go-lib/rest"
	"github.com/stretchr/testify/assert"
)

func TestReplyError2(t *testing.T) {
	gin.SetMode(gin.TestMode)

	t.Run("GetRestHttpErr_with_nil", func(t *testing.T) {
		restErr, ok := GetRestHttpErr(nil)

		assert.False(t, ok, "GetRestHttpErr should return false for nil error")
		assert.Nil(t, restErr, "GetRestHttpErr should return nil for nil error")
	})

	t.Run("GetRestHttpErr_with_regular_error", func(t *testing.T) {
		regularErr := errors.New("regular error")
		restErr, ok := GetRestHttpErr(regularErr)

		assert.False(t, ok, "GetRestHttpErr should return false for regular error")
		assert.Nil(t, restErr, "GetRestHttpErr should return nil for regular error")
	})

	t.Run("GetRestHttpErr_with_HTTPError", func(t *testing.T) {
		w := httptest.NewRecorder()
		c, _ := gin.CreateTestContext(w)
		c.Request = &http.Request{}

		httpErr := rest.NewHTTPError(c.Request.Context(), http.StatusBadRequest, rest.PublicError_BadRequest)
		err, ok := GetRestHttpErr(httpErr)

		assert.True(t, ok, "GetRestHttpErr should return true for HTTPError")
		assert.NotNil(t, err, "GetRestHttpErr should return non-nil error")
	})

	t.Run("GetRestHttpErr_with_HTTPError_Unauthorized", func(t *testing.T) {
		w := httptest.NewRecorder()
		c, _ := gin.CreateTestContext(w)
		c.Request = &http.Request{}

		httpErr := rest.NewHTTPError(c.Request.Context(), http.StatusUnauthorized, rest.PublicError_Unauthorized)
		err, ok := GetRestHttpErr(httpErr)

		assert.True(t, ok, "GetRestHttpErr should return true for HTTPError")
		assert.NotNil(t, err, "GetRestHttpErr should return non-nil error")
	})
}
