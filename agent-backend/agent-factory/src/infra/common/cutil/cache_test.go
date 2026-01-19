package cutil

import (
	"context"
	"encoding/json"
	"testing"
	"time"

	"github.com/go-redis/redismock/v8"
	"github.com/stretchr/testify/assert"
)

type TestStruct struct {
	Name  string
	Value int
}

func TestSetCache(t *testing.T) {
	db, mock := redismock.NewClientMock()
	ctx := context.Background()

	testCases := []struct {
		name    string
		key     string
		value   TestStruct
		expire  time.Duration
		wantErr bool
		setup   func()
	}{
		{
			name:   "正常设置缓存",
			key:    "test_key",
			value:  TestStruct{Name: "test", Value: 123},
			expire: time.Hour,
			setup: func() {
				data, _ := json.Marshal(TestStruct{Name: "test", Value: 123})
				mock.ExpectSet("test_key", data, time.Hour).SetVal("OK")
			},
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			tc.setup()

			err := SetCache(ctx, db, tc.key, tc.value, tc.expire)
			if tc.wantErr {
				assert.Error(t, err)
			} else {
				assert.NoError(t, err)
			}
		})
	}
}

func TestGetCache(t *testing.T) {
	db, mock := redismock.NewClientMock()
	ctx := context.Background()

	testCases := []struct {
		name     string
		key      string
		mockData TestStruct
		wantErr  bool
		setup    func()
	}{
		{
			name: "正常获取缓存",
			key:  "test_key",
			mockData: TestStruct{
				Name:  "test",
				Value: 123,
			},
			setup: func() {
				data, _ := json.Marshal(TestStruct{Name: "test", Value: 123})
				mock.ExpectGet("test_key").SetVal(string(data))
			},
		},
		{
			name:    "键不存在",
			key:     "not_exist_key",
			wantErr: false,
			setup: func() {
				mock.ExpectGet("not_exist_key").RedisNil()
			},
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			tc.setup()

			result, err := GetCache[TestStruct](ctx, db, tc.key)
			if tc.wantErr {
				assert.Error(t, err)
			} else {
				assert.NoError(t, err)

				if tc.key == "not_exist_key" {
					assert.Nil(t, result)
				} else {
					assert.Equal(t, &tc.mockData, result)
				}
			}
		})
	}
}

func TestDelCache(t *testing.T) {
	db, mock := redismock.NewClientMock()
	ctx := context.Background()

	testCases := []struct {
		name    string
		key     string
		wantErr bool
		setup   func()
	}{
		{
			name: "正常删除缓存",
			key:  "test_key",
			setup: func() {
				mock.ExpectDel("test_key").SetVal(1)
			},
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			tc.setup()

			err := DelCache(ctx, db, tc.key)
			if tc.wantErr {
				assert.Error(t, err)
			} else {
				assert.NoError(t, err)
			}
		})
	}
}
