import React from 'react'
import ReactDOM from 'react-dom/client'
import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom";
import { App, ConfigProvider } from 'antd';

import AppPlatorm from './routes/App'
import TagFaces from './tagFaces/TagFaces'
import Events from './events/events'
import ErrorPage from "./error-page";
import './index.css'

const router = createBrowserRouter([
  {
    path: "/",
    element: <AppPlatorm />,
    errorElement: <ErrorPage />,
    children: [
      {
        path: "/",
        element: <TagFaces />,
      },
      {
        path: "/events",
        element: <Events />,
      },
    ],
  },
]);

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ConfigProvider theme={{
        token: {
          colorPrimary: '#00b96b'
        },
        //algorithm: theme.darkAlgorithm,
      }}>
      <App>
        <RouterProvider router={router} />
      </App>
    </ConfigProvider>
  </React.StrictMode>,
)
