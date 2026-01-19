package cutil

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestParseHost(t *testing.T) {
	// 测试解析IP地址
	ip := "192.168.1.1"
	assert.Equal(t, ip, ParseHost(ip))

	// 测试解析域名
	host := "example.com"
	assert.Equal(t, host, ParseHost(host))

	// 测试解析IPv6地址
	ipv6 := "2001:0db8:85a3:0000:0000:8a2e:0370:7334"
	assert.Equal(t, "["+ipv6+"]", ParseHost(ipv6))
}
