import styles from './index.module.less';
import { Splitter } from 'antd';
import DataSourceArea from './DataSourceArea';
import FileArea from './FileArea';
import type { FileItem, PreviewFileType } from '@/components/DipChat/interface';
import classNames from 'classnames';
import { getFileExtension } from '@/utils/doc';
import { useDipChatStore } from '@/components/DipChat/store';

const TempArea = () => {
  const {
    dipChatStore: { agentDetails, previewFile },
    setDipChatStore,
  } = useDipChatStore();
  const { data_source } = agentDetails?.config || {};
  const knExperimentalDataSource = data_source?.knowledge_network ?? [];
  const metricTreeDataSource = data_source?.metric ?? [];

  const setPreviewFile = (file: PreviewFileType | undefined) => {
    setDipChatStore({
      previewFile: file,
    });
  };

  const renderContent = () => {
    // 只配置了配置了临时区
    if (knExperimentalDataSource.length === 0 && metricTreeDataSource.length === 0) {
      return (
        <FileArea
          onPreviewFile={(file: FileItem) => {
            setPreviewFile({
              fileId: file.id,
              fileExt: getFileExtension(file.name),
              fileName: file.name,
            });
          }}
        />
      );
    }

    return (
      <Splitter layout="vertical">
        <Splitter.Panel>
          <FileArea />
        </Splitter.Panel>
        <Splitter.Panel>
          <DataSourceArea />
        </Splitter.Panel>
      </Splitter>
    );
  };

  return (
    <div className={classNames(styles.container)} style={{ display: previewFile ? 'none' : 'block' }}>
      {renderContent()}
    </div>
  );
};

export default TempArea;
