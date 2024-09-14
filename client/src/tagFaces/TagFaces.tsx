import React, { useCallback, useEffect, useState } from 'react';
import { Col, Row } from 'antd';
import { Avatar, Flex, AutoComplete } from 'antd';
import { DeleteOutlined, UserOutlined } from '@ant-design/icons';

import { getBaseURL } from '../common/url';
import FaceGallery from './faceGallery';
import useGetFaces from '../api/queries/useGetFaces.ts';
import './TagFaces.css';
import useRenameFace from '../api/mutations/useRenameFace.ts';
import useFaceDelete from '../api/mutations/useFaceDelete.ts';

export interface IFace {
  name: string;
  path: string;
}

interface OptionType {
  value: string;
}

type FilterFunc = (inputValue: string, option?: OptionType) => boolean;

const FaceItem: React.FC<{
  index: number;
  setFaceForGallery: (faceName: string) => void;
  face: IFace;
  facesOptions: OptionType[];
  filterOption: FilterFunc;
  setFaces: React.Dispatch<React.SetStateAction<IFace[]>>;
  faces: IFace[];
  setFacesValue: React.Dispatch<React.SetStateAction<{ [key: string]: string }>>;
  facesValue: { [key: string]: string };
}> = ({ index, setFaceForGallery, face, facesOptions, filterOption, setFaces, faces, setFacesValue, facesValue }) => {
  const onRenamingSuccess = useCallback(
    (data: { action: string }) => {
      if (data.action === 'merge') {
        setFaces(faces.filter((_face, idx) => idx !== index));
      } else {
        setFaces(faces.map((face, idx) => (idx === index ? { ...face, name: facesValue[face.name] } : face)));
      }
      const cloneFacesValue = { ...facesValue };
      delete cloneFacesValue[faces[index].name];
      setFacesValue(cloneFacesValue);
    },
    [faces, facesValue, index, setFaces, setFacesValue]
  );

  const { mutate: mutateRenaming } = useRenameFace(onRenamingSuccess);

  const renameFace = async () => {
    if (
      faces[index].name.toLowerCase() === facesValue[faces[index].name].toLowerCase() ||
      facesValue[faces[index].name] === ''
    ) {
      return;
    }

    mutateRenaming({
      source_face: faces[index].name.toLowerCase(),
      dest_face: facesValue[faces[index].name].toLowerCase()
    });
  };

  const onDeleteFaceSuccess = useCallback(
    () => setFaces([...faces.slice(0, index), ...faces.slice(index + 1)]),
    [faces, index, setFaces]
  );
  const { mutate: deleteFaceMutation } = useFaceDelete(onDeleteFaceSuccess);
  const onDelete = async () => {
    deleteFaceMutation(faces[index].name);
  };

  const onClickFaceGallery = (faceName: string) => {
    setFaceForGallery(faceName);
  };

  const onChange = (faceName: string, data: string) => {
    setFacesValue(prevInputValues => ({
      ...prevInputValues,
      [faceName]: data.toLowerCase().trim()
    }));
  };

  return (
    <Col>
      <Flex className="face-flex" vertical>
        <Avatar
          onClick={() => onClickFaceGallery(face.name)}
          className="face-img"
          src={`${getBaseURL()}/faces/${face.name}/${face.path}`}
          size={100}
          icon={<UserOutlined />}
        />
        <AutoComplete
          options={facesOptions}
          style={{ width: 100, marginTop: '1rem' }}
          filterOption={filterOption}
          onBlur={renameFace}
          onChange={data => onChange(face.name, data)}
          value={
            facesValue[face.name] !== undefined
              ? facesValue[face.name]
              : face.name.startsWith('unknown')
                ? ''
                : face.name
          }
        />
        <DeleteOutlined onClick={onDelete} className="face-delete" />
      </Flex>
    </Col>
  );
};

const TagFaces: React.FC = () => {
  const [facesOptions, setFacesOptions] = useState<OptionType[]>([]);
  const [facesValue, setFacesValue] = useState<{ [key: string]: string }>({});
  const [faces, setFaces] = useState<IFace[]>([]);
  const [faceForGallery, setFaceForGallery] = useState<string | undefined>(); // Updated setFaceForGallery type

  const onGetFacesSuccess = useCallback((data: IFace[]) => setFaces(data), []);
  useGetFaces(onGetFacesSuccess);

  useEffect(() => {
    const relevantOptions = faces
      .map(face => ({ value: face.name.startsWith('unknown') ? '' : face.name }))
      .filter(item => item.value !== '');
    setFacesOptions(relevantOptions);
  }, [faces]);

  const filterOption: FilterFunc = (inputValue: string, option?: OptionType) => {
    return option ? option.value.includes(inputValue) : true;
  };

  if (faceForGallery) {
    return <FaceGallery onBack={() => setFaceForGallery(undefined)} faceName={faceForGallery} />;
  }

  return (
    <Row gutter={{ xs: 8, sm: 16, md: 24, lg: 32 }}>
      {faces.map((face, index) => (
        <FaceItem
          key={`col-${index}`}
          face={face}
          facesOptions={facesOptions}
          index={index}
          filterOption={filterOption}
          setFaces={setFaces}
          faces={faces}
          setFacesValue={setFacesValue}
          facesValue={facesValue}
          setFaceForGallery={setFaceForGallery}
        />
      ))}
    </Row>
  );
};

export default TagFaces;
