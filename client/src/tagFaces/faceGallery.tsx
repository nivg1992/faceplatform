import React, { useCallback, useState } from 'react';
import { Image, Col, Row, Breadcrumb, Flex } from 'antd';
import { DeleteOutlined } from '@ant-design/icons';

import { getBaseURL } from '../common/url';
import './faceGallery.css';
import useDeleteFaceImage from '../api/mutations/useDeleteFaceImage.ts';
import useGetFacesGallery from '../api/queries/useGetFacesGallery.ts';

interface FaceItemProps {
  faceName: string;
  img: string;
  index: number;
  setGallery: React.Dispatch<React.SetStateAction<string[]>>;
  gallery: string[];
}

const FaceItem: React.FC<FaceItemProps> = ({ faceName, img, index, setGallery, gallery }) => {
  const onSuccess = useCallback(() => {
    setGallery(prevGallery => [...prevGallery.slice(0, index), ...prevGallery.slice(index + 1)]);
  }, [index, setGallery]);

  const { mutate } = useDeleteFaceImage({ onSuccess });
  const onDelete = () => mutate({ faceName, imageId: gallery[index] });

  return (
    <Col>
      <Image className="gallery-img" width={200} src={`${getBaseURL()}/faces/${faceName}/${img}`} />
      <DeleteOutlined onClick={onDelete} className="face-img-delete" />
    </Col>
  );
};

interface FaceGalleryProps {
  faceName: string;
  onBack: () => void;
}

const FaceGallery: React.FC<FaceGalleryProps> = ({ faceName, onBack }) => {
  const [gallery, setGallery] = useState<string[]>([]);

  const onSuccess = useCallback((data: string[]) => setGallery(data), []);
  useGetFacesGallery(faceName, onSuccess);

  return (
    <Flex vertical>
      <Breadcrumb
        className="gallery-breadcrumb"
        items={[
          {
            title: 'TagFaces',
            href: '',
            onClick: evt => {
              evt.preventDefault();
              onBack();
            }
          },
          {
            title: faceName
          }
        ]}
      />
      <Row gutter={{ xs: 8, sm: 16, md: 24, lg: 32 }}>
        {gallery.map((img, index) => (
          <FaceItem
            key={`col-${index}`}
            index={index}
            faceName={faceName}
            gallery={gallery}
            setGallery={setGallery}
            img={img}
          />
        ))}
      </Row>
    </Flex>
  );
};

export default FaceGallery;
