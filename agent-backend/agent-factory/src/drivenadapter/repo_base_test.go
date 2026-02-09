package drivenadapter

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestNewRepoBase(t *testing.T) {
	repo := NewRepoBase()

	assert.NotNil(t, repo)
	assert.IsType(t, &RepoBase{}, repo)
}

func TestRepoBase_Struct(t *testing.T) {
	repo := &RepoBase{}

	assert.NotNil(t, repo)
}

func TestRepoBase_IsValidBase(t *testing.T) {
	// Verify RepoBase can be used as a base for other repository structs
	type testRepo struct {
		*RepoBase
		Name string
	}

	repo := &testRepo{
		RepoBase: NewRepoBase(),
		Name:     "test",
	}

	assert.NotNil(t, repo.RepoBase)
	assert.Equal(t, "test", repo.Name)
}
