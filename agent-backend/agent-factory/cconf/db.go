package cconf

type DBConf struct {
	UserName string `yaml:"user_name" env:"RDSUSER"`
	Password string `yaml:"user_pwd" env:"RDSPASS"`
	DBHost   string `yaml:"db_host" env:"RDSHOST"`
	DBPort   int    `yaml:"db_port" env:"RDSPORT"`
	DBName   string `yaml:"db_name" env:"RDSDBNAME"`

	Charset          string `yaml:"db_charset"`
	Timeout          int    `yaml:"timeout"`
	TimeoutRead      int    `yaml:"read_timeout"`
	TimeoutWrite     int    `yaml:"write_timeout"`
	MaxOpenConns     int    `yaml:"max_open_conns"`
	MaxOpenReadConns int    `yaml:"max_open_read_conns"`
}
