package agentsvc

import (
	"fmt"
	"strings"

	agentreq "github.com/kweaver-ai/decision-agent/agent-factory/src/driveradapter/api/rdto/agent/req"
)

// buildUserQuery 将文件信息注入到用户问题中
// 生成的格式：
// 当前会话的临时文件路径：/workspace/{conversation_id}/uploads/temparea/
//
// 可用文件：
// - data.csv (/workspace/conv-123/uploads/temparea/data.csv)
// - config.json (/workspace/conv-123/uploads/temparea/config.json)
//
// 用户问题：{originalQuery}
func buildUserQuery(originalQuery string, conversationID string, selectedFiles []agentreq.SelectedFile) string {
	if len(selectedFiles) == 0 {
		return originalQuery
	}

	var fileList strings.Builder
	for _, file := range selectedFiles {
		filePath := fmt.Sprintf("/workspace/%s/uploads/temparea/%s", conversationID, file.FileName)
		fileList.WriteString(fmt.Sprintf("- %s (%s)\n", file.FileName, filePath))
	}

	rootPath := fmt.Sprintf("/workspace/%s/uploads/temparea/", conversationID)
	injectedQuery := fmt.Sprintf(`当前会话的临时文件路径：%s

可用文件：
%s用户问题：%s`,
		rootPath,
		fileList.String(),
		originalQuery,
	)

	return injectedQuery
}
