package cdaenum

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestConversationMsgStatus_Constants(t *testing.T) {
	assert.Equal(t, ConversationMsgStatus("received"), MsgStatusReceived)
	assert.Equal(t, ConversationMsgStatus("processed"), MsgStatusProcessed)
	assert.Equal(t, ConversationMsgStatus("processing"), MsgStatusProcessing)
	assert.Equal(t, ConversationMsgStatus("succeded"), MsgStatusSucceded)
	assert.Equal(t, ConversationMsgStatus("failed"), MsgStatusFailed)
	assert.Equal(t, ConversationMsgStatus("cancelled"), MsgStatusCancelled)
}

func TestConversationMsgStatus_EnumCheck_Valid(t *testing.T) {
	validStatuses := []ConversationMsgStatus{
		MsgStatusReceived,
		MsgStatusProcessed,
		MsgStatusProcessing,
		MsgStatusSucceded,
		MsgStatusFailed,
		MsgStatusCancelled,
	}

	for _, status := range validStatuses {
		t.Run(string(status), func(t *testing.T) {
			err := status.EnumCheck()
			assert.NoError(t, err)
		})
	}
}

func TestConversationMsgStatus_EnumCheck_Invalid(t *testing.T) {
	invalidStatus := ConversationMsgStatus("invalid_status")
	err := invalidStatus.EnumCheck()
	assert.Error(t, err)
	assert.Contains(t, err.Error(), "消息状态不合法")
}

func TestConversationMsgStatus_EnumCheck_Empty(t *testing.T) {
	emptyStatus := ConversationMsgStatus("")
	err := emptyStatus.EnumCheck()
	assert.Error(t, err)
}

func TestConversationMsgStatus_AllUnique(t *testing.T) {
	statuses := []ConversationMsgStatus{
		MsgStatusReceived,
		MsgStatusProcessed,
		MsgStatusProcessing,
		MsgStatusSucceded,
		MsgStatusFailed,
		MsgStatusCancelled,
	}

	uniqueStatuses := make(map[ConversationMsgStatus]bool)
	for _, status := range statuses {
		assert.False(t, uniqueStatuses[status], "Duplicate status found: %s", status)
		uniqueStatuses[status] = true
	}
}
