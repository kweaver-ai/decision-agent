import { Button, message, Upload } from 'antd';
import DipIcon from '@/components/DipIcon';
import { type ReactNode } from 'react';
import type { UploadProps } from 'antd';
import { useDipChatStore } from '@/components/DipChat/store.tsx';
import { post } from '@/utils/http';
import { createConversation } from '@/apis/super-assistant';
import { useMicroWidgetProps } from '@/hooks';

export type FileUploadBtnProps = {
  disabled?: boolean;
  customBtn?: ReactNode;
};

const FileUploadBtn = (props: FileUploadBtnProps) => {
  const microWidgetProps = useMicroWidgetProps();
  const {
    dipChatStore: { agentDetails, agentAppKey, debug },
    getDipChatStore,
    setDipChatStore,
    getConversationData,
  } = useDipChatStore();
  const { disabled = false, customBtn } = props;
  const [messageApi, contextHolder] = message.useMessage();
  const sessionId = `sess-${microWidgetProps.userid}`;

  // 处理对话创建后的 store 和 URL 更新
  const handleConversation = (conversation_id: string) => {
    const url = new URL(window.location.href);
    url.searchParams.set('conversation_id', conversation_id);
    // 使用 history API 更新 URL 而不刷新页面
    window.history.replaceState({}, '', url.toString());
    setDipChatStore({ activeConversationKey: conversation_id });
    getConversationData();
  };

  // 自定义上传逻辑
  const customRequest: UploadProps['customRequest'] = async options => {
    const { file, onSuccess, onError } = options;
    const uploadFile = file as File;

    try {
      let conversationId = getDipChatStore().activeConversationKey;

      // 1. 如果没有 activeConversationKey，先创建对话
      if (!conversationId) {
        const conversationRes = await createConversation(agentAppKey, {
          agent_id: agentDetails.id,
          agent_version: debug ? 'v0' : agentDetails.version,
          executor_version: 'v2',
        });

        if (!conversationRes) {
          throw new Error('创建对话失败');
        }

        conversationId = conversationRes.id;
        // 更新 URL 和 store
        handleConversation(conversationId);
      }

      // 2. 构建上传 URL
      const customPath = `${conversationId}/uploads/temparea/${uploadFile.name}`;
      const uploadUrl = `/api/v1/sessions/${sessionId}/files/upload?path=${customPath}`;

      // 3. 使用 FormData 上传文件
      const formData = new FormData();
      formData.append('file', uploadFile);

      const res = await post(uploadUrl, {
        body: formData,
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      onSuccess?.(res);
      // TODO: 上传成功后，根据实际需求更新 tempFileList
    } catch (error: any) {
      messageApi.error(error.message || '上传失败');
      onError?.(error);
    }
  };

  const uploadProps: UploadProps = {
    customRequest,
    showUploadList: false,
    maxCount: 1,
    disabled,
  };

  return (
    <>
      {contextHolder}
      <Upload {...uploadProps}>{customBtn || <Button icon={<DipIcon type="icon-dip-attachment" />} />}</Upload>
    </>
  );
};

export default FileUploadBtn;
