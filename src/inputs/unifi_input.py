import ssl
import asyncio
import json
import logging
import websockets
import requests
from src.inputs.input import Input


class UnifiInput(Input):
    def __init__(self, go2rtc_server):
        self.go2trc_server = go2rtc_server
        self.running = False
        self.headers = {}
        self.cameras = {}
        super().__init__()

    def authenticate(self) -> None:
        """Authenticate to the Unifi server and store headers for future requests."""
        try:
            response = requests.post(f'{self.host}/api/auth/login', json={
                'username': self.user,
                'password': self.password
            }, verify=False)
            if response.status_code == 200:
                csrf_token = response.headers.get("X-Updated-CSRF-Token") or response.headers.get("X-CSRF-Token")
                cookie = response.headers.get("Set-Cookie").split(';')[0]
                self.headers = {
                    'Cookie': cookie,
                    'X-CSRF-Token': csrf_token
                }
                logging.debug('Authenticated successfully')
            else:
                logging.error('Authentication failed')
                raise Exception('Authentication failed')
        except Exception as e:
            logging.error(f'Error authenticating: {e}')
            raise e

    async def connect_to_websocket(self) -> None:
        ws_url = self.host.replace('https', 'wss') + '/proxy/protect/ws/updates'
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        headers = [(key, value) for key, value in self.headers.items()]
        try:
            async with websockets.connect(ws_url, ssl=ssl_context, extra_headers=headers) as websocket:
                while True and self.running:
                    logging.debug('Websocket created Successfully')
                    response = await websocket.recv()
                    self.on_message(response)
        except Exception as e:
            logging.error(f'Failed to initiate websocket connection: {e}')
            raise e

    def get_bootstrap(self) -> None:
        """Retrieve initial camera information from the server."""
        try:
            response = requests.get(f'{self.host}/proxy/protect/api/bootstrap', headers=self.headers, verify=False)
            data = response.json()
            self.cameras = {}
            for camera in data['cameras']:
                channels = {channel['name']: {
                    'id': channel['id'],
                    'name': channel['name'],
                    'enabled': channel['enabled'],
                    'rtspAlias': channel['rtspAlias']
                } for channel in camera['channels']}
                self.cameras[camera['id']] = {
                    'name': camera['name'],
                    'id': camera['id'],
                    'mac': camera['mac'],
                    'state': camera['state'],
                    'lastMotion': camera['lastMotion'],
                    'channels': channels
                }
        except Exception as e:
            logging.error(f'Failed to bootstrap: {e}')
            raise e

    def get_rtsp_link(self, rtsp_alias: str) -> str:
        """Generate an RTSP link for a camera."""
        return self.host.replace('https', 'rtsp') + f':7441/{rtsp_alias}?enableSrtp'

    @staticmethod
    def decode_packet(packet: bytes):
        """Decode a received WebSocket packet."""
        s = packet.decode('utf-8', errors='ignore')
        json_objects = []
        start_idx = 0
        while True:
            start = s.find('{', start_idx)
            if start == -1:
                break
            brace_count = 1
            end = start
            while brace_count > 0 and end < len(s) - 1:
                end += 1
                if s[end] == '{':
                    brace_count += 1
                elif s[end] == '}':
                    brace_count -= 1
            if brace_count == 0:
                json_str = s[start:end + 1]
                try:
                    json_obj = json.loads(json_str)
                    json_objects.append(json_obj)
                except json.JSONDecodeError:
                    pass
            start_idx = end + 1
        return {'header': json_objects[0], 'payload': json_objects[1]}

    def on_message(self, message) -> None:
        """Handle messages received from WebSocket."""
        decoded_message = self.decode_packet(message)
        header = decoded_message.get('header')
        payload = decoded_message.get('payload')
        is_smart_detection = payload.get('isSmartDetected')
        if payload and is_smart_detection:
            logging.info('Smart motion start detected')
            camera_name = self.cameras[header.get('id')].get('name')
            rtsp_link = self.get_rtsp_link(self.cameras[header.get('id')].get('channels').get('Low').get('rtspAlias'))
            logging.info(f'Smart motion start detected for name: {camera_name} use URL: {rtsp_link}')
        elif payload and is_smart_detection == False:
            camera_name = self.cameras[header.get('id')].get('name')
            logging.info(f'Smart motion stop detected for name: {camera_name}')

    def configure(self, config):
        self.host = config["host"]
        self.user = config["user"]
        self.password = config["password"]

    def get_streams(self):
        return self.cameras;

    def capture(self, event_id, camera):
        return self.go2rtc_server.capture_image(event_id, camera)


    def listen(self):
        print('unifi listen')
        self.authenticate()
        self.get_bootstrap()
        self.running = True
        asyncio.run(self.connect_to_websocket())

    def stop(self):
        self.running = False
