import { useState } from 'react'
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  UploadOutlined,
  UserOutlined,
  VideoCameraOutlined,
} from '@ant-design/icons';
import { Button, Layout, Menu, theme, Typography, Flex  } from 'antd';
import './App.css'
import TagFaces from './tagFaces/TagFaces'

const { Title } = Typography;
const { Header, Sider, Content, Footer } = Layout;

function App() {
  const [collapsed, setCollapsed] = useState(true);
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  return (
    <Layout style={{height:"100vh"}}>
      <Sider 
        trigger={null} 
        collapsible 
        style={{ padding: 0, background: colorBgContainer }}
        breakpoint="lg"
        className="hideOnMobile"
        collapsed={collapsed}>
        <Menu
          mode="inline"
          style={{ padding: 0, background: colorBgContainer, height: "100%" }}
          defaultSelectedKeys={['1']}
          items={[
            {
              key: '1',
              icon: <UserOutlined />,
              label: 'Tag Faces',
            },
            {
              key: '2',
              icon: <VideoCameraOutlined />,
              label: 'Events',
            },
            {
              key: '3',
              icon: <UploadOutlined />,
              label: 'Integration',
            },
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
                height: 64,
              }}
            />
            <Title className='pageTitle' level={2}>FacePlatform</Title>
          </Flex>
          
        </Header>
        <Content
          style={{
            margin: '24px 16px',
            padding: 24,
            minHeight: 280,
            background: colorBgContainer,
            borderRadius: borderRadiusLG,
          }}
        >
          <TagFaces />
        </Content>
        <Footer style={{ textAlign: 'center' }}>
          FacePlatform ©{new Date().getFullYear()} Created by nivg1992
        </Footer>
      </Layout>
    </Layout>
  );
}

export default App
