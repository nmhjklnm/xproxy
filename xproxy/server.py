import asyncio
import logging
import httpx
from xproxy.manager import DuoMiProxyManager

# Initialize logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class DynamicProxyServer:
    def __init__(self, port: int, proxy_manager: DuoMiProxyManager):
        print("Initializing DynamicProxyServer")
        self.port = port
        self.proxy_manager = proxy_manager

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        print("Handling client")
        try:
            request_line = await reader.readline()
            method, path, protocol = request_line.decode('utf-8').strip().split()
            headers = await self.parse_http_headers(reader)

            body = await reader.read()
            if method.upper() == 'CONNECT':
                await self.handle_connect_method(writer, path)
            else: 
                response = await self.proxy_request(method, path, headers, body)
                await self.send_http_response(writer, response)
        except Exception as e:
            logging.error(f"Error handling client: {e}")
        finally:
            writer.close()
            await writer.wait_closed()

    async def parse_http_headers(self, reader: asyncio.StreamReader) -> dict:
        print("Parsing HTTP headers")
        headers = {}
        while True:
            line = await reader.readline()
            if line in (b'\r\n', b''):
                break
            name, value = line.decode('utf-8').strip().split(': ', 1)
            headers[name.lower()] = value
        print(headers)
        return headers

    async def handle_connect_method(self, writer: asyncio.StreamWriter, path: str):
        print("Handling CONNECT method")
        # Handle CONNECT method for HTTPS tunneling
        response_line = "HTTP/1.1 200 Connection Established\r\n\r\n"
        writer.write(response_line.encode())
        await writer.drain()

    async def proxy_request(self, method: str, path: str, headers: dict, body: bytes) -> httpx.Response:
        print("Proxying request")
        proxy = self.proxy_manager.get_random_proxy()
        proxy_url = proxy.formatted

        # Construct the full URL for the request
        if path.startswith("http://") or path.startswith("https://"):
            target_url = path
        else:
            target_url = f"http://{headers['host']}{path}"

        print(f"Proxying request to {target_url} via {proxy_url}")

        async with httpx.AsyncClient(proxies={"http://": proxy_url, "https://": proxy_url}) as client:
            response = await client.request(method, target_url, headers=headers, content=body)
            return response

    async def send_http_response(self, writer: asyncio.StreamWriter, response: httpx.Response):
        print("Sending HTTP response")
        status_line = f'HTTP/1.1 {response.status_code} {response.reason_phrase}\r\n'
        writer.write(status_line.encode())
        for key, value in response.headers.items():
            writer.write(f'{key}: {value}\r\n'.encode())
        writer.write(b'\r\n')
        writer.write(response.content)
        await writer.drain()

    async def run_server(self):
        print("Running server")
        server = await asyncio.start_server(self.handle_client, '127.0.0.1', self.port)
        async with server:
            await server.serve_forever()

async def main():
    print("Starting main function")
    port = 6123
    proxy_manager = DuoMiProxyManager(max_use_count=4, min_valid_proxies=10, proxy_expiry_seconds=60)
    server = DynamicProxyServer(port, proxy_manager)
    await server.run_server()

if __name__ == '__main__':
    try:
        print("Starting server")
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
