package agentsvc

import (
	"fmt"
	"os"
	"path/filepath"
	"sync"
	"time"

	"github.com/kweaver-ai/decision-agent/agent-factory/src/infra/common/chelper/cenvhelper"
)

// StreamingResponseLogger 流式响应日志记录器
type StreamingResponseLogger struct {
	file           *os.File
	chunksCount    int
	totalBytes     int
	startTime      time.Time
	conversationID string
	mutex          sync.Mutex
}

// NewStreamingResponseLogger 创建流式响应日志记录器（仅 DEBUG 模式）
func NewStreamingResponseLogger(conversationID string) (*StreamingResponseLogger, error) {
	// 仅在 DEBUG 模式下启用
	if !cenvhelper.IsDebugMode() {
		return nil, nil
	}

	// 获取日志根目录
	logRootDir := os.Getenv("AGENT_FACTORY_LOCAL_DEV_LOG_ROOT_DIR")
	if logRootDir == "" {
		logRootDir = "log"
	}

	logDir := filepath.Join(logRootDir, "streaming_responses")
	if err := os.MkdirAll(logDir, 0755); err != nil {
		return nil, err
	}

	timestamp := time.Now().Format("20060102_150405")
	filename := fmt.Sprintf("%s_%s.log", timestamp, conversationID)
	filePath := filepath.Join(logDir, filename)

	file, err := os.Create(filePath)
	if err != nil {
		return nil, err
	}

	return &StreamingResponseLogger{
		file:           file,
		startTime:      time.Now(),
		conversationID: conversationID,
	}, nil
}

// LogChunk 记录一个数据块
func (l *StreamingResponseLogger) LogChunk(chunk []byte) {
	if l == nil || l.file == nil {
		return
	}

	l.mutex.Lock()
	defer l.mutex.Unlock()

	l.chunksCount++
	l.totalBytes += len(chunk)

	fmt.Fprintf(l.file, "[%s] Chunk %d (%d bytes):\n%s\n%s\n",
		time.Now().Format(time.RFC3339Nano),
		l.chunksCount,
		len(chunk),
		string(chunk),
		"==================================================",
	)
}

// Complete 完成日志记录
func (l *StreamingResponseLogger) Complete() {
	if l == nil || l.file == nil {
		return
	}

	l.mutex.Lock()
	defer l.mutex.Unlock()

	duration := time.Since(l.startTime)
	fmt.Fprintf(l.file, "\n[%s] Stream completed: %d chunks, %d bytes total, duration=%v\n",
		time.Now().Format(time.RFC3339Nano),
		l.chunksCount,
		l.totalBytes,
		duration,
	)

	l.file.Close()
}
