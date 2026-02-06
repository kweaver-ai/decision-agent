package datasourcevalobj

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestNewRetrieverAdvancedConfig(t *testing.T) {
	config := NewRetrieverAdvancedConfig()
	assert.NotNil(t, config)
	assert.Nil(t, config.KG)
	assert.Nil(t, config.Doc)
}

func TestRetrieverAdvancedConfig_GetErrMsgMap(t *testing.T) {
	config := &RetrieverAdvancedConfig{}
	errMap := config.GetErrMsgMap()
	assert.NotNil(t, errMap)
	assert.Empty(t, errMap)
}

func TestRetrieverAdvancedConfig_ValObjCheck_Valid(t *testing.T) {
	validKG := 60
	simThreshold := -5.5
	graphRagTopK := 25
	longTextLength := 256
	retrievalMaxLength := 1000

	config := &RetrieverAdvancedConfig{
		KG: &KGAdvancedConfig{
			TextMatchEntityNums:   &validKG,
			VectorMatchEntityNums: &validKG,
			GraphRagTopK:          &graphRagTopK,
			LongTextLength:        &longTextLength,
			RerankerSimThreshold:  &simThreshold,
			RetrievalMaxLength:    &retrievalMaxLength,
		},
	}

	err := config.ValObjCheck()
	assert.NoError(t, err)
}

func TestRetrieverAdvancedConfig_ValObjCheck_InvalidKG(t *testing.T) {
	invalidValue := 200 // Out of range
	config := &RetrieverAdvancedConfig{
		KG: &KGAdvancedConfig{
			TextMatchEntityNums: &invalidValue,
			// Missing other required fields
		},
	}

	err := config.ValObjCheck()
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "kg is invalid")
}

func TestRetrieverAdvancedConfig_ValObjCheck_InvalidDoc(t *testing.T) {
	retrievalSlicesNum := 150
	maxSlicePerCite := 16
	rerankTopK := 15
	sliceHeadNum := 2
	sliceTailNum := 0
	documentsNum := 8
	docThreshold := -5.5
	retrievalMaxLength := 1000

	config := &RetrieverAdvancedConfig{
		Doc: &DocAdvancedConfig{
			RetrievalSlicesNum: &retrievalSlicesNum,
			MaxSlicePerCite:    &maxSlicePerCite,
			RerankTopK:         &rerankTopK,
			SliceHeadNum:       &sliceHeadNum,
			SliceTailNum:       &sliceTailNum,
			DocumentsNum:       &documentsNum,
			DocumentThreshold:  &docThreshold,
			RetrievalMaxLength: &retrievalMaxLength,
		},
	}

	err := config.ValObjCheck()
	assert.NoError(t, err)
}

func TestRetrieverAdvancedConfig_ValObjCheck_Empty(t *testing.T) {
	config := &RetrieverAdvancedConfig{}
	err := config.ValObjCheck()
	assert.NoError(t, err)
}

func TestDocAdvancedConfig_GetErrMsgMap(t *testing.T) {
	config := &DocAdvancedConfig{}
	errMap := config.GetErrMsgMap()
	assert.NotNil(t, errMap)
	assert.Len(t, errMap, 8)
	assert.Contains(t, errMap, "RetrievalSlicesNum.required")
	assert.Contains(t, errMap, "MaxSlicePerCite.required")
}

func TestKGAdvancedConfig_GetErrMsgMap(t *testing.T) {
	config := &KGAdvancedConfig{}
	errMap := config.GetErrMsgMap()
	assert.NotNil(t, errMap)
	assert.Len(t, errMap, 6)
	assert.Contains(t, errMap, "TextMatchEntityNums.required")
	assert.Contains(t, errMap, "VectorMatchEntityNums.required")
}
