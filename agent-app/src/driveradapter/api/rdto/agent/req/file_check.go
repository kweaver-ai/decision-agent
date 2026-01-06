package agentreq

type (
	FileCheckReq []FileCheck
	FileCheck    struct {
		ID string `json:"id"`
	}
)
