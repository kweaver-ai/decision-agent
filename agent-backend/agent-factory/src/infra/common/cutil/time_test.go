package cutil

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

func TestNowStr(t *testing.T) {
	result := NowStr()
	assert.NotEmpty(t, result, "NowStr() should not be empty")

	_, err := time.Parse(DefaultTimeFormat, result)
	assert.NoError(t, err, "NowStr() should return valid time format")
}

func TestGetCurrentMSTimestamp(t *testing.T) {
	before := GetCurrentMSTimestamp()
	time.Sleep(1 * time.Millisecond)
	after := GetCurrentMSTimestamp()
	assert.Greater(t, after, before, "GetCurrentMSTimestamp() should return increasing values")
}

func TestGetCurrentTimestamp(t *testing.T) {
	before := GetCurrentTimestamp()
	time.Sleep(2 * time.Second)
	after := GetCurrentTimestamp()
	assert.Greater(t, after, before, "GetCurrentTimestamp() should return increasing values")
}

func TestFormatTime(t *testing.T) {
	now := time.Date(2026, 1, 24, 12, 30, 45, 0, time.Local)
	formatted := FormatTime(now)
	assert.NotEmpty(t, formatted, "FormatTime() should not be empty")
	assert.Equal(t, "2026-01-24 12:30:45", formatted)
}

func TestFormatTimeUnix(t *testing.T) {
	timestamp := int64(1735724645)
	formatted := FormatTimeUnix(timestamp)
	assert.NotEmpty(t, formatted, "FormatTimeUnix() should not be empty")

	_, err := time.Parse(DefaultTimeFormat, formatted)
	assert.NoError(t, err, "FormatTimeUnix() should return valid time format")
}

func TestParseTime(t *testing.T) {
	tests := []struct {
		name     string
		timeStr  string
		wantHour int
		wantMin  int
		wantSec  int
		wantErr  bool
	}{
		{
			name:     "有效时间",
			timeStr:  "12:30:45",
			wantHour: 12,
			wantMin:  30,
			wantSec:  45,
			wantErr:  false,
		},
		{
			name:     "边界值-最大小时",
			timeStr:  "23:59:59",
			wantHour: 23,
			wantMin:  59,
			wantSec:  59,
			wantErr:  false,
		},
		{
			name:     "边界值-最大分钟",
			timeStr:  "12:59:59",
			wantHour: 12,
			wantMin:  59,
			wantSec:  59,
			wantErr:  false,
		},
		{
			name:     "边界值-最大秒",
			timeStr:  "12:30:59",
			wantHour: 12,
			wantMin:  30,
			wantSec:  59,
			wantErr:  false,
		},
		{
			name:     "最小值",
			timeStr:  "00:00:00",
			wantHour: 0,
			wantMin:  0,
			wantSec:  0,
			wantErr:  false,
		},
		{
			name:     "格式错误-部分格式",
			timeStr:  "12:30",
			wantHour: 0,
			wantMin:  0,
			wantSec:  0,
			wantErr:  true,
		},
		{
			name:     "格式错误-完整格式",
			timeStr:  "12:30:45:67",
			wantHour: 0,
			wantMin:  0,
			wantSec:  0,
			wantErr:  true,
		},
		{
			name:     "分钟超出范围",
			timeStr:  "12:60:00",
			wantHour: 0,
			wantMin:  0,
			wantSec:  0,
			wantErr:  true,
		},
		{
			name:     "小时超出范围",
			timeStr:  "24:00:00",
			wantHour: 0,
			wantMin:  0,
			wantSec:  0,
			wantErr:  true,
		},
		{
			name:     "空字符串",
			timeStr:  "",
			wantHour: 0,
			wantMin:  0,
			wantSec:  0,
			wantErr:  true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			hour, min, sec, err := ParseTime(tt.timeStr)
			if tt.wantErr {
				assert.Error(t, err, "expected error")
			} else {
				assert.NoError(t, err, "expected no error")
				assert.Equal(t, tt.wantHour, hour, "hour should match expected")
				assert.Equal(t, tt.wantMin, min, "min should match expected")
				assert.Equal(t, tt.wantSec, sec, "sec should match expected")
			}
		})
	}
}
