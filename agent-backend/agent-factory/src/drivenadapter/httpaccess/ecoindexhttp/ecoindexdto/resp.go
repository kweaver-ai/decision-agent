package ecoindexdto

type BotIndexStatusInfo struct {
	BotVersion    string           `json:"bot_version"`
	CompleteCount int              `json:"complete_count"`
	FailInfos     []*IndexFailInfo `json:"fail_infos"`
	Progress      float64          `json:"progress"`
}

// IndexFailInfo 索引失败信息
type IndexFailInfo struct {
	ID      string `json:"id"`
	FailMsg string `json:"fail_msg"`
	Name    string `json:"name"`
	Path    string `json:"path"`
	Gns     string `json:"gns"`
}

func GetMockBotIndexStatusInfoBys() []byte {
	return []byte(`{
		"bot_version": "1",
		"complete_count": 1,
		"fail_infos": [
			{
				"id": "1",
				"fail_msg": "1",
				"name": "1",
				"path": "1",
				"gns": "1"
			}
		],
		"progress": 1
	}`)
}
