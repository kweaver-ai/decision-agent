package cconf

type BizDomainConf struct {
	PrivateSvc *BizDomainSvcConf `yaml:"private_svc"`
}

type BizDomainSvcConf struct {
	Host     string `yaml:"host" env:"BIZDOMAIN_HOST"`
	Port     int    `yaml:"port" env:"BIZDOMAIN_PORT"`
	Protocol string `yaml:"protocol" env:"BIZDOMAIN_PROTOCOL"`
}
