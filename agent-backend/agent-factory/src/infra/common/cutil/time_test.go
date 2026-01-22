package cutil

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
)

func TestNowStr(t *testing.T) {
	// capture the current time
	now := time.Now().Format(DefaultTimeFormat)

	// call the NowStr function
	result := NowStr()

	// check if the result matches the captured time format
	assert.Equal(t, now, result)
}

func TestFormatTime(t *testing.T) {
	// define a specific time
	testTime := time.Date(2023, time.October, 2, 15, 0, 0, 0, time.UTC)

	// format the time using DefaultTimeFormat
	expected := testTime.Format(DefaultTimeFormat)

	// call the FormatTime function
	result := FormatTime(testTime)

	// assert that the formatted time matches the expected format
	assert.Equal(t, expected, result)
}

func TestFormatTimeUnix(t *testing.T) {
	// define a specific unix time
	unixTime := int64(1672531200) // corresponds to 2023-01-01 00:00:00 UTC

	// format the time using DefaultTimeFormat
	expected := time.Unix(unixTime, 0).Format(DefaultTimeFormat)

	// call the FormatTimeUnix function
	result := FormatTimeUnix(unixTime)

	// assert that the formatted time matches the expected format
	assert.Equal(t, expected, result)
}
