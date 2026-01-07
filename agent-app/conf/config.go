package conf

import (
	"sync"

	"github.com/kweaver-ai/decision-agent/agent-app/appruntime"
	"github.com/kweaver-ai/agent-go-common-pkg/src/infra/common/chelper/cenvhelper"

	"github.com/kweaver-ai/agent-go-common-pkg/cconf"
	o11y "github.com/kweaver-ai/kweaver-go-lib/observability"
	"github.com/spf13/viper"
)

type Config struct {
	*cconf.Config

	AgentFactoryConf  *AgentFactoryConf  `yaml:"agent_factory"`
	AgentExecutorConf *AgentExecutorConf `yaml:"agent_executor"`
	EfastConf         *EfastConf         `yaml:"efast"`
	DocsetConf        *DocsetConf        `yaml:"docset"`
	EcoConfigConf     *EcoConfigConf     `yaml:"ecoconfig"`
	UniqueryConf      *UniqueryConf      `yaml:"uniquery"`
	// 可观测性相关配置
	O11yCfg *o11y.ObservabilitySetting
	// 流式响应配置
	StreamDiffFrequency int `yaml:"stream_diff_frequency"`
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
		configImpl.O11yCfg = &o11y.ObservabilitySetting{}

		bys := cconf.GetConfigBys("agent-app.yaml")
		cconf.LoadConfig(bys, configImpl.Config)

		secretBys := cconf.GetConfigBys("secret/agent-app-secret.yaml")
		cconf.LoadConfig(secretBys, configImpl.Config)

		// NOTE: 加载configImpl
		cconf.LoadConfig(bys, configImpl)

		init_o11y()
	})

	return configImpl
}

// 加载&初始化可观测性相关配置
func init_o11y() {
	if cenvhelper.IsLocalDev(cenvhelper.RunScenario_Aaron_Local_Dev) {
		return
	}

	viper.SetConfigName("observability")
	viper.SetConfigType("yaml")
	viper.AddConfigPath("/sysvol/conf/")

	if err := viper.ReadInConfig(); err != nil {
		panic(err)
	}

	if err := viper.Unmarshal(&configImpl.O11yCfg); err != nil {
		panic(err)
	}

	serverInfo := o11y.ServerInfo{
		ServerName:    appruntime.ServerName,
		ServerVersion: appruntime.ServerVersion,
		Language:      appruntime.LanguageGo,
		GoVersion:     appruntime.GoVersion,
		GoArch:        appruntime.GoArch,
	}

	o11y.Init(serverInfo, *configImpl.O11yCfg)
}
