import React, {useEffect, useState} from 'react';
import axios from 'axios'
import { Col, Row } from 'antd';
import {getBaseURL} from '../common/url';
import { Avatar, Flex, AutoComplete } from "antd";
import { DeleteOutlined, UserOutlined } from '@ant-design/icons';
import FaceGallery from './faceGallery';
import './TagFaces.css'

interface IFace {
    name: string;
    path: string;
  }
  

const TagFaces: React.FC = () => {
    const [facesOptions, setFacesOptions] = useState<{ value: string }[]>([])
    const [facesValue, setFacesValue] = useState<{[key: string]: string}>({})
    const [faces, setFaces] = useState<IFace[]>([]);
    const [faceForGallery, setFaceForGallery] = useState<string>()

    useEffect(() => {
        async function getFaces() {
            const response = await axios.get(`${getBaseURL()}/faces`)
            setFaces(response.data)
        }
        getFaces()
    }, []);

    useEffect(() => {
        setFacesOptions(faces.map(face => ({value: face.name.startsWith('unknown') ? '' : face.name})).filter(item => item.value != ''))
    }, [faces])

    const onChange = (faceName: string, data: string) => {
        setFacesValue(prevInputValues => ({
            ...prevInputValues,
            [faceName]: data
        }))
    };

    const renameFace = async (faceIndex: number) => {
        await axios.post(`${getBaseURL()}/faces/rename`, {source_face: faces[faceIndex].name,dest_face: facesValue[faces[faceIndex].name]});
        const cloneFacesValue = {...facesValue};
        delete cloneFacesValue[faces[faceIndex].name];
        setFaces(faces.map((face, index) => index === faceIndex ? { ...face,  name: facesValue[face.name]} : face))
        setFacesValue(cloneFacesValue);
        
    }

    const onDelete = async (faceIndex: number) => {
        await axios.delete(`${getBaseURL()}/faces/${faces[faceIndex].name}`);
        setFaces([...faces.slice(0, faceIndex), ...faces.slice(faceIndex + 1)]);
    }

    const onSelect = (data: string) => {
        console.log('onSelect', data);
    };

    const onClickFaceGallery = (faceName: string) => {
        setFaceForGallery(faceName)
    }

    if(faceForGallery) {
        return <FaceGallery onBack={() => setFaceForGallery(undefined)} faceName={faceForGallery}/>
    }

    return (
        <Row gutter={{ xs: 8, sm: 16, md: 24, lg: 32 }}>
            {faces.map((face, index) => {
                const key = `col-${index}`;
                return (
                    <Col
                    key={key}
                    >
                        <Flex className='face-flex' vertical>
                            <Avatar onClick={() => onClickFaceGallery(face.name)} className='face-img' src={`${getBaseURL()}/faces/${face.name}/${face.path}`} size={100} icon={<UserOutlined />} />
                            <AutoComplete
                                options={facesOptions}
                                style={{ width: 100, marginTop: "1rem" }}
                                onSelect={onSelect}
                                onBlur={() => renameFace(index)}
                                onChange={(data) => onChange(face.name, data)}
                                value={facesValue[face.name] || (face.name.startsWith('unknown') ? '' : face.name)}
                            />
                            <DeleteOutlined onClick={() => onDelete(index)} className='face-delete' />
                        </Flex>
                    </Col>
                );
            })}
        </Row>
    )}

export default TagFaces
