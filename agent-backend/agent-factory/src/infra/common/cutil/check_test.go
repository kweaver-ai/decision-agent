package cutil

import (
	"math"
	"testing"
)

func TestCheckInRange_Int(t *testing.T) {
	tests := []struct {
		name  string
		value int
		min   int
		max   int
		want  bool
	}{
		{"值在范围内", 5, 1, 10, true},
		{"值等于最小值", 1, 1, 10, true},
		{"值等于最大值", 10, 1, 10, true},
		{"值小于最小值", 0, 1, 10, false},
		{"值大于最大值", 11, 1, 10, false},
		{"负数范围内", -5, -10, -1, true},
		{"负数小于最小值", -11, -10, -1, false},
		{"负数大于最大值", 0, -10, -1, false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := CheckInRange(tt.value, tt.min, tt.max)
			if got != tt.want {
				t.Errorf("CheckInRange(%v, %v, %v) = %v, want %v", tt.value, tt.min, tt.max, got, tt.want)
			}
		})
	}
}

func TestCheckInRange_Float(t *testing.T) {
	tests := []struct {
		name  string
		value float64
		min   float64
		max   float64
		want  bool
	}{
		{"浮点数范围内", 5.5, 1.0, 10.0, true},
		{"浮点数等于最小值", 1.0, 1.0, 10.0, true},
		{"浮点数等于最大值", 10.0, 1.0, 10.0, true},
		{"浮点数小于最小值", 0.9, 1.0, 10.0, false},
		{"浮点数大于最大值", 10.1, 1.0, 10.0, false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := CheckInRange(tt.value, tt.min, tt.max)
			if got != tt.want {
				t.Errorf("CheckInRange(%v, %v, %v) = %v, want %v", tt.value, tt.min, tt.max, got, tt.want)
			}
		})
	}
}

func TestCheckInRange_Uint(t *testing.T) {
	tests := []struct {
		name  string
		value uint
		min   uint
		max   uint
		want  bool
	}{
		{"uint 在范围内", uint(5), uint(1), uint(10), true},
		{"uint 超出范围-小于", uint(0), uint(1), uint(10), false},
		{"uint 超出范围-大于", uint(11), uint(1), uint(10), false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := CheckInRange(tt.value, tt.min, tt.max)
			if got != tt.want {
				t.Errorf("CheckInRange(%v, %v, %v) = %v, want %v", tt.value, tt.min, tt.max, got, tt.want)
			}
		})
	}
}

func TestCheckInRange_Int8(t *testing.T) {
	tests := []struct {
		name  string
		value int8
		min   int8
		max   int8
		want  bool
	}{
		{"int8 在范围内", int8(5), int8(1), int8(10), true},
		{"int8 超出范围-小于", int8(0), int8(1), int8(10), false},
		{"int8 超出范围-大于", int8(11), int8(1), int8(10), false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := CheckInRange(tt.value, tt.min, tt.max)
			if got != tt.want {
				t.Errorf("CheckInRange(%v, %v, %v) = %v, want %v", tt.value, tt.min, tt.max, got, tt.want)
			}
		})
	}
}

func TestCheckInRange_FloatSpecial(t *testing.T) {
	tests := []struct {
		name  string
		value float64
		min   float64
		max   float64
		want  bool
	}{
		{"无穷大超出范围", math.Inf(1), 0.0, 100.0, false},
		{"负无穷大超出范围", math.Inf(-1), -100.0, 0.0, false},
		{"NaN在范围内", math.NaN(), 0.0, 100.0, false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := CheckInRange(tt.value, tt.min, tt.max)
			if got != tt.want {
				t.Errorf("CheckInRange(%v, %v, %v) = %v, want %v", tt.value, tt.min, tt.max, got, tt.want)
			}
		})
	}
}

func TestCheckMin(t *testing.T) {
	tests := []struct {
		name  string
		value int
		min   int
		want  bool
	}{
		{"值等于最小值", 5, 5, true},
		{"值大于最小值", 10, 5, true},
		{"值小于最小值", 3, 5, false},
		{"负数等于最小值", -5, -5, true},
		{"负数大于最小值", -1, -5, true},
		{"负数小于最小值", -10, -5, false},
		{"零值", 0, 0, true},
		{"零值大于最小值", 0, -1, true},
		{"零值小于最小值", 0, 1, false},
		{"浮点数等于最小值", 5.0, 5.0, true},
		{"浮点数大于最小值", 10.0, 5.0, true},
		{"浮点数小于最小值", 3.0, 5.0, false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := CheckMin(tt.value, tt.min)
			if got != tt.want {
				t.Errorf("CheckMin(%v, %v) = %v, want %v", tt.value, tt.min, got, tt.want)
			}
		})
	}
}
