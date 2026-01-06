package conf

import (
    "sync"

    "github.com/kweaver-ai/agent-go-common-pkg/cconf"
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

        bys := cconf.GetConfigBys("agent-factory.yaml")
        cconf.LoadConfig(bys, configImpl.Config)

        secretBys := cconf.GetConfigBys("secret/agent-factory-secret.yaml")
        cconf.LoadConfig(secretBys, configImpl.Config)

        mqBys := cconf.GetConfigBys("mq_config.yaml")
        cconf.LoadConfig(mqBys, &configImpl.MQ)
    })

    return configImpl
}
