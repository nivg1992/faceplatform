# FacePlatform

FacePlatform is a powerful tool designed to enhance your home security system by utilizing your home cameras. It captures snapshots, tags faces, and sends pictures along with identification information. With FacePlatform, you can keep track of who is coming and going in real-time.

## Features

- **Snapshot Capture**: Takes snapshots from your home cameras automatically.
- **Face Tagging**: Detects and tags faces in the snapshots.
- **Notification System**: Sends a picture of the face along with identification details.

## Getting Started

### Prerequisites

Ensure you have the following prerequisites before installing FacePlatform:

- Python 3.10+
- go2rtc server
- cmake

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/faceplatform.git
   cd faceplatform
   ```
2. Install the required dependencies:
   
   ```bash
   poetry install
   ```
3. Configure your camera settings and identification details in `cameras.json`
   ```json
   [
      {
        "type": "mqtt_trigger",
        "mqtt_host": "127.0.0.1",
        "mqtt_port": 1883,
        "mqtt_user": "user",
        "mqtt_password": "password",
        "cameras": [
            {
                "name": "camera1",
                "topic": "camera_topic",
                "stream_protocol": "rtsp",
                "stream_url": "rtsp://127.0.0.1/aa"
            }
        ]
      }
   ]
   ```

### Build with Docker
  ```bash
  docker build . -t faceplatform
  ```

### Running the Application
   ```bash
   python -m "src.main"
   ```

### Docker Compose
   ```yaml
   services:
    faceplatform:
        image: nivg1992/faceplatform
        environment:
        - PF_DATA_FOLDER=/data
        volumes:
        - ./cameras.json:/app/cameras.json
        - ./data:/data
   ```

## License
This project is licensed under the Apache License - see the [LICENSE](LICENSE) file for details.