import { Button, message, Upload } from 'antd';
import DipIcon from '@/components/DipIcon';
import { forwardRef, type ReactNode, useImperativeHandle } from 'react';
import type { UploadProps } from 'antd';
import { useDipChatStore } from '@/components/DipChat/store.tsx';
import { createConversation } from '@/apis/super-assistant';
import { useMicroWidgetProps } from '@/hooks';
import { getFileListFromSandBox, uploadFileToSandBox } from '@/apis/sandbox';

export type FileUploadBtnProps = {
  disabled?: boolean;
  customBtn?: ReactNode;
  onSuccess?: () => void;
};

export type FileUploadBtnRef = {
  getFileList: () => void;
  clearFileList: () => void;
};

const FileUploadBtn = forwardRef<FileUploadBtnRef, FileUploadBtnProps>((props, ref) => {
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

  useImperativeHandle(ref, () => ({
    getFileList,
    clearFileList,
  }));

  const clearFileList = () => {
    setDipChatStore({ tempFileList: [] });
  };

  const getFileList = async () => {
    const conversationId = getDipChatStore().activeConversationKey;
    const path = `${conversationId}/uploads/temparea`;
    const res: any = await getFileListFromSandBox({
      sessionId,
      path,
      limit: 1000,
    });
    if (res) {
      console.log(res, '文件列表');
      const list = res.files.map((item: any) => ({
        ...item,
        checked: debug,
        status: 'completed',
      }));
      setDipChatStore({ tempFileList: list });
    }
  };

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
        if (!debug) {
          handleConversation(conversationId);
        } else {
          setDipChatStore({ activeConversationKey: conversationId });
        }
      }
      const filePath = `${conversationId}/uploads/temparea/${uploadFile.name}`;
      const res = await uploadFileToSandBox({
        file: uploadFile,
        sessionId,
        filePath,
      });
      if (res) {
        onSuccess?.(res);
        getFileList?.();
        props.onSuccess?.();
      }
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
});
FileUploadBtn.displayName = 'FileUploadBtn';
export default FileUploadBtn;
