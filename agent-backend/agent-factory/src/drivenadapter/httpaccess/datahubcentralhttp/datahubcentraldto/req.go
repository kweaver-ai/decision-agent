package datahubcentraldto

type CreateDatasetsReq struct {
	UserID      string                  `json:"user_id"`
	DatasetName string                  `json:"dataset_name"`
	Items       []*DataSetUpsertReqItem `json:"items"`
}

type DataSetUpsertReqItem struct {
	Type   string `json:"type"`
	Value  string `json:"value"`
	Name   string `json:"name"`
	Config string `json:"config"`
}
