package daconfvalobj

import (
	"context"
	"sort"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/enum/cdaenum"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/valueobject/daconfvalobj/datasourcevalobj"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/valueobject/daconfvalobj/skillvalobj"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/capierr"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cutil"
	"github.com/pkg/errors"
)

// Config 表示agent配置
type Config struct {
	Input         *Input                                `json:"input" binding:"required"` // 输入参数
	SystemPrompt  string                                `json:"system_prompt"`            // 系统提示词
	Dolphin       string                                `json:"dolphin"`                  // Dolphin语句
	IsDolphinMode cdaenum.DolphinMode                   `json:"is_dolphin_mode"`          // 是否是dolphin模式
	PreDolphin    []*DolphinTpl                         `json:"pre_dolphin"`              // 在用户自定义dolphin之前执行的内置dolphin语句
	PostDolphin   []*DolphinTpl                         `json:"post_dolphin"`             // 在用户自定义dolphin之后执行的内置dolphin语句
	DataSource    *datasourcevalobj.RetrieverDataSource `json:"data_source"`              // 数据源
	Skill         *skillvalobj.Skill                    `json:"skills"`                   // 技能
	Llms          []*LlmItem                            `json:"llms"`                     // LLM配置

	IsDataFlowSetEnabled int                   `json:"is_data_flow_set_enabled"`   // 是否启用数据流设置
	OpeningRemarkConfig  *OpeningRemarkConfig  `json:"opening_remark_config"`      // 开场白配置
	PresetQuestions      []*PresetQuestion     `json:"preset_questions"`           // 预设问题列表
	Output               *Output               `json:"output"  binding:"required"` // 输出结果
	BuiltInCanEditFields *BuiltInCanEditFields `json:"built_in_can_edit_fields"`   // 内置agent可编辑字段配置
	MemoryCfg            *MemoryCfg            `json:"memory"`                     // 长期记忆配置
	RelatedQuestion      *RelatedQuestion      `json:"related_question"`           // 相关问题配置
	PlanMode             *PlanMode             `json:"plan_mode"`                  // 任务规划模式配置

	Metadata ConfigMetadata `json:"metadata"` // 配置元数据
}

func NewConfig() *Config {
	return &Config{}
}

func (p *Config) GetErrMsgMap() map[string]string {
	// 返回错误信息映射，用于将验证错误转换为用户友好的错误消息
	return map[string]string{
		"Input.required":  `"input"不能为空`,
		"Output.required": `"output"不能为空`,
	}
}

func (p *Config) ValObjCheckWithCtx(ctx context.Context, isPrivateAPI bool) (err error) {
	// 1. 检查Input是否为空
	if p.Input == nil {
		err = errors.New("[Config]: input is required")
		return
	}

	// 2. 验证Input的有效性
	if err = p.Input.ValObjCheck(); err != nil {
		err = errors.Wrap(err, "[Config]: input is invalid")
		return
	}

	// 3. 如果DataSource不为空，验证其有效性
	if p.DataSource != nil {
		if err = p.DataSource.ValObjCheckWithCtx(ctx); err != nil {
			err = errors.Wrap(err, "[Config]: data_source is invalid")
			return
		}
	}

	// 4. 如果Skill不为空，验证每个工具的有效性
	if p.Skill != nil {
		if err = p.Skill.ValObjCheck(); err != nil {
			err = errors.Wrap(err, "[Config]: tools is invalid")
			return
		}
	}

	// 5. 如果不是私有API，必须配置LLM
	if !isPrivateAPI && len(p.Llms) == 0 {
		err = capierr.NewCustom400Err(ctx, capierr.DataAgentConfigLlmRequired, "[Config]: llms is required when is_private_api is false")
		return
	}

	// 6. 验证LLM配置的有效性

	// 6.1 验证每个LLM配置的有效性
	if p.Llms != nil {
		isHasDefault := false

		for _, llm := range p.Llms {
			if err = llm.ValObjCheck(); err != nil {
				err = errors.Wrap(err, "[Config]: llms is invalid")
				return
			}

			if llm.IsDefault {
				isHasDefault = true
			}
		}

		if len(p.Llms) > 0 && !isHasDefault {
			err = errors.New("[Config]: llms must have at least one default llm")
			return
		}
	}

	// 7. 验证IsDataFlowSetEnabled的值必须为0或1
	if p.IsDataFlowSetEnabled != 0 && p.IsDataFlowSetEnabled != 1 {
		err = errors.New("[Config]: is_data_flow_set_enabled must be 0 or 1")
		return
	}

	// 8. 如果OpeningRemarkConfig不为空，验证其有效性
	if p.OpeningRemarkConfig != nil {
		if err = p.OpeningRemarkConfig.ValObjCheck(); err != nil {
			err = errors.Wrap(err, "[Config]: opening_remark_config is invalid")
			return
		}
	}

	// 9. 如果PresetQuestions不为空，验证每个预设问题的有效性
	if p.PresetQuestions != nil {
		for _, question := range p.PresetQuestions {
			if err = question.ValObjCheck(); err != nil {
				err = errors.Wrap(err, "[Config]: preset_questions is invalid")
				return
			}
		}
	}

	// 10. 验证dolphin相关配置
	if err = p.checkAboutDolphin(); err != nil {
		err = errors.Wrap(err, "[Config]: checkAboutDolphin is invalid")
		return
	}

	// 11. check output
	if p.Output == nil {
		p.Output = &Output{}
	}

	if err = p.Output.ValObjCheck(p.IsDolphinMode.Bool()); err != nil {
		err = errors.Wrap(err, "[Config]: output is invalid")
		return
	}

	// 12. 验证plan_mode相关配置
	if p.PlanMode != nil {
		// 12.1 验证plan_mode的有效性
		if err = p.PlanMode.ValObjCheck(); err != nil {
			err = errors.Wrap(err, "[Config]: plan_mode is invalid")
			return
		}

		// 12.2 验证plan_mode和is_dolphin_mode的冲突
		if p.PlanMode.IsEnabled && p.IsDolphinMode.Bool() {
			err = errors.New("[Config]: plan_mode is invalid when is_dolphin_mode is true")
			return
		}
	}

	return
}

// checkAboutDolphin 检查dolphin相关配置
func (p *Config) checkAboutDolphin() (err error) {
	// 1. 验证IsDolphinMode枚举值的有效性
	if err = p.IsDolphinMode.EnumCheck(); err != nil {
		err = errors.Wrap(err, "[Config]: is_dolphin_mode is invalid")
		return
	}

	// 2. check pre_dolphin
	if p.PreDolphin != nil {
		for _, tpl := range p.PreDolphin {
			if err = tpl.ValObjCheck(); err != nil {
				err = errors.Wrap(err, "[Config]: pre_dolphin is invalid")
				return
			}
		}
	}

	// 3. check post_dolphin
	if p.PostDolphin != nil {
		for _, tpl := range p.PostDolphin {
			if err = tpl.ValObjCheck(); err != nil {
				err = errors.Wrap(err, "[Config]: post_dolphin is invalid")
				return
			}
		}
	}

	// 4. 根据IsDolphinMode的值检查相关配置
	if p.IsDolphinMode.Bool() {
		// 如果启用了dolphin模式，判断pre_dolphin、post_dolphin、dolphin三者中至少有一个不为空
		if p.GetDolphinTplLength() == 0 && p.Dolphin == "" {
			err = errors.New("[Config]: pre_dolphin or post_dolphin or dolphin is required when is_dolphin_mode is enabled")
			return
		}
	} else if p.SystemPrompt == "" {
		// 去掉这里的验证（2025年05月29日16:24:47）
		// 如果未启用dolphin模式，system_prompt不能为空
		// err = errors.New("[Config]: system_prompt is required when is_dolphin_mode is disabled")
		// return
	}

	return
}

// GetBuiltInDsDocSourceFields 获取内置文档类型数据源字段
func (p *Config) GetBuiltInDsDocSourceFields() (fields []*datasourcevalobj.DocSourceField) {
	fields = []*datasourcevalobj.DocSourceField{}
	if p.DataSource != nil {
		fields = p.DataSource.GetBuiltInDsDocSourceFields()
	}

	return
}

func (p *Config) GetDocIDsHash() (indexKey string, err error) {
	ids := p.GetBuiltInDocObjIDs()
	if len(ids) == 0 {
		err = errors.New("[daconfvalobj][Config]: 没有内置doc数据源")
		return
	}

	// 排序
	sort.Strings(ids)

	bys, err := cutil.JSON().Marshal(ids)
	if err != nil {
		return
	}

	indexKey = cutil.Hash256(bys)

	return
}

func (p *Config) GetBuiltInDocObjIDs() (ids []string) {
	fields := p.GetBuiltInDsDocSourceFields()
	for _, field := range fields {
		id := field.GetDirObjID()
		if id != "" {
			ids = append(ids, id)
		}
	}

	return
}

func (p *Config) IsHasBuiltInDocSource() (has bool) {
	has = len(p.GetBuiltInDocObjIDs()) > 0

	return
}

func (p *Config) GetBuiltInDocDatasetId() (datasetId string) {
	if p.DataSource == nil {
		return
	}

	if len(p.DataSource.Doc) == 0 {
		return
	}

	datasetId = p.DataSource.GetFirstDocDatasetId()

	return
}

func (p *Config) ClearDsDocDatasets() {
	if p.DataSource == nil {
		return
	}

	if len(p.DataSource.Doc) == 0 {
		return
	}

	for _, doc := range p.DataSource.Doc {
		if doc.Datasets != nil {
			doc.Datasets = []string{}
		}
	}
}

func (p *Config) GetConfigMetadata() *ConfigMetadata {
	return &p.Metadata
}

// CheckProductAndDataSource 检查产品类型与数据源是否相符
func (p *Config) CheckProductAndDataSource(product cdaenum.Product) (err error) {
	if p.DataSource == nil {
		return
	}
	// 文档数据源不能用于智能问数产品
	if p.DataSource.Doc != nil {
		if product == cdaenum.ProductChatBI && len(p.DataSource.Doc) > 0 {
			err = errors.New("[Config]: 文档数据源不能用于智能问数产品")
			return
		}
	}

	return
}
