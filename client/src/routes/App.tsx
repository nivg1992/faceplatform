import { useState } from 'react';
import { Outlet, NavLink, useLocation } from 'react-router-dom';
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  UploadOutlined,
  UserOutlined,
  VideoCameraOutlined
} from '@ant-design/icons';
import { Button, Layout, Menu, theme, Typography, Flex } from 'antd';
import './App.css';

const { Title } = Typography;
const { Header, Sider, Content, Footer } = Layout;

function App() {
  const location = useLocation();
  const { pathname } = location;
  const [collapsed, setCollapsed] = useState(true);
  const {
    token: { colorBgContainer, borderRadiusLG }
  } = theme.useToken();

  return (
    <Layout style={{ minHeight: '100vh' }} hasSider>
      <Sider
        style={{ padding: 0, background: colorBgContainer }}
        trigger={null}
        collapsible
        breakpoint="lg"
        className="hideOnMobile"
        collapsed={collapsed}
      >
        <Menu
          mode="inline"
          style={{ padding: 0, background: colorBgContainer, height: '100%' }}
          defaultSelectedKeys={['/']}
          selectedKeys={[pathname]}
          items={[
            {
              key: '/',
              icon: <UserOutlined />,
              label: <NavLink to="/">Tag Faces</NavLink>
            },
            {
              key: '/events',
              icon: <VideoCameraOutlined />,
              label: <NavLink to="/events">Events</NavLink>
            },
            {
              key: '/Integration',
              icon: <UploadOutlined />,
              label: <NavLink to="/integration">Integration</NavLink>
            }
          ]}
        />
      </Sider>
      <Layout>
        <Header style={{ padding: 0, background: colorBgContainer }}>
          <Flex>
            <Button
              type="text"
              className="hideOnMobile"
              icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              onClick={() => setCollapsed(!collapsed)}
              style={{
                fontSize: '16px',
                width: 64,
                height: 64
              }}
            />
            <Title className="pageTitle" level={2}>
              FacePlatform
            </Title>
          </Flex>
        </Header>
        <Content style={{ margin: '24px 16px 0', overflow: 'initial' }}>
          <div
            style={{
              padding: 24,
              textAlign: 'center',
              background: colorBgContainer,
              borderRadius: borderRadiusLG
            }}
          >
            <Outlet />
          </div>
        </Content>
        <Footer style={{ textAlign: 'center' }}>FacePlatform ©{new Date().getFullYear()} Created by nivg1992</Footer>
      </Layout>
    </Layout>
  );
}

export default App;
