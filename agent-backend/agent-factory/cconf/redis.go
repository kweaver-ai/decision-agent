package cconf

type RedisConf struct {
	ConnectType string `yaml:"connect_type" env:"REDISCLUSTERMODE"` // 部署方式 sentinel:哨兵模式 master-slave:主从模式 cluster:集群模式 standalone:单机模式

	UserName string `yaml:"username" env:"REDISUSER"`
	Password string `yaml:"password" env:"REDISPASS"`

	// standalone
	Host string `yaml:"host" env:"REDISHOST"`
	Port string `yaml:"port" env:"REDISPORT"`

	// sentinel
	MasterGroupName  string `yaml:"master_group_name" env:"SENTINELMASTER"`
	SentinelHost     string `yaml:"sentinel_host" env:"REDISHOST"`
	SentinelPort     string `yaml:"sentinel_port" env:"REDISPORT"`
	SentinelUsername string `yaml:"sentinel_username" env:"SENTINELUSER"`
	SentinelPwd      string `yaml:"sentinel_password" env:"SENTINELPASS"`

	// master-slave
	MasterHost string `yaml:"master_host" env:"REDISWRITEHOST"`
	MasterPort string `yaml:"master_port" env:"REDISWRITEPORT"`
	SlaveHost  string `yaml:"slave_host" env:"REDISREADHOST"`
	SlavePort  string `yaml:"slave_port" env:"REDISREADPORT"`

	// cluster 弃用，proton不支持这种模式
	ClusterHosts []string `yaml:"cluster_addrs"`
	ClusterPwd   string   `yaml:"cluster_password"`

	DB                 int `yaml:"db"`                   // 数据库
	MaxRetries         int `yaml:"max_retries"`          // 最大重试次数
	PoolSize           int `yaml:"pool_size"`            // 连接池大小
	ReadTimeout        int `yaml:"read_timeout"`         // 读取超时时间 默认3秒
	WriteTimeout       int `yaml:"write_timeout"`        // 写入超时时间 默认3秒
	IdleTimeout        int `yaml:"idle_timeout"`         // 连接空闲时间 默认300秒
	IdleCheckFrequency int `yaml:"idle_check_frequency"` // 检测死连接并清理 默认60秒
	MaxConnAge         int `yaml:"max_conn_age"`         // 连接最长时间 默认300秒
	PoolTimeout        int `yaml:"pool_timeout"`         // 如果连接池已满 等待可用连接的时间 默认8秒
}
