export const mainAppProps = {
  businessDomainID: 'bd_public',
  changeCustomPathComponent: () => {},
  config: {
    systemInfo: {
      location: {
        protocol: 'http:',
        hostname: 'localhost',
        port: '1101',
      },
    },
    getTheme: {
      normal: '#126ee3',
    },
  },
  prefix: '',
  language: {
    getLanguage: 'zh-CN',
  },
  token: {
    getToken: {
      access_token: 'ory_at__AyXvqqVj9atU6uHc90r-05P05cfcAgsTzUcfj3GeW8.eMIs27BA_kYMWcVG2oPwu_wB8me3cqV9xSCD02gy5_w',
    },
    onTokenExpired: () => {},
    refreshOauth2Token: () => {},
  },
  history: {
    navigateToMicroWidget: () => {},
  },
  userid: '4b91118a-6f67-11f0-b0dc-36fa540cff80',
};
