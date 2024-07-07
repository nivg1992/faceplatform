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
- [go2rtc server](https://github.com/AlexxIT/go2rtc?tab=readme-ov-file#go2rtc-docker) An easy way to get started is by pulling the Docker image and running it with a configuration like this: 
  ```
  streams:
     camera: rtsp://127.0.0.1/token
  ```
- [cmake](https://github.com/Kitware/CMake/releases) Download and install the relevant binary
- node22

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
      ports:
        - 5000:5000
      environment:
        - PF_DATA_FOLDER=/data
      volumes:
        - ./cameras.json:/app/cameras.json
        - ./data:/data
   ```

### Add new input
1. **Create input file:** add an input file at `src/inputs`
   
2. **Subclass Input:** Begin by subclassing the `Input` abstract class to define your custom input source. Implement the required methods for initialization, configuration, stream management, event handling, and data capture.
   
3. **Utilize Events Management:** Use the events_manager property inherited from Input to manage events and start/stop data capture from specific topics or cameras using `start_capture_topic` and `stop_capture_topic`.

4. **Add to input_manager:** After defining your input source, add it to the `input_manager` of FacePlatform using the `add_input` function. This step ensures that your input source is registered and can be accessed and controlled centrally within the application.

5. **Testing and Integration:** Test your input source thoroughly to ensure compatibility and seamless integration with FacePlatform’s existing components. Refer to provided examples and documentation for assistance.

## License
This project is licensed under the Apache License - see the [LICENSE](LICENSE) file for details.