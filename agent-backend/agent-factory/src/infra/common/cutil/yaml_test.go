package cutil

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestYamlParseFromStr(t *testing.T) {
	//	YamlParseFromStr ut
	str := `
a: Easy!
b:
  c: 2
  d: [3, 4]	
`
	obj := struct {
		A string `yaml:"a"`
		B struct {
			C int   `yaml:"c"`
			D []int `yaml:"d"`
		}
	}{}

	err := YamlParseFromStr(str, &obj)
	if err != nil {
		t.Error(err)
	}

	assert.Equal(t, "Easy!", obj.A)
	assert.Equal(t, 2, obj.B.C)
	assert.Equal(t, []int{3, 4}, obj.B.D)
}
