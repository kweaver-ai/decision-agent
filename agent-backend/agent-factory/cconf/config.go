package cconf

import (
	"fmt"
	"log"
	"os"
	"path/filepath"
	"reflect"
	"strconv"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/chelper/cenvhelper"
	"github.com/kweaver-ai/kweaver-go-lib/rest"
	"gopkg.in/yaml.v3"
)

var _configPath string

func GetConfigPath() string {
	if _configPath != "" {
		return _configPath
	}

	_configPath = "/sysvol/conf/"
	if _, err := os.Stat(_configPath); os.IsNotExist(err) {
		_configPath = "./conf"
	}

	if cenvhelper.ConfigPathFromEnv() != "" {
		_configPath = cenvhelper.ConfigPathFromEnv()
	}

	return _configPath
}

type Config struct {
	Project Project   `yaml:"project"`
	DB      DBConf    `yaml:"db"`
	Redis   RedisConf `yaml:"redis"`
	Hydra   HydraCfg  `yaml:"hydra"`

	ModelFactory   *ModelFactoryConf   `yaml:"model_factory"`
	EcoIndex       *EcoIndexConf       `yaml:"eco_index"`
	DataHubCentral *DataHubCentralConf `yaml:"datahubcentral"`
	Authorization  *AuthzCfg           `yaml:"authorization"`
	AgentFactory   *AgentFactoryConf   `yaml:"agent_factory"`
	BizDomain      *BizDomainConf      `yaml:"biz_domain"`

	MqCfgPath string
}

func (c *Config) IsDebug() bool {
	return c.Project.Debug
}

func (c *Config) Check() (err error) {
	err = c.Project.Check()
	if err != nil {
		return
	}

	return
}

func (c *Config) GetDefaultLanguage() rest.Language {
	return c.Project.Language
}

// GetLogLevelString 获取日志级别字符串
func (c *Config) GetLogLevelString() string {
	return c.Project.LoggerLevel.String()
}

func BaseDefConfig() (defConf *Config) {
	defConf = &Config{
		Project: Project{
			Host:        "0.0.0.0",
			Port:        30777,
			Language:    rest.SimplifiedChinese,
			LoggerLevel: 1,
			Debug:       false,
			DebugHost:   "",
		},
		DB: DBConf{
			UserName:         "anyshare",
			Password:         "eisoo.com123",
			DBHost:           "",
			DBPort:           3330,
			DBName:           "dip_data_agent",
			Charset:          "utf8mb4",
			Timeout:          10,
			TimeoutRead:      10,
			TimeoutWrite:     10,
			MaxOpenConns:     30,
			MaxOpenReadConns: 30,
		},
		Redis: RedisConf{
			ConnectType:        "",
			UserName:           "",
			Password:           "",
			Host:               "",
			Port:               "",
			MasterGroupName:    "",
			SentinelHost:       "",
			SentinelPort:       "",
			SentinelUsername:   "",
			SentinelPwd:        "",
			MasterHost:         "",
			MasterPort:         "",
			SlaveHost:          "",
			SlavePort:          "",
			ClusterHosts:       nil,
			ClusterPwd:         "",
			DB:                 3,
			MaxRetries:         0,
			PoolSize:           0,
			ReadTimeout:        0,
			WriteTimeout:       0,
			IdleTimeout:        0,
			IdleCheckFrequency: 0,
			MaxConnAge:         0,
			PoolTimeout:        0,
		},
	}

	defConf.MqCfgPath = filepath.Join(GetConfigPath(), "mq_config.yaml")

	return
}

func GetConfigBys(fileName string) []byte {
	configFilePath := filepath.Join(GetConfigPath(), fileName)

	file, err := os.ReadFile(configFilePath)
	if err != nil {
		log.Fatalf("load %v failed: %v", configFilePath, err)
	}

	return file
}

func LoadConfig(file []byte, configImpl IConf) IConf {
	err := yaml.Unmarshal(file, configImpl)
	if err != nil {
		log.Fatalf("unmarshal yaml file failed: %v", err)
	}

	overrideWithEnv(configImpl)

	if configImpl.IsDebug() {
		conf := configImpl
		fmt.Println(conf)
	}

	return configImpl
}

// overrideWithEnv 自动遍历结构体，用反射根据 tag 进行环境变量覆盖
func overrideWithEnv(cfg interface{}) {
	v := reflect.ValueOf(cfg).Elem() // 获取指向结构体的指针
	t := v.Type()

	for i := 0; i < v.NumField(); i++ {
		field := v.Field(i)
		fieldType := t.Field(i)

		if field.Kind() == reflect.Struct {
			// 递归处理嵌套结构体
			overrideWithEnv(field.Addr().Interface())
			continue
		}

		// 获取字段的 env 标签
		envTag := fieldType.Tag.Get("env")
		if envTag == "" {
			continue // 如果没有定义 env 标签，跳过
		}

		// 判断环境变量是否存在
		envValue, exists := os.LookupEnv(envTag)
		if !exists {
			continue // 如果环境变量 key 不存在，跳过
		}

		// 如果 key 存在但值为空，则将字段设为类型的零值
		if envValue == "" {
			field.Set(reflect.Zero(field.Type()))
			continue
		}

		// 使用反射直接设置字段值，要求类型匹配
		switch field.Kind() {
		case reflect.String:
			field.SetString(envValue)
		case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64:
			intValue, err := strconv.ParseInt(envValue, 10, 64)
			if err == nil {
				field.SetInt(intValue)
			}
		case reflect.Bool:
			boolValue, err := strconv.ParseBool(envValue)
			if err == nil {
				field.SetBool(boolValue)
			}
		default:
			panic("Unsupported field type for env override")
		}
	}
}
