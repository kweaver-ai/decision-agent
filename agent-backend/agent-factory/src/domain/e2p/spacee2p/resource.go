package spacee2p

import (
	"github.com/kweaver-ai/decision-agent/agent-factory/src/domain/entity/spaceeo"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/cutil"
	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/persistence/dapo"
)

// SpaceResources 将多个空间资源实体转换为持久化对象
func SpaceResources(eos []*spaceeo.SpaceResource) (pos []*dapo.SpaceResourcePo, err error) {
	pos = make([]*dapo.SpaceResourcePo, 0, len(eos))

	for i := range eos {
		var po *dapo.SpaceResourcePo

		if po, err = SpaceResource(eos[i]); err != nil {
			return
		}

		pos = append(pos, po)
	}

	return
}

// SpaceResource 将单个空间资源实体转换为持久化对象
func SpaceResource(eo *spaceeo.SpaceResource) (po *dapo.SpaceResourcePo, err error) {
	po = &dapo.SpaceResourcePo{}

	err = cutil.CopyStructUseJSON(po, eo.SpaceResourcePo)
	if err != nil {
		return
	}

	return
}
