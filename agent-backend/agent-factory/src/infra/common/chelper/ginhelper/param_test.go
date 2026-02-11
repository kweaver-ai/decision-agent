package ginhelper

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
)

func TestGetParmID(t *testing.T) {
	t.Run("returns id from context", func(t *testing.T) {
		gin.SetMode(gin.TestMode)
		router := gin.New()
		
		router.GET("/test/:id", func(c *gin.Context) {
			id, err := GetParmID(c)
			assert.NoError(t, err)
			assert.Equal(t, "123", id)
			c.JSON(http.StatusOK, gin.H{"id": id})
		})
		
		req := httptest.NewRequest("GET", "/test/123", nil)
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusOK, w.Code)
	})
	
	t.Run("returns error when id is empty", func(t *testing.T) {
		gin.SetMode(gin.TestMode)
		router := gin.New()
		
		router.GET("/test", func(c *gin.Context) {
			id, err := GetParmID(c)
			assert.Error(t, err)
			assert.Empty(t, id)
		})
		
		req := httptest.NewRequest("GET", "/test", nil)
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)
	})
}

func TestGetParmInt64(t *testing.T) {
	t.Run("returns int64 id from context", func(t *testing.T) {
		gin.SetMode(gin.TestMode)
		router := gin.New()
		
		router.GET("/test/:id", func(c *gin.Context) {
			id, err := GetParmIDInt64(c)
			assert.NoError(t, err)
			assert.Equal(t, int64(123), id)
			c.JSON(http.StatusOK, gin.H{"id": id})
		})
		
		req := httptest.NewRequest("GET", "/test/123", nil)
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusOK, w.Code)
	})
}

func TestGetParmKey(t *testing.T) {
	t.Run("returns key from context", func(t *testing.T) {
		gin.SetMode(gin.TestMode)
		router := gin.New()
		
		router.GET("/test/:key", func(c *gin.Context) {
			key, err := GetParmKey(c)
			assert.NoError(t, err)
			assert.Equal(t, "mykey", key)
			c.JSON(http.StatusOK, gin.H{"key": key})
		})
		
		req := httptest.NewRequest("GET", "/test/mykey", nil)
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)
		
		assert.Equal(t, http.StatusOK, w.Code)
	})
}
