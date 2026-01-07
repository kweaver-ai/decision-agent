package appruntime

import (
	"runtime"
)

var (
	ServerName    string = "agent-app"
	ServerVersion string = "1.0.0"
	LanguageGo    string = "go"
	GoVersion     string = runtime.Version()
	GoArch        string = runtime.GOARCH
)
