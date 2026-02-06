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

func TestRetrieverAdvancedConfig_ValObjCheck_ValidDoc(t *testing.T) {
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

func TestKGAdvancedConfig_ValObjCheck_InvalidTextMatchEntityNums(t *testing.T) {
	invalidValue := 150 // Out of range (40-100)
	config := &KGAdvancedConfig{
		TextMatchEntityNums: &invalidValue,
	}
	err := config.ValObjCheck()
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "text_match_entity_nums must between 40 and 100")
}

func TestKGAdvancedConfig_ValObjCheck_InvalidRerankerSimThreshold(t *testing.T) {
	textMatchEntityNums := 60
	invalidValue := 15.0 // Out of range (-10 to 10)
	config := &KGAdvancedConfig{
		TextMatchEntityNums:  &textMatchEntityNums,
		RerankerSimThreshold: &invalidValue,
	}
	err := config.ValObjCheck()
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "reranker_sim_threshold must between -10 and 10")
}

func TestKGAdvancedConfig_ValObjCheck_InvalidGraphRagTopK(t *testing.T) {
	textMatchEntityNums := 60
	rerankerSimThreshold := -5.5
	invalidValue := 150 // Out of range (10-100)
	config := &KGAdvancedConfig{
		TextMatchEntityNums:  &textMatchEntityNums,
		RerankerSimThreshold: &rerankerSimThreshold,
		GraphRagTopK:         &invalidValue,
	}
	err := config.ValObjCheck()
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "graph_rag_topk must between 10 and 100")
}

func TestKGAdvancedConfig_ValObjCheck_InvalidLongTextLength(t *testing.T) {
	textMatchEntityNums := 60
	rerankerSimThreshold := -5.5
	graphRagTopK := 25
	invalidValue := 30 // Less than 50
	config := &KGAdvancedConfig{
		TextMatchEntityNums:  &textMatchEntityNums,
		RerankerSimThreshold: &rerankerSimThreshold,
		GraphRagTopK:         &graphRagTopK,
		LongTextLength:       &invalidValue,
	}
	err := config.ValObjCheck()
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "long_text_length must be greater than 50")
}

func TestKGAdvancedConfig_ValObjCheck_InvalidVectorMatchEntityNums(t *testing.T) {
	textMatchEntityNums := 60
	rerankerSimThreshold := -5.5
	graphRagTopK := 25
	longTextLength := 256
	invalidValue := 150 // Out of range (40-100)
	config := &KGAdvancedConfig{
		TextMatchEntityNums:  &textMatchEntityNums,
		RerankerSimThreshold: &rerankerSimThreshold,
		GraphRagTopK:         &graphRagTopK,
		LongTextLength:       &longTextLength,
		VectorMatchEntityNums: &invalidValue,
	}
	err := config.ValObjCheck()
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "vector_match_entity_nums must between 40 and 100")
}

func TestRetrieverAdvancedConfig_ValObjCheck_InvalidDoc(t *testing.T) {
	retrievalSlicesNum := 250 // Out of range
	config := &RetrieverAdvancedConfig{
		Doc: &DocAdvancedConfig{
			RetrievalSlicesNum: &retrievalSlicesNum,
		},
	}
	err := config.ValObjCheck()
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "doc is invalid")
}

func TestRetrieverAdvancedConfig_ValObjCheck_AllInvalid(t *testing.T) {
	invalidKG := 200
	invalidDoc := 250
	config := &RetrieverAdvancedConfig{
		KG: &KGAdvancedConfig{
			TextMatchEntityNums: &invalidKG,
		},
		Doc: &DocAdvancedConfig{
			RetrievalSlicesNum: &invalidDoc,
		},
	}
	err := config.ValObjCheck()
	assert.Error(t, err)
	// The first error encountered is returned
	assert.Contains(t, err.Error(), "is invalid")
}

func TestDocAdvancedConfig_ValObjCheck_InvalidRetrievalSlicesNum(t *testing.T) {
	invalidValue := 250 // Out of range (50-200)
	config := &DocAdvancedConfig{
		RetrievalSlicesNum: &invalidValue,
	}
	err := config.ValObjCheck()
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "retrieval_slices_num must between 50 and 200")
}

func TestDocAdvancedConfig_ValObjCheck_InvalidRerankTopK(t *testing.T) {
	retrievalSlicesNum := 150
	invalidValue := 50 // Out of range (10-30)
	config := &DocAdvancedConfig{
		RetrievalSlicesNum: &retrievalSlicesNum,
		RerankTopK:         &invalidValue,
	}
	err := config.ValObjCheck()
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "rerank_topk must between 10 and 30")
}

func TestDocAdvancedConfig_ValObjCheck_InvalidSliceHeadNum(t *testing.T) {
	retrievalSlicesNum := 150
	rerankTopK := 15
	invalidValue := 5 // Out of range (0-3)
	config := &DocAdvancedConfig{
		RetrievalSlicesNum: &retrievalSlicesNum,
		RerankTopK:         &rerankTopK,
		SliceHeadNum:       &invalidValue,
	}
	err := config.ValObjCheck()
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "slice_head_num must between 0 and 3")
}

func TestDocAdvancedConfig_ValObjCheck_InvalidSliceTailNum(t *testing.T) {
	retrievalSlicesNum := 150
	rerankTopK := 15
	sliceHeadNum := 2
	invalidValue := 5 // Out of range (0-3)
	config := &DocAdvancedConfig{
		RetrievalSlicesNum: &retrievalSlicesNum,
		RerankTopK:         &rerankTopK,
		SliceHeadNum:       &sliceHeadNum,
		SliceTailNum:       &invalidValue,
	}
	err := config.ValObjCheck()
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "slice_tail_num must between 0 and 3")
}

func TestDocAdvancedConfig_ValObjCheck_InvalidDocumentsNum(t *testing.T) {
	retrievalSlicesNum := 150
	rerankTopK := 15
	sliceHeadNum := 2
	sliceTailNum := 0
	invalidValue := 15 // Out of range (4-10)
	config := &DocAdvancedConfig{
		RetrievalSlicesNum: &retrievalSlicesNum,
		RerankTopK:         &rerankTopK,
		SliceHeadNum:       &sliceHeadNum,
		SliceTailNum:       &sliceTailNum,
		DocumentsNum:       &invalidValue,
	}
	err := config.ValObjCheck()
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "documents_num must between 4 and 10")
}

func TestDocAdvancedConfig_ValObjCheck_InvalidMaxSlicePerCite(t *testing.T) {
	retrievalSlicesNum := 150
	rerankTopK := 15
	sliceHeadNum := 2
	sliceTailNum := 0
	documentsNum := 8
	invalidValue := 25 // Out of range (5-20)
	config := &DocAdvancedConfig{
		RetrievalSlicesNum: &retrievalSlicesNum,
		RerankTopK:         &rerankTopK,
		SliceHeadNum:       &sliceHeadNum,
		SliceTailNum:       &sliceTailNum,
		DocumentsNum:       &documentsNum,
		MaxSlicePerCite:    &invalidValue,
	}
	err := config.ValObjCheck()
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "max_slice_per_cite must between 5 and 20")
}

func TestDocAdvancedConfig_ValObjCheck_InvalidDocumentThreshold(t *testing.T) {
	retrievalSlicesNum := 150
	rerankTopK := 15
	sliceHeadNum := 2
	sliceTailNum := 0
	documentsNum := 8
	maxSlicePerCite := 16
	invalidValue := 15.0 // Out of range (-10 to 10)
	config := &DocAdvancedConfig{
		RetrievalSlicesNum: &retrievalSlicesNum,
		RerankTopK:         &rerankTopK,
		SliceHeadNum:       &sliceHeadNum,
		SliceTailNum:       &sliceTailNum,
		DocumentsNum:       &documentsNum,
		MaxSlicePerCite:    &maxSlicePerCite,
		DocumentThreshold:  &invalidValue,
	}
	err := config.ValObjCheck()
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "document_threshold must between -10 and 10")
}
