package conf

import "github.com/kweaver-ai/decision-agent/agent-factory/cconf"

// SandboxPlatformConf Sandbox Platform 配置
type SandboxPlatformConf struct {
	SvcConf                 cconf.SvcConf      `yaml:"svc"`
	DefaultTTL              int64               `yaml:"default_ttl"`     // 默认 Session TTL（秒）
	MaxRetries               int                 `yaml:"max_retries"`     // 等待 Session 就绪的最大重试次数
	RetryInterval            string              `yaml:"retry_interval"`  // 重试间隔（如 "500ms"）
	DefaultFileUploadConfig   FileUploadConfig    `yaml:"file_upload_config"`
}

// FileUploadConfig 文件上传配置
type FileUploadConfig struct {
	MaxFileSize      int64    `yaml:"max_file_size"`      // 最大文件大小（数值）
	MaxFileSizeUnit  string   `yaml:"max_file_size_unit"` // 单位：KB/MB/GB
	MaxFileCount     int      `yaml:"max_file_count"`     // 最大文件数量
	AllowedFileTypes []string `yaml:"allowed_file_types"` // 允许的文件类型
}
