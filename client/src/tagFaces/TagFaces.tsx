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

interface OptionType {
    value: string
}

type FilterFunc<OptionType> = (inputValue: string, option?: OptionType) => boolean;

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
        const relevantOptions = faces.map(face => ({value: face.name.startsWith('unknown') ? '' : face.name})).filter(item => item.value != '')
        setFacesOptions(relevantOptions)
    }, [faces])

    const onChange = (faceName: string, data: string) => {
        setFacesValue(prevInputValues => ({
            ...prevInputValues,
            [faceName]: data.toLowerCase().trim()
        }))
    };

    const renameFace = async (faceIndex: number) => {
        if(faces[faceIndex].name.toLowerCase() == facesValue[faces[faceIndex].name].toLowerCase() || facesValue[faces[faceIndex].name] == '') {
            return;
        }
        const response = await axios.post(`${getBaseURL()}/faces/rename`, {source_face: faces[faceIndex].name.toLowerCase(),dest_face: facesValue[faces[faceIndex].name].toLowerCase()});
        if(response.data.action === "merge") {
            setFaces(faces.filter((_face, index) => index !== faceIndex))
        } else {
            setFaces(faces.map((face, index) => index === faceIndex ? { ...face,  name: facesValue[face.name]} : face))
        }
        const cloneFacesValue = {...facesValue};
        delete cloneFacesValue[faces[faceIndex].name];
        setFacesValue(cloneFacesValue);
    }

    const onDelete = async (faceIndex: number) => {
        await axios.delete(`${getBaseURL()}/faces/${faces[faceIndex].name}`);
        setFaces([...faces.slice(0, faceIndex), ...faces.slice(faceIndex + 1)]);
    }


    const onClickFaceGallery = (faceName: string) => {
        setFaceForGallery(faceName)
    }   

    const filterOption: FilterFunc<OptionType> = (inputValue: string, option?: OptionType) => {
        return option ? option.value.includes(inputValue) : true
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
                                //options={options && options?.length > 0 ? options : facesOptions}
                                options={facesOptions}
                                style={{ width: 100, marginTop: "1rem" }}
                                filterOption={filterOption}
                                // onSearch={(text) => setOptions(searchOnOptions(text))}
                                // onFocus={() => setOptions(searchOnOptions(''))}
                                onBlur={() => renameFace(index)}
                                onChange={(data) => onChange(face.name, data)}
                                value={facesValue[face.name] !== undefined ? facesValue[face.name] : (face.name.startsWith('unknown') ? '' : face.name)}
                            />
                            <DeleteOutlined onClick={() => onDelete(index)} className='face-delete' />
                        </Flex>
                    </Col>
                );
            })}
        </Row>
    )}

export default TagFaces
