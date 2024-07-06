import React from 'react'
import ReactDOM from 'react-dom/client'
import { App, ConfigProvider } from 'antd';

import AppPlatorm from './App.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ConfigProvider theme={{
        token: {
          colorPrimary: '#00b96b'
        },
        //algorithm: theme.darkAlgorithm,
      }}>
      <App>
        <AppPlatorm />
      </App>
    </ConfigProvider>
  </React.StrictMode>,
)
