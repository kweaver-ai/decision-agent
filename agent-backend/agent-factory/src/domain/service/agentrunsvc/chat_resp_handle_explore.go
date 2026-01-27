package agentsvc

import (
	"context"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/valueobject/agentrespvo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/valueobject/conversationmsgvo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cutil"
	otelTrace "github.com/kweaver-ai/decision-agent/agent-factory/src/infra/opentelemetry/trace"
)

type handleExploreDto struct {
	exploreAnswerList []*agentrespvo.AnswerExplore
	nameToTypeMap     map[string]string
}

func (agentSvc *agentSvc) handleExplore(ctx context.Context, dto handleExploreDto) (mainThinking string, skillsProcess []*conversationmsgvo.SkillsProcessItem, err error) {
	ctx, _ = otelTrace.StartInternalSpan(ctx)
	defer otelTrace.EndSpan(ctx, err)

	skillsProcess = make([]*conversationmsgvo.SkillsProcessItem, 0, len(dto.exploreAnswerList))

	for i := range dto.exploreAnswerList {
		skillsItem := &conversationmsgvo.SkillsProcessItem{}

		err = cutil.CopyStructUseJSON(skillsItem, dto.exploreAnswerList[i])
		if err != nil {
			return
		}

		skillsItem.Type = dto.nameToTypeMap[skillsItem.AgentName]

		skillName := dto.exploreAnswerList[i].AgentName

		//	AgentName   == main   取  answer 字段 作为返回
		//	AgentName   ！= main   取  BlockAnswer 字段 作为返回
		if skillName == "main" {
			_dto := &mainHandleDto{
				skillsItem:        skillsItem,
				exploreAnswerList: dto.exploreAnswerList,
				i:                 i,
				mainThinking:      &mainThinking,
				skillsProcess:     skillsProcess,
			}
			skillsProcess = agentSvc.mainHandle(ctx, _dto)
		} else {
			if skillsItem.Type == "tool" {
				_dto := &toolHandleDto{
					exploreAnswerList: dto.exploreAnswerList,
					i:                 i,
					skillsItem:        skillsItem,
					skillsProcess:     skillsProcess,
				}
				skillsProcess, err = agentSvc.toolHandle(ctx, _dto)
			} else {
				_dto := &agentToolHandleDto{
					exploreAnswerList: dto.exploreAnswerList,
					i:                 i,
					skillsItem:        skillsItem,
					skillsProcess:     skillsProcess,
				}
				skillsProcess, err = agentSvc.agentToolHandle(ctx, _dto)
			}
		}
	}

	return
}
