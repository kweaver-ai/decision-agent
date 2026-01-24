package agentsvc

import (
	"strings"
	"unicode"
)

type text2Vec struct {
	model     map[string][]float64
	stopWords map[string]struct{}
}

// NewText2Vec 文本转向量及相似度计算
func NewText2Vec() *text2Vec {
	return &text2Vec{
		model:     make(map[string][]float64),
		stopWords: make(map[string]struct{}),
	}
}

// simpleSegment 简单的分词函数，使用空格和标点符号作为分隔符
func (t *text2Vec) simpleSegment(text string) []string {
	var words []string
	
	wordStart := -1
	for i, r := range text {
		if unicode.IsSpace(r) || unicode.IsPunct(r) {
			if wordStart >= 0 {
				words = append(words, strings.ToLower(text[wordStart:i]))
				wordStart = -1
			}
		} else {
			if wordStart < 0 {
				wordStart = i
			}
		}
	}
	
	if wordStart >= 0 {
		words = append(words, strings.ToLower(text[wordStart:]))
	}
	
	return words
}

// SameWordsPercentage 计算 text1 与 text2 之间相同词的百分比
func (t *text2Vec) SameWordsPercentage(text1 string, text2 string) float64 {
	text1Words := t.simpleSegment(text1)
	text2Words := t.simpleSegment(text2)
	commonWords := intersect(text1Words, text2Words)

	if len(text1Words) == 0 {
		return 0.0
	}

	return float64(len(commonWords)) / float64(len(text1Words))
}

// intersect: 查找两个字符串切片的交集
func intersect(a, b []string) []string {
	m := map[string]struct{}{}
	for _, item := range a {
		m[item] = struct{}{}
	}

	resultMap := map[string]struct{}{}

	var result []string

	for _, item := range b {
		_, ok := m[item]
		if !ok {
			continue
		}

		_, ok = resultMap[item]
		if ok {
			continue
		}

		result = append(result, item)
		resultMap[item] = struct{}{}
	}

	return result
}
