package skillenum

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestDatasource_EnumCheck_Valid(t *testing.T) {
	tests := []struct {
		name       string
		datasource Datasource
	}{
		{"inherit main", DatasourceInheritMain},
		{"self configured", DatasourceSelfConfigured},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := tt.datasource.EnumCheck()
			assert.NoError(t, err)
		})
	}
}

func TestDatasource_EnumCheck_Invalid(t *testing.T) {
	tests := []struct {
		name       string
		datasource Datasource
	}{
		{"empty datasource", ""},
		{"invalid datasource", "invalid_datasource"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := tt.datasource.EnumCheck()
			assert.Error(t, err)
			assert.Contains(t, err.Error(), "invalid skill agent datasource")
		})
	}
}

func TestDatasourceSpecificInherit_EnumCheck_Valid(t *testing.T) {
	tests := []struct {
		name    string
		inherit DatasourceSpecificInherit
	}{
		{"inherit docs", DatasourceInheritDocs},
		{"inherit graph", DatasourceInheritGraph},
		{"inherit all", DatasourceInheritAll},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := tt.inherit.EnumCheck()
			assert.NoError(t, err)
		})
	}
}

func TestDatasourceSpecificInherit_EnumCheck_Invalid(t *testing.T) {
	tests := []struct {
		name    string
		inherit DatasourceSpecificInherit
	}{
		{"empty inherit", ""},
		{"invalid inherit", "invalid_inherit"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := tt.inherit.EnumCheck()
			assert.Error(t, err)
			assert.Contains(t, err.Error(), "数据源继承类型不合法")
		})
	}
}

func TestDatasource_String(t *testing.T) {
	assert.Equal(t, "inherit_main", string(DatasourceInheritMain))
	assert.Equal(t, "self_configured", string(DatasourceSelfConfigured))
}

func TestDatasourceSpecificInherit_String(t *testing.T) {
	assert.Equal(t, "docs_only", string(DatasourceInheritDocs))
	assert.Equal(t, "graph_only", string(DatasourceInheritGraph))
	assert.Equal(t, "all", string(DatasourceInheritAll))
}
