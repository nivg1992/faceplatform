import os
import ssl
import asyncio
import json
import logging
import websockets
import requests
import threading
import warnings
from urllib3.exceptions import InsecureRequestWarning

# Disable only the InsecureRequestWarning
warnings.filterwarnings("ignore", category=InsecureRequestWarning)
from src.inputs.input import Input

class UnifiInput(Input):
    def __init__(self, go2rtc_server):
        self.go2rtc_server = go2rtc_server
        self.running = False
        self.headers = {}
        self.cameras = {}
        self.stop_event = threading.Event()
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
                logging.debug('[Unifi] Authenticated successfully')
            else:
                logging.error('[Unifi] Authentication failed')
                raise Exception('[Unifi] Authentication failed')
        except Exception as e:
            logging.error(f'[Unifi] Error authenticating: {e}')
            raise e

    def connect_to_websocket(self) -> None:
        ws_url = self.host.replace('https', 'wss') + '/proxy/protect/ws/updates'
        ssl_context = {};
        if self.skip_ssl_check:
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
        headers = [(key, value) for key, value in self.headers.items()]
        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_until_complete(self.send_receive_message(ws_url, ssl_context, headers))
            self.loop.close()
        except Exception as e:
            logging.error(f'[Unifi] Failed to initiate websocket connection: {e}')
            raise e

    async def send_receive_message(self, ws_url, ssl_context, headers) -> None:
        async with websockets.connect(ws_url, ssl=ssl_context, extra_headers=headers) as websocket:
            logging.info(f"[Unifi] Websocket created Successfully with image quality {self.image_quality}")
            while not self.stop_event.is_set():
                response = await websocket.recv()
                try:
                    self.on_message(response)
                except Exception as e:
                    logging.error(f'[Unifi]: {e}')


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
                    'name': camera['name'].replace(" ", ""),
                    'id': camera['id'],
                    'mac': camera['mac'],
                    'state': camera['state'],
                    'lastMotion': camera['lastMotion'],
                    'channels': channels
                }
        except Exception as e:
            logging.error(f'[Unifi] Failed to bootstrap: {e}')
            raise e

    def get_rtsp_link(self, rtsp_alias: str) -> str:
        """Generate an RTSP link for a camera."""
        return self.host.replace('https', 'rtspx') + f':7441/{rtsp_alias}'

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
            camera_name = self.get_camera_name(header)
            if not self.is_camera_excluded(camera_name):
                logging.debug(f'[Unifi] Smart motion start detected for name: {camera_name}')
                super().start_capture_topic(camera_name)
        elif payload and is_smart_detection == False:
            camera_name = self.get_camera_name(header)
            if not self.is_camera_excluded(camera_name):
                logging.debug(f'[Unifi] Smart motion stop detected for name: {camera_name}')
                super().stop_capture_topic(camera_name)

    def get_camera_name(self, header) -> str:
        return f"{self.cameras[header.get('id')].get('name')}_{self.image_quality}".lower()

    def is_camera_excluded(self, camera_name) -> bool:
        for excluded_camera in self.exclude_cameras:
            if excluded_camera in camera_name:
                return True
        return False

    def configure(self, config):
        self.host = "https://" + config.get("host", "")
        self.user = config.get("user")
        self.password = config.get("password")
        self.image_quality = config.get("image_quality", "LOW")
        self.skip_ssl_check = bool(config.get("skip_ssl_check", True))
        self.exclude_cameras = config.get("exclude_cameras", [])
        if not config.get("host") or not self.user or not self.password:
            raise Exception('[Unifi] host, user and password must be configured in config file!') 
        self.authenticate()
        self.get_bootstrap()


    def get_streams(self):
        streams = []
        for camera in self.cameras.values():
            for channel in camera['channels'].values():
                if(channel['enabled']):
                    streams.append({
                        'name': f"{camera['name']}_{channel['name']}".replace(' ', '').lower(),
                        'stream_url': self.get_rtsp_link(channel['rtspAlias'])
                    })
        return streams

    def capture(self, event_id, camera):
        return self.go2rtc_server.capture_image(event_id, camera)


    def listen(self):
        thread = threading.Thread(target=self.connect_to_websocket)
        thread.start()

    def stop(self):
        self.stop_event.set()