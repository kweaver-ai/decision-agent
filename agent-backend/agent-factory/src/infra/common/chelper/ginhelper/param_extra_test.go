package ginhelper

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
)

func TestGetParmIDInt64_ErrorCases(t *testing.T) {
	t.Run("returns error when id is not an integer", func(t *testing.T) {
		gin.SetMode(gin.TestMode)
		router := gin.New()

		router.GET("/test/:id", func(c *gin.Context) {
			id, err := GetParmIDInt64(c)
			assert.Error(t, err)
			assert.Equal(t, int64(0), id)
		})

		req := httptest.NewRequest("GET", "/test/abc", nil)
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)
	})

	t.Run("returns error when id is missing", func(t *testing.T) {
		gin.SetMode(gin.TestMode)
		router := gin.New()

		router.GET("/test", func(c *gin.Context) {
			id, err := GetParmIDInt64(c)
			assert.Error(t, err)
			assert.Equal(t, int64(0), id)
		})

		req := httptest.NewRequest("GET", "/test", nil)
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)
	})

	t.Run("handles negative integer id", func(t *testing.T) {
		gin.SetMode(gin.TestMode)
		router := gin.New()

		router.GET("/test/:id", func(c *gin.Context) {
			id, err := GetParmIDInt64(c)
			assert.NoError(t, err)
			assert.Equal(t, int64(-123), id)
			c.JSON(http.StatusOK, gin.H{"id": id})
		})

		req := httptest.NewRequest("GET", "/test/-123", nil)
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)
	})

	t.Run("handles large integer id", func(t *testing.T) {
		gin.SetMode(gin.TestMode)
		router := gin.New()

		router.GET("/test/:id", func(c *gin.Context) {
			id, err := GetParmIDInt64(c)
			assert.NoError(t, err)
			assert.Equal(t, int64(9223372036854775807), id)
			c.JSON(http.StatusOK, gin.H{"id": id})
		})

		req := httptest.NewRequest("GET", "/test/9223372036854775807", nil)
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)
	})
}

func TestGetParmKey_ErrorCases(t *testing.T) {
	t.Run("returns error when key is missing", func(t *testing.T) {
		gin.SetMode(gin.TestMode)
		router := gin.New()

		router.GET("/test", func(c *gin.Context) {
			key, err := GetParmKey(c)
			assert.Error(t, err)
			assert.Empty(t, key)
		})

		req := httptest.NewRequest("GET", "/test", nil)
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)
	})
}

func TestGetParmInt64_ExtraCases(t *testing.T) {
	t.Run("returns int64 value from context", func(t *testing.T) {
		gin.SetMode(gin.TestMode)
		router := gin.New()

		router.GET("/test/:id", func(c *gin.Context) {
			id, err := GetParmInt64(c, "id")
			assert.NoError(t, err)
			assert.Equal(t, int64(123), id)
			c.JSON(http.StatusOK, gin.H{"id": id})
		})

		req := httptest.NewRequest("GET", "/test/123", nil)
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)
	})

	t.Run("returns error when parameter is empty", func(t *testing.T) {
		gin.SetMode(gin.TestMode)
		router := gin.New()

		router.GET("/test", func(c *gin.Context) {
			id, err := GetParmInt64(c, "id")
			assert.Error(t, err)
			assert.Equal(t, int64(0), id)
		})

		req := httptest.NewRequest("GET", "/test", nil)
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)
	})

	t.Run("returns error when parameter is not an integer", func(t *testing.T) {
		gin.SetMode(gin.TestMode)
		router := gin.New()

		router.GET("/test/:id", func(c *gin.Context) {
			id, err := GetParmInt64(c, "id")
			assert.Error(t, err)
			assert.Equal(t, int64(0), id)
		})

		req := httptest.NewRequest("GET", "/test/abc", nil)
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)
	})

	t.Run("handles negative integer", func(t *testing.T) {
		gin.SetMode(gin.TestMode)
		router := gin.New()

		router.GET("/test/:id", func(c *gin.Context) {
			id, err := GetParmInt64(c, "id")
			assert.NoError(t, err)
			assert.Equal(t, int64(-456), id)
			c.JSON(http.StatusOK, gin.H{"id": id})
		})

		req := httptest.NewRequest("GET", "/test/-456", nil)
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)
	})

	t.Run("handles zero value", func(t *testing.T) {
		gin.SetMode(gin.TestMode)
		router := gin.New()

		router.GET("/test/:id", func(c *gin.Context) {
			id, err := GetParmInt64(c, "id")
			assert.NoError(t, err)
			assert.Equal(t, int64(0), id)
			c.JSON(http.StatusOK, gin.H{"id": id})
		})

		req := httptest.NewRequest("GET", "/test/0", nil)
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)
	})
}

func TestGetParmID_EdgeCases(t *testing.T) {
	t.Run("handles empty string id", func(t *testing.T) {
		gin.SetMode(gin.TestMode)
		router := gin.New()

		router.GET("/test/:id", func(c *gin.Context) {
			id, err := GetParmID(c)
			// Empty string should return error
			assert.Error(t, err)
			assert.Empty(t, id)
		})

		req := httptest.NewRequest("GET", "/test/", nil)
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)
	})

	t.Run("handles special characters in id", func(t *testing.T) {
		gin.SetMode(gin.TestMode)
		router := gin.New()

		router.GET("/test/:id", func(c *gin.Context) {
			id, err := GetParmID(c)
			assert.NoError(t, err)
			assert.Equal(t, "test-key_123", id)
			c.JSON(http.StatusOK, gin.H{"id": id})
		})

		req := httptest.NewRequest("GET", "/test/test-key_123", nil)
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)
	})

	t.Run("handles unicode in id", func(t *testing.T) {
		gin.SetMode(gin.TestMode)
		router := gin.New()

		router.GET("/test/:id", func(c *gin.Context) {
			id, err := GetParmID(c)
			assert.NoError(t, err)
			assert.Equal(t, "测试id", id)
			c.JSON(http.StatusOK, gin.H{"id": id})
		})

		req := httptest.NewRequest("GET", "/test/测试id", nil)
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)
	})
}

func TestGetParmInt64_DifferentKeys(t *testing.T) {
	t.Run("works with different parameter names", func(t *testing.T) {
		gin.SetMode(gin.TestMode)
		router := gin.New()

		router.GET("/test/:userId", func(c *gin.Context) {
			userId, err := GetParmInt64(c, "userId")
			assert.NoError(t, err)
			assert.Equal(t, int64(999), userId)
			c.JSON(http.StatusOK, gin.H{"userId": userId})
		})

		req := httptest.NewRequest("GET", "/test/999", nil)
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)
	})

	t.Run("returns error when key does not exist", func(t *testing.T) {
		gin.SetMode(gin.TestMode)
		router := gin.New()

		router.GET("/test/:id", func(c *gin.Context) {
			value, err := GetParmInt64(c, "nonexistent")
			assert.Error(t, err)
			assert.Equal(t, int64(0), value)
		})

		req := httptest.NewRequest("GET", "/test/123", nil)
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)
	})
}
