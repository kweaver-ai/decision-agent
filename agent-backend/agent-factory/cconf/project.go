package cconf

import (
	"errors"

	"github.com/kweaver-ai/kweaver-go-lib/rest"
	"go.uber.org/zap/zapcore"
)

type Project struct {
	Host        string        `yaml:"host"`
	Port        int           `yaml:"port"`
	Language    rest.Language `yaml:"language"`
	LoggerLevel zapcore.Level `yaml:"logger_level"`
	Debug       bool          `yaml:"debug" env:"DEBUG"`
	DebugHost   string        `yaml:"debug_host"`
}

func (p *Project) Check() (err error) {
	if p.Language == "" {
		err = errors.New("[cconf.Project]:language is empty")
		return
	}

	if p.Language != rest.SimplifiedChinese && p.Language != rest.AmericanEnglish {
		err = errors.New("[cconf.Project]:language is invalid")
		return
	}

	return
}
