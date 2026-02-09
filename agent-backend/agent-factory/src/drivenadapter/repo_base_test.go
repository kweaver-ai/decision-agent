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

func TestRepoBase_MultipleInstances(t *testing.T) {
	repo1 := NewRepoBase()
	repo2 := NewRepoBase()

	assert.NotNil(t, repo1)
	assert.NotNil(t, repo2)
	assert.NotSame(t, repo1, repo2)
}
