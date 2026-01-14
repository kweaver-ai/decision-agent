package dolphintpleo

import (
	"fmt"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/enum/cdaenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/valueobject/daconfvalobj"
)

type TempFileProcessContent struct {
	Content           string `json:"content"`
	IsEnable          bool
	TempZoneFieldName string `json:"temp_zone_field_name"`
}

func NewTempFileProcessContent() *TempFileProcessContent {
	return &TempFileProcessContent{
		Content: "",
	}
}

func (t *TempFileProcessContent) LoadFromConfig(config *daconfvalobj.Config) {
	if config.Input.IsTempZoneEnabled == cdaenum.TempZoneEnabled {
		t.Content, t.TempZoneFieldName = config.Input.Fields.GenFileDolphinStr()
		t.IsEnable = true
	}
}

func (t *TempFileProcessContent) ToString() (str string) {
	str = fmt.Sprintf(`
%s
`, t.Content)

	return
}

func (t *TempFileProcessContent) ToDolphinTplEo() *DolphinTplEo {
	key := cdaenum.DolphinTplKeyTempFileProcess

	return &DolphinTplEo{
		Key:   key,
		Name:  key.GetName(),
		Value: t.ToString(),
	}
}
