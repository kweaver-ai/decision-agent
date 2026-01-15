package uniqueryaccess

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"path/filepath"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/drivenadapter/httpaccess/uniqueryaccess/uniquerydto"
	o11y "github.com/kweaver-ai/kweaver-go-lib/observability"
	"github.com/bytedance/sonic"
	"github.com/pkg/errors"
	"go.opentelemetry.io/otel/attribute"
)

func (uq *uniqueryHttpAcc) GetDataView(ctx context.Context, viewID string, reqData uniquerydto.ReqDataView) (uniquerydto.ViewResults, error) {
	var err error

	ctx, _ = o11y.StartInternalSpan(ctx)
	defer o11y.EndSpan(ctx, err)
	o11y.SetAttributes(ctx, attribute.String("view_id", viewID))

	uri := fmt.Sprintf("%s/api/mdl-uniquery/in/v1/data-views/%s?include_view=false", uq.privateAddress, viewID)

	// 设置请求头
	headers := map[string]string{
		"Content-Type":           "application/json",
		"x-http-method-override": "GET",
		"x-language":             "zh-CN",
		"x-account-id":           reqData.XAccountID,
		"x-account-type":         reqData.XAccountType,
	}

	code, res, err := uq.client.PostNoUnmarshal(ctx, uri, headers, reqData)
	if err != nil {
		o11y.Error(ctx, fmt.Sprintf("[GetDataViews] request uri %s err %s", uri, err))
		err = errors.Wrapf(err, "[GetDataViews] request uri %s err %s", uri, err)

		return uniquerydto.ViewResults{}, err
	}

	if code != http.StatusOK {
		o11y.Error(ctx, fmt.Sprintf("[GetDataViews] status code: %d , resp %s", code, string(res)))
		return uniquerydto.ViewResults{}, fmt.Errorf("status code: %d , resp %s", code, string(res))
	}

	// 反序列化响应数据
	var response uniquerydto.ViewResults

	err = sonic.Unmarshal(res, &response)
	if err != nil {
		o11y.Error(ctx, fmt.Sprintf("[GetDataViews] request uri %s unmarshal err %s,  resp %s ", uri, err, string(res)))
		return uniquerydto.ViewResults{}, errors.Wrapf(err, "[GetDataViews] request uri %s unmarshal err %s,  resp %s ", uri, err, string(res))
	}

	return response, nil
}

func (uq *uniqueryHttpAcc) GetDataViewMock(ctx context.Context, viewID string, reqData uniquerydto.ReqDataView, mockType string) (uniquerydto.ViewResults, error) {
	// 根据mockType参数选择不同的JSON文件
	var fileName string

	switch mockType {
	case "run_detail":
		fileName = "run_detail.json"
	case "run_list":
		fileName = "run_list.json"
	case "session_list":
		fileName = "session_list.json"
	default:
		return uniquerydto.ViewResults{}, nil
	}

	currentDir := filepath.Dir("./src/drivenadapter/httpaccess/uniqueryaccess/")
	jsonPath := filepath.Join(currentDir, fileName)

	// 读取JSON文件
	data, err := os.ReadFile(jsonPath)
	if err != nil {
		return uniquerydto.ViewResults{}, err
	}

	// 解析JSON数据
	var jsonData struct {
		Entries []interface{} `json:"entries"`
	}

	if err := json.Unmarshal(data, &jsonData); err != nil {
		return uniquerydto.ViewResults{}, err
	}

	// 构建返回结果
	response := uniquerydto.ViewResults{
		Entries:    jsonData.Entries,
		TotalCount: len(jsonData.Entries),
	}

	return response, nil
}
