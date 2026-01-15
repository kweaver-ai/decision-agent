package cutil

import (
	"fmt"
	"regexp"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestGenerateRandomString(t *testing.T) {
	t.Run("基本长度测试", func(t *testing.T) {
		testCases := []int{1, 5, 10, 50, 100}
		for _, length := range testCases {
			str := GenerateRandomString(length)
			if len(str) != length {
				t.Errorf("长度 %d: 期望字符串长度 %d, 实际得到 %d", length, length, len(str))
			}
		}
	})

	t.Run("字符集合法性测试", func(t *testing.T) {
		// 测试生成的字符串只包含预期的字符集
		validChars := regexp.MustCompile(`^[a-zA-Z0-9]+$`)
		str := GenerateRandomString(50)

		if !validChars.MatchString(str) {
			t.Errorf("生成的字符串包含非法字符: %s", str)
		}
	})

	t.Run("随机性测试", func(t *testing.T) {
		// 生成多个字符串，验证它们不完全相同
		const testCount = 10

		const stringLength = 20

		strings := make([]string, testCount)

		for i := 0; i < testCount; i++ {
			strings[i] = GenerateRandomString(stringLength)
		}

		// 检查是否有重复的字符串（概率极低但可能发生）
		duplicateCount := 0

		for i := 0; i < testCount; i++ {
			for j := i + 1; j < testCount; j++ {
				if strings[i] == strings[j] {
					duplicateCount++
				}
			}
		}

		// 允许少量重复，但不应该全部相同
		if duplicateCount > testCount/2 {
			t.Errorf("生成的字符串重复率过高: %d/%d", duplicateCount, testCount)
		}
	})

	t.Run("边界值测试", func(t *testing.T) {
		// 测试最小值
		str1 := GenerateRandomString(1)
		if len(str1) != 1 {
			t.Errorf("最小长度测试失败: 期望长度 1, 实际得到 %d", len(str1))
		}

		// 测试最大值
		str100 := GenerateRandomString(100)
		if len(str100) != 100 {
			t.Errorf("最大长度测试失败: 期望长度 100, 实际得到 %d", len(str100))
		}
	})

	t.Run("异常情况测试", func(t *testing.T) {
		// 测试非法长度值应该触发panic
		testCases := []int{0, -1, -10, 101, 200}

		for _, length := range testCases {
			t.Run(fmt.Sprintf("length_%d", length), func(t *testing.T) {
				defer func() {
					if r := recover(); r == nil {
						t.Errorf("长度 %d 应该触发panic，但没有", length)
					}
				}()
				GenerateRandomString(length)
			})
		}
	})

	t.Run("字符分布测试", func(t *testing.T) {
		// 生成一个较长的字符串，验证字符分布的合理性
		str := GenerateRandomString(100)

		hasLower := false
		hasUpper := false
		hasDigit := false

		for _, char := range str {
			if char >= 'a' && char <= 'z' {
				hasLower = true
			} else if char >= 'A' && char <= 'Z' {
				hasUpper = true
			} else if char >= '0' && char <= '9' {
				hasDigit = true
			}
		}

		// 对于100个字符的字符串，应该有合理的概率包含各种类型的字符
		// 注意：这是概率性测试，极小概率可能失败
		if !hasLower && !hasUpper && !hasDigit {
			t.Error("生成的字符串字符分布异常")
		}
	})
}

func TestStringSplitAndJoin(t *testing.T) {
	t.Parallel()

	assert.Equal(t, "a\nb\nc", StringSplitAndJoin("a:b:c"))
}
