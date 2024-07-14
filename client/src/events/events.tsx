import React, {useEffect, useState} from 'react';
import {getBaseURL} from '../common/url';
import { Avatar, List, Space, Flex, Typography, Image} from 'antd';
import { VideoCameraOutlined, FieldTimeOutlined, FrownOutlined, UserOutlined } from '@ant-design/icons';
import axios from 'axios';

const { Text } = Typography;

interface IFace {
    id: number,
    name: string,
    confidence: number,
    path: string
}

interface IEvent {
    id: number,
    camera: string,
    created: string,
    done: string,
    faces: IFace[]
}

function capitalizeFirstLetter(string: string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

function timeDifference(date1: Date, date2: Date) {
    const diffInSeconds = Math.floor((date2.getTime() - date1.getTime()) / 1000);
    const diffInMinutes = Math.floor(diffInSeconds / 60);
    const diffInHours = Math.floor(diffInMinutes / 60);
    const diffInDays = Math.floor(diffInHours / 24);

    if (diffInSeconds < 60) {
        return `${diffInSeconds}s`;
    } else if (diffInMinutes < 60) {
        return `${diffInMinutes}m`;
    } else if (diffInHours < 24) {
        return `${diffInHours}h`;
    } else {
        return `${diffInDays}d`;
    }
}

const Events: React.FC = () => {
    const [events, setEvents] = useState<IEvent[]>([])
    useEffect(() => {
        async function getFacesGallery() {
            const response = await axios.get(`${getBaseURL()}/events`)
            setEvents(response.data)
        }
        getFacesGallery()
    }, []);

    return (<List
        itemLayout="vertical"
        size="large"
        pagination={{
          pageSize: 3,
        }}
        dataSource={events}
        renderItem={(item) => (
          <List.Item
            key={item.id}
            extra={
              <Image
                width={272}
                alt="logo"
                src={`${getBaseURL()}/events/${item.id}/img`}
              />
            }
          >
            <Flex vertical>
                <Space direction="vertical" size="middle" style={{ display: 'flex' }}>
                    <Flex>
                        <Space align="center" style={{fontSize: '1.1em'}}>
                            <FieldTimeOutlined  />
                            <div>{new Date(item.created).toISOString()} - {timeDifference(new Date(item.created), new Date())} ago ({timeDifference(new Date(item.created), new Date(item.done))})</div>
                        </Space>
                    </Flex>
                    <Flex>
                        {item.faces.map((face) => <Avatar size={60} src={`${getBaseURL()}/faces/${face.name}/img`} />)}
                    </Flex>
                    <Flex>
                        <Flex vertical>
                            <Flex>
                                <Space align="center" style={{fontSize: '1.1em'}}>
                                    <UserOutlined />
                                    {<Text strong>{item.faces.map((face) => capitalizeFirstLetter(face.name)).join(', ')}</Text >}
                                </Space>
                            </Flex>
                            <Flex>
                                <Space align="center" style={{fontSize: '1.1em'}}>
                                    <VideoCameraOutlined />{item.camera}
                                </Space>
                            </Flex>
                            <Flex>
                                <Space align="center" style={{fontSize: '1.1em'}}>
                                    <FrownOutlined />
                                    <div>{item.faces[0].confidence * 100}%</div>
                                </Space>
                            </Flex>
                        </Flex>
                        <div style={{flexGrow: 1}}></div>
                    </Flex>
                </Space>
            </Flex>
            
          </List.Item>
        )}
      />);
}

export default Events