package conf

import (
	"sync"

	"github.com/kweaver-ai/decision-agent/agent-factory/cconf"
)

type AuthConf struct {
	Mechanism string `yaml:"mechanism"`
	Password  string `yaml:"password"`
	Username  string `yaml:"username"`
}

type MQConf struct {
	Auth          AuthConf `yaml:"auth"`
	ConnectorType string   `yaml:"connectorType"`
	MQHost        string   `yaml:"mqHost"`
	MQLookupdHost string   `yaml:"mqLookupdHost"`
	MQLookupdPort int      `yaml:"mqLookupdPort"`
	MQPort        int      `yaml:"mqPort"`
	MQType        string   `yaml:"mqType"`
	Protocol      string   `yaml:"protocol"`
	Tenant        string   `yaml:"tenant"`
}

// TODO?
func (c MQConf) IsDebug() bool {
	return true
}

type Config struct {
	*cconf.Config
	MQ MQConf

	// APP 配置字段
	AgentFactoryConf    *AgentFactoryConf    `yaml:"agent_factory"`
	AgentExecutorConf   *AgentExecutorConf   `yaml:"agent_executor"`
	FastConf            *EfastConf           `yaml:"efast"`
	DocsetConf          *DocsetConf          `yaml:"docset"`
	EcoConfigConf       *EcoConfigConf       `yaml:"ecoconfig"`
	UniqueryConf        *UniqueryConf        `yaml:"uniquery"`
	SandboxPlatformConf *SandboxPlatformConf `yaml:"sandbox_platform"`

	// 流式响应配置
	StreamDiffFrequency int `yaml:"stream_diff_frequency"`

	// OpenTelemetry 配置
	OtelConfig *OtelConfig `yaml:"opentelemetry"`

	// 是否保留老的APP路径，默认false
	KeepLegacyAppPath bool `yaml:"keep_legacy_app_path"`

	// 是否禁用权限检查，默认false
	DisablePmsCheck bool `yaml:"disable_pms_check"`

	// 是否禁用业务域初始化，默认false
	DisableBizDomainInit bool `yaml:"disable_biz_domain_init"`

	// 是否禁用审计日志初始化，默认false
	DisableAuditInit bool `yaml:"disable_audit_init"`

	// 是否使用Mock MQ客户端（本地开发时建议设置为true）
	MockMQClient bool `yaml:"mock_mq_client"`
}

func (c Config) IsDebug() bool {
	return c.Project.Debug
}

var (
	configOnce sync.Once
	configImpl *Config
)

func NewConfig() *Config {
	configOnce.Do(func() {
		configImpl = &Config{}
		configImpl.Config = cconf.BaseDefConfig()
		configImpl.OtelConfig = &OtelConfig{}

		bys := cconf.GetConfigBys("agent-factory.yaml")
		cconf.LoadConfig(bys, configImpl.Config)
		// 同时加载扩展字段（AgentFactoryConf等）
		cconf.LoadConfig(bys, configImpl)

		setOtelDefaults(configImpl.OtelConfig)

		secretBys := cconf.GetConfigBys("secret/agent-factory-secret.yaml")
		cconf.LoadConfig(secretBys, configImpl.Config)

		mqBys := cconf.GetConfigBys("mq_config.yaml")
		cconf.LoadConfig(mqBys, &configImpl.MQ)
	})

	return configImpl
}
