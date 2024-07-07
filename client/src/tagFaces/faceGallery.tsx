import React, {useEffect, useState} from 'react';
import axios from 'axios'
import {getBaseURL} from '../common/url';
import { Image, Col, Row, Breadcrumb, Flex } from 'antd';
import './faceGallery.css'
import { DeleteOutlined } from '@ant-design/icons';

const FaceGallery: React.FC<{faceName: string, onBack: () => void}> = ({faceName, onBack}) => {
    const [gallery, setGallery] = useState<string[]>([])
    useEffect(() => {
        async function getFacesGallery() {
            const response = await axios.get(`${getBaseURL()}/faces/${faceName}`)
            setGallery(response.data)
        }
        getFacesGallery()
    }, [faceName]);

    const onDeleteFaceImg = async (faceName: string, imgIndex: number) => {
        await axios.delete(`${getBaseURL()}/faces/${faceName}/${gallery[imgIndex]}`)
        setGallery([...gallery.slice(0, imgIndex), ...gallery.slice(imgIndex + 1)]);
    }

    return (
        <Flex vertical>
            <Breadcrumb className='gallery-breadcrumb' items={[
                {
                    title: 'TagFaces',                    
                    href: '',
                    onClick: (evt) => {
                        evt.preventDefault();
                        onBack()
                    }
                },
                {
                    title: faceName
                }
            ]}/>
            <Row gutter={{ xs: 8, sm: 16, md: 24, lg: 32 }}>
                {gallery.map((img, index) => {
                    const key = `col-${index}`;
                    return (
                        <Col
                        key={key}
                        >
                            <Image
                                className='gallery-img'
                                width={200}
                                src={`${getBaseURL()}/faces/${faceName}/${img}`}
                            />
                            <DeleteOutlined onClick={() => onDeleteFaceImg(faceName, index)} className='face-img-delete' />
                        </Col>
                    );
                })}
            </Row>
        </Flex>
    )
}

export default FaceGallery