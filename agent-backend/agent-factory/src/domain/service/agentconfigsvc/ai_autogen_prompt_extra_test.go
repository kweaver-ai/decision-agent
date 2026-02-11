package v3agentconfigsvc

import (
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
)

// TestOpeningRemarksSystemPrompt_English tests openingRemarksSystemPrompt for English language
func TestOpeningRemarksSystemPrompt_English(t *testing.T) {
	prompt := openingRemarksSystemPrompt("en-US")
	assert.NotEmpty(t, prompt)
	assert.Contains(t, prompt, "Generate an opening statement")
	assert.Contains(t, prompt, "Name: Document Reading Assistant")
}

// TestOpeningRemarksSystemPrompt_ChineseTraditional tests openingRemarksSystemPrompt for Traditional Chinese
func TestOpeningRemarksSystemPrompt_ChineseTraditional(t *testing.T) {
	prompt := openingRemarksSystemPrompt("zh-TW")
	assert.NotEmpty(t, prompt)
	assert.Contains(t, prompt, "根據用戶輸入的內容生成開場白")
	assert.Contains(t, prompt, "名稱：文檔閱讀小助手")
}

// TestOpeningRemarksSystemPrompt_ChineseSimplified tests openingRemarksSystemPrompt for Simplified Chinese
func TestOpeningRemarksSystemPrompt_ChineseSimplified(t *testing.T) {
	prompt := openingRemarksSystemPrompt("zh-CN")
	assert.NotEmpty(t, prompt)
	assert.Contains(t, prompt, "根据用户输入的内容生成开场白")
	assert.Contains(t, prompt, "名称：文档阅读小助手")
}

// TestOpeningRemarksSystemPrompt_DefaultLanguage tests openingRemarksSystemPrompt with unknown language (defaults to zh-CN)
func TestOpeningRemarksSystemPrompt_DefaultLanguage(t *testing.T) {
	prompt := openingRemarksSystemPrompt("fr")
	assert.NotEmpty(t, prompt)
	assert.Contains(t, prompt, "根据用户输入的内容生成开场白")
	assert.Contains(t, prompt, "名称：文档阅读小助手")
}

// TestSystemPrompt_English tests systemPrompt for English language
func TestSystemPrompt_English(t *testing.T) {
	prompt := systemPrompt("en-US")
	assert.NotEmpty(t, prompt)
	assert.Contains(t, prompt, "Generate a \"Personality and Response Logic\"")
	assert.Contains(t, prompt, "Name: Document Reading Assistant")
}

// TestSystemPrompt_ChineseTraditional tests systemPrompt for Traditional Chinese
func TestSystemPrompt_ChineseTraditional(t *testing.T) {
	prompt := systemPrompt("zh-TW")
	assert.NotEmpty(t, prompt)
	assert.Contains(t, prompt, "根據用戶輸入的內容生成\"人設及回覆邏輯\"")
	assert.Contains(t, prompt, "名稱：文檔閱讀小助手")
}

// TestSystemPrompt_ChineseSimplified tests systemPrompt for Simplified Chinese
func TestSystemPrompt_ChineseSimplified(t *testing.T) {
	prompt := systemPrompt("zh-CN")
	assert.NotEmpty(t, prompt)
	assert.Contains(t, prompt, "根据用户输入的内容生成\"人设及回复逻辑\"")
	assert.Contains(t, prompt, "你是一个提示词工程师")
}

// TestSystemPrompt_DefaultLanguage tests systemPrompt with unknown language (defaults to zh-CN)
func TestSystemPrompt_DefaultLanguage(t *testing.T) {
	prompt := systemPrompt("de")
	assert.NotEmpty(t, prompt)
	assert.Contains(t, prompt, "根据用户输入的内容生成\"人设及回复逻辑\"")
	assert.Contains(t, prompt, "你是一个提示词工程师")
}

// TestUserPromptForOpenRemarks_English tests userPromptForOpenRemarks for English
func TestUserPromptForOpenRemarks_English(t *testing.T) {
	name := "Test Agent"
	profile := "A test assistant"
	skills := []string{"reading", "writing"}
	sources := []string{"document A", "database B"}

	prompt := userPromptForOpenRemarks("en-US", name, profile, skills, sources)
	assert.NotEmpty(t, prompt)
	assert.Contains(t, prompt, name)
	assert.Contains(t, prompt, profile)
	// The strings are joined without spaces
	assert.Contains(t, prompt, "reading,writing")
	assert.Contains(t, prompt, "document A,database B")
	assert.Contains(t, prompt, "Please generate an opening statement")
}

// TestUserPromptForOpenRemarks_ChineseTraditional tests userPromptForOpenRemarks for Traditional Chinese
func TestUserPromptForOpenRemarks_ChineseTraditional(t *testing.T) {
	name := "測試助手"
	profile := "一個測試助手"
	skills := []string{"閱讀", "寫作"}
	sources := []string{"文檔 A", "數據庫 B"}

	prompt := userPromptForOpenRemarks("zh-TW", name, profile, skills, sources)
	assert.NotEmpty(t, prompt)
	assert.Contains(t, prompt, name)
	assert.Contains(t, prompt, profile)
	assert.Contains(t, prompt, "請根據上面提供的信息生成一個開場白")
}

// TestUserPromptForOpenRemarks_ChineseSimplified tests userPromptForOpenRemarks for Simplified Chinese
func TestUserPromptForOpenRemarks_ChineseSimplified(t *testing.T) {
	name := "测试助手"
	profile := "一个测试助手"
	skills := []string{"阅读", "写作"}
	sources := []string{"文档 A", "数据库 B"}

	prompt := userPromptForOpenRemarks("zh-CN", name, profile, skills, sources)
	assert.NotEmpty(t, prompt)
	assert.Contains(t, prompt, name)
	assert.Contains(t, prompt, profile)
	assert.Contains(t, prompt, "请根据上面提供的信息生成一个开场白")
}

// TestUserPromptForOpenRemarks_EmptySkills tests userPromptForOpenRemarks with empty skills
func TestUserPromptForOpenRemarks_EmptySkills(t *testing.T) {
	name := "Test Agent"
	profile := "A test assistant"
	skills := []string{}
	sources := []string{"document A"}

	prompt := userPromptForOpenRemarks("en-US", name, profile, skills, sources)
	assert.NotEmpty(t, prompt)
	assert.Contains(t, prompt, name)
	assert.Contains(t, prompt, "Skills List: ")
}

// TestUserPromptForOpenRemarks_EmptySources tests userPromptForOpenRemarks with empty sources
func TestUserPromptForOpenRemarks_EmptySources(t *testing.T) {
	name := "Test Agent"
	profile := "A test assistant"
	skills := []string{"reading"}
	sources := []string{}

	prompt := userPromptForOpenRemarks("en-US", name, profile, skills, sources)
	assert.NotEmpty(t, prompt)
	assert.Contains(t, prompt, name)
	assert.Contains(t, prompt, "Knowledge Sources: ")
}

// TestUserPromptForPresetQuestion_English tests userPromptForPresetQuestion for English
func TestUserPromptForPresetQuestion_English(t *testing.T) {
	name := "Test Agent"
	profile := "A test assistant"
	skills := []string{"reading", "writing"}
	sources := []string{"document A", "database B"}

	prompt := userPromptForPresetQuestion("en-US", name, profile, skills, sources)
	assert.NotEmpty(t, prompt)
	assert.Contains(t, prompt, name)
	assert.Contains(t, prompt, profile)
	assert.Contains(t, prompt, "Please generate 3 preset questions")
}

// TestUserPromptForPresetQuestion_ChineseSimplified tests userPromptForPresetQuestion for Simplified Chinese
func TestUserPromptForPresetQuestion_ChineseSimplified(t *testing.T) {
	name := "测试助手"
	profile := "一个测试助手"
	skills := []string{"阅读", "写作"}
	sources := []string{"文档 A", "数据库 B"}

	prompt := userPromptForPresetQuestion("zh-CN", name, profile, skills, sources)
	assert.NotEmpty(t, prompt)
	assert.Contains(t, prompt, name)
	assert.Contains(t, prompt, "请根据上面提供的信息生成3个预设问题")
}

// TestUserPromptForPresetQuestion_ChineseTraditional tests userPromptForPresetQuestion for Traditional Chinese
func TestUserPromptForPresetQuestion_ChineseTraditional(t *testing.T) {
	name := "測試助手"
	profile := "一個測試助手"
	skills := []string{"閱讀", "寫作"}
	sources := []string{"文檔 A", "數據庫 B"}

	prompt := userPromptForPresetQuestion("zh-TW", name, profile, skills, sources)
	assert.NotEmpty(t, prompt)
	assert.Contains(t, prompt, name)
	assert.Contains(t, prompt, "請根據上面提供的信息生成3個預設問題")
}

// TestUserPromptForSystem_English tests userPromptForSystem for English
func TestUserPromptForSystem_English(t *testing.T) {
	name := "Test Agent"
	profile := "A test assistant"
	skills := []string{"reading", "writing"}
	sources := []string{"document A", "database B"}

	prompt := userPromptForSystem("en-US", name, profile, skills, sources)
	assert.NotEmpty(t, prompt)
	assert.Contains(t, prompt, name)
	assert.Contains(t, prompt, profile)
	assert.Contains(t, prompt, "Please generate a personality and instruction")
}

// TestUserPromptForSystem_ChineseSimplified tests userPromptForSystem for Simplified Chinese
func TestUserPromptForSystem_ChineseSimplified(t *testing.T) {
	name := "测试助手"
	profile := "一个测试助手"
	skills := []string{"阅读", "写作"}
	sources := []string{"文档 A", "数据库 B"}

	prompt := userPromptForSystem("zh-CN", name, profile, skills, sources)
	assert.NotEmpty(t, prompt)
	assert.Contains(t, prompt, name)
	assert.Contains(t, prompt, "请根据上面提供的信息生成一个人设和指令")
}

// TestUserPromptForSystem_ChineseTraditional tests userPromptForSystem for Traditional Chinese
func TestUserPromptForSystem_ChineseTraditional(t *testing.T) {
	name := "測試助手"
	profile := "一個測試助手"
	skills := []string{"閱讀", "寫作"}
	sources := []string{"文檔 A", "數據庫 B"}

	prompt := userPromptForSystem("zh-TW", name, profile, skills, sources)
	assert.NotEmpty(t, prompt)
	assert.Contains(t, prompt, name)
	assert.Contains(t, prompt, "請根據上面提供的信息生成一個人設和指令")
}

// TestUserPromptFunctions_SpecialCharacters tests user prompt functions with special characters
func TestUserPromptFunctions_SpecialCharacters(t *testing.T) {
	name := "Test <Agent> & Co."
	profile := "A test assistant with \"quotes\" and 'apostrophes'"
	skills := []string{"skill & 1", "skill < 2"}
	sources := []string{"source \"A\"", "source 'B'"}

	t.Run("userPromptForOpenRemarks", func(t *testing.T) {
		prompt := userPromptForOpenRemarks("en-US", name, profile, skills, sources)
		assert.Contains(t, prompt, name)
		assert.Contains(t, prompt, profile)
	})

	t.Run("userPromptForPresetQuestion", func(t *testing.T) {
		prompt := userPromptForPresetQuestion("en-US", name, profile, skills, sources)
		assert.Contains(t, prompt, name)
		assert.Contains(t, prompt, profile)
	})

	t.Run("userPromptForSystem", func(t *testing.T) {
		prompt := userPromptForSystem("en-US", name, profile, skills, sources)
		assert.Contains(t, prompt, name)
		assert.Contains(t, prompt, profile)
	})
}

// TestUserPromptFunctions_LongStrings tests user prompt functions with long strings
func TestUserPromptFunctions_LongStrings(t *testing.T) {
	longString := strings.Repeat("a", 1000)
	name := longString
	profile := longString
	skills := []string{longString}
	sources := []string{longString}

	t.Run("userPromptForOpenRemarks handles long strings", func(t *testing.T) {
		prompt := userPromptForOpenRemarks("en-US", name, profile, skills, sources)
		assert.Contains(t, prompt, longString)
	})

	t.Run("userPromptForPresetQuestion handles long strings", func(t *testing.T) {
		prompt := userPromptForPresetQuestion("en-US", name, profile, skills, sources)
		assert.Contains(t, prompt, longString)
	})

	t.Run("userPromptForSystem handles long strings", func(t *testing.T) {
		prompt := userPromptForSystem("en-US", name, profile, skills, sources)
		assert.Contains(t, prompt, longString)
	})
}

// TestUserPromptFunctions_MultipleSkillsAndSources tests with multiple skills and sources
func TestUserPromptFunctions_MultipleSkillsAndSources(t *testing.T) {
	name := "Multi-Agent"
	profile := "An agent with many skills"
	skills := []string{"skill1", "skill2", "skill3", "skill4", "skill5"}
	sources := []string{"source1", "source2", "source3", "source4"}

	t.Run("userPromptForOpenRemarks with multiple skills", func(t *testing.T) {
		prompt := userPromptForOpenRemarks("en-US", name, profile, skills, sources)
		assert.Contains(t, prompt, "skill1,skill2,skill3,skill4,skill5")
		assert.Contains(t, prompt, "source1,source2,source3,source4")
	})

	t.Run("userPromptForPresetQuestion with multiple skills", func(t *testing.T) {
		prompt := userPromptForPresetQuestion("en-US", name, profile, skills, sources)
		assert.Contains(t, prompt, "skill1,skill2,skill3,skill4,skill5")
		assert.Contains(t, prompt, "source1,source2,source3,source4")
	})

	t.Run("userPromptForSystem with multiple skills", func(t *testing.T) {
		prompt := userPromptForSystem("en-US", name, profile, skills, sources)
		assert.Contains(t, prompt, "skill1,skill2,skill3,skill4,skill5")
		assert.Contains(t, prompt, "source1,source2,source3,source4")
	})
}

// TestUserPromptFunctions_UnicodeCharacters tests with Unicode characters
func TestUserPromptFunctions_UnicodeCharacters(t *testing.T) {
	name := "代理助手 🤖"
	profile := "这是一个测试助手 📝"
	skills := []string{"阅读 📚", "写作 ✍️"}
	sources := []string{"文档 📄", "数据库 💾"}

	t.Run("userPromptForOpenRemarks with Unicode", func(t *testing.T) {
		prompt := userPromptForOpenRemarks("zh-CN", name, profile, skills, sources)
		assert.Contains(t, prompt, name)
		assert.Contains(t, prompt, profile)
		assert.Contains(t, prompt, "阅读 📚,写作 ✍️")
		assert.Contains(t, prompt, "文档 📄,数据库 💾")
	})

	t.Run("userPromptForPresetQuestion with Unicode", func(t *testing.T) {
		prompt := userPromptForPresetQuestion("zh-CN", name, profile, skills, sources)
		assert.Contains(t, prompt, name)
		assert.Contains(t, prompt, profile)
	})

	t.Run("userPromptForSystem with Unicode", func(t *testing.T) {
		prompt := userPromptForSystem("zh-CN", name, profile, skills, sources)
		assert.Contains(t, prompt, name)
		assert.Contains(t, prompt, profile)
	})
}

// TestSystemPrompt_ContainsFormatting tests that system prompt contains expected formatting
func TestSystemPrompt_ContainsFormatting(t *testing.T) {
	t.Run("English prompt contains markdown", func(t *testing.T) {
		prompt := systemPrompt("en-US")
		assert.Contains(t, prompt, "###")
	})

	t.Run("Chinese prompt contains formatting", func(t *testing.T) {
		prompt := systemPrompt("zh-CN")
		assert.Contains(t, prompt, "##")
	})
}

// TestOpeningRemarksSystemPrompt_ContainsFormatting tests that opening remarks prompt contains expected formatting
func TestOpeningRemarksSystemPrompt_ContainsFormatting(t *testing.T) {
	t.Run("English prompt contains requirements", func(t *testing.T) {
		prompt := openingRemarksSystemPrompt("en-US")
		assert.Contains(t, prompt, "Requirements:")
		assert.Contains(t, prompt, "1.")
		assert.Contains(t, prompt, "2.")
		assert.Contains(t, prompt, "3.")
	})

	t.Run("Chinese prompt contains requirements", func(t *testing.T) {
		prompt := openingRemarksSystemPrompt("zh-CN")
		assert.Contains(t, prompt, "要求：")
		assert.Contains(t, prompt, "1.")
		assert.Contains(t, prompt, "2.")
		assert.Contains(t, prompt, "3.")
	})
}
