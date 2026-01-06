SET SCHEMA dip_data_agent;

CREATE TABLE if not exists t_biz_domain_agent_rel
(
    f_id            BIGINT      not null IDENTITY(1, 1),
    f_biz_domain_id VARCHAR(40 CHAR) not null,
    f_agent_id      VARCHAR(40 CHAR) not null,
    f_created_at    BIGINT      not null default 0,
    CLUSTER PRIMARY KEY (f_id)
);

CREATE UNIQUE INDEX IF NOT EXISTS t_biz_domain_agent_rel_uk_biz_domain_id_agent_id ON t_biz_domain_agent_rel(f_biz_domain_id, f_agent_id);
CREATE INDEX IF NOT EXISTS t_biz_domain_agent_rel_idx_agent_id ON t_biz_domain_agent_rel(f_agent_id);



CREATE TABLE if not exists t_biz_domain_agent_tpl_rel
(
    f_id            BIGINT      not null IDENTITY(1, 1),
    f_biz_domain_id VARCHAR(40 CHAR) not null,
    f_agent_tpl_id  BIGINT      not null,
    f_created_at    BIGINT      not null default 0,
    CLUSTER PRIMARY KEY (f_id)
);

CREATE UNIQUE INDEX IF NOT EXISTS t_biz_domain_agent_tpl_rel_uk_biz_domain_id_agent_tpl_id ON t_biz_domain_agent_tpl_rel(f_biz_domain_id, f_agent_tpl_id);
CREATE INDEX IF NOT EXISTS t_biz_domain_agent_tpl_rel_idx_agent_tpl_id ON t_biz_domain_agent_tpl_rel(f_agent_tpl_id);

