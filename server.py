#!/usr/bin/env python3
import os
import json
import aiohttp
from aiohttp import web
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CORS 中间件
@web.middleware
async def cors_middleware(request, handler):
    # 处理 OPTIONS 预检请求
    if request.method == 'OPTIONS':
        response = web.Response()
    else:
        response = await handler(request)
    
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-API-URL, X-API-Key, X-Server-ID'
    return response

def get_headers(request):
    api_key = request.headers.get('X-API-Key', '')
    return {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Accept-Encoding': 'gzip, deflate'
    }

def get_base_url(request):
    api_url = request.headers.get('X-API-URL', '').rstrip('/')
    server_id = request.headers.get('X-Server-ID', '')
    return f"{api_url}/{server_id}/files"

async def index(request):
    return web.FileResponse('./static/index.html')

async def list_files(request):
    api_url = request.headers.get('X-API-URL', '')
    server_id = request.headers.get('X-Server-ID', '')
    api_key = request.headers.get('X-API-Key', '')
    
    if not api_url or not server_id or not api_key:
        return web.json_response({'error': '请先配置 API 地址、Server ID 和 API Key'}, status=400)
    
    directory = request.query.get('directory', '/')
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{get_base_url(request)}/list"
            async with session.get(url, params={'directory': directory}, headers=get_headers(request), ssl=False) as resp:
                text = await resp.text()
                if resp.status == 200:
                    try:
                        data = json.loads(text)
                        return web.json_response(data)
                    except json.JSONDecodeError:
                        return web.json_response({'error': f'API 返回无效 JSON: {text[:200]}'}, status=500)
                else:
                    try:
                        err_data = json.loads(text)
                        err_msg = err_data.get('errors', [{}])[0].get('detail', text[:200])
                    except:
                        err_msg = text[:200]
                    return web.json_response({'error': f'API 错误 ({resp.status}): {err_msg}'}, status=resp.status)
    except Exception as e:
        logger.exception("list_files error")
        return web.json_response({'error': str(e)}, status=500)

async def get_file_contents(request):
    file_path = request.query.get('file', '')
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{get_base_url(request)}/contents"
            async with session.get(url, params={'file': file_path}, headers=get_headers(request), ssl=False) as resp:
                if resp.status == 200:
                    content = await resp.text()
                    # 处理各种可能的格式
                    try:
                        data = json.loads(content)
                        # 如果是 Buffer 格式 {"type":"Buffer","data":[...]}
                        if isinstance(data, dict) and data.get('type') == 'Buffer' and 'data' in data:
                            content = bytes(data['data']).decode('utf-8')
                        # 如果是纯字符串
                        elif isinstance(data, str):
                            content = data
                    except (json.JSONDecodeError, TypeError, ValueError):
                        pass
                    return web.Response(text=content, content_type='text/plain')
                else:
                    text = await resp.text()
                    try:
                        err_data = json.loads(text)
                        err_msg = err_data.get('errors', [{}])[0].get('detail', text[:200])
                    except:
                        err_msg = text[:200]
                    return web.json_response({'error': err_msg}, status=resp.status)
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)

async def write_file(request):
    file_path = request.query.get('file', '')
    content = await request.read()  # 读取原始字节
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{get_base_url(request)}/write"
            headers = get_headers(request)
            headers.pop('Content-Type', None)  # 移除 Content-Type
            async with session.post(url, params={'file': file_path}, data=content, headers=headers, ssl=False) as resp:
                if resp.status in [200, 204]:
                    return web.json_response({'status': 'ok'})
                else:
                    text = await resp.text()
                    return web.json_response({'error': text}, status=resp.status)
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)

async def delete_files(request):
    data = await request.json()
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{get_base_url(request)}/delete"
            async with session.post(url, json=data, headers=get_headers(request), ssl=False) as resp:
                if resp.status in [200, 204]:
                    return web.json_response({'status': 'ok'})
                else:
                    text = await resp.text()
                    return web.json_response({'error': text}, status=resp.status)
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)

async def rename_file(request):
    data = await request.json()
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{get_base_url(request)}/rename"
            async with session.put(url, json=data, headers=get_headers(request), ssl=False) as resp:
                if resp.status in [200, 204]:
                    return web.json_response({'status': 'ok'})
                else:
                    text = await resp.text()
                    return web.json_response({'error': text}, status=resp.status)
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)

async def create_folder(request):
    data = await request.json()
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{get_base_url(request)}/create-folder"
            async with session.post(url, json=data, headers=get_headers(request), ssl=False) as resp:
                if resp.status in [200, 204]:
                    return web.json_response({'status': 'ok'})
                else:
                    text = await resp.text()
                    return web.json_response({'error': text}, status=resp.status)
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)

async def download_file(request):
    file_path = request.query.get('file', '')
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{get_base_url(request)}/download"
            async with session.get(url, params={'file': file_path}, headers=get_headers(request), ssl=False) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return web.json_response(data)
                else:
                    text = await resp.text()
                    return web.json_response({'error': text}, status=resp.status)
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)

async def get_upload_url(request):
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{get_base_url(request)}/upload"
            async with session.get(url, headers=get_headers(request), ssl=False) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return web.json_response(data)
                else:
                    text = await resp.text()
                    return web.json_response({'error': text}, status=resp.status)
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)

async def proxy_upload(request):
    """代理上传文件到 Wings 服务器，避免 CORS 问题"""
    directory = request.query.get('directory', '/')
    try:
        # 先获取上传 URL
        async with aiohttp.ClientSession() as session:
            url = f"{get_base_url(request)}/upload"
            async with session.get(url, headers=get_headers(request), ssl=False) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    return web.json_response({'error': f'获取上传地址失败: {text}'}, status=resp.status)
                data = await resp.json()
                upload_url = data.get('attributes', {}).get('url', '')
                if not upload_url:
                    return web.json_response({'error': '无法获取上传地址'}, status=500)
        
        # 读取上传的文件
        reader = await request.multipart()
        
        async with aiohttp.ClientSession() as session:
            # 创建 FormData
            form = aiohttp.FormData()
            
            async for part in reader:
                if part.filename:
                    content = await part.read()
                    form.add_field('files', content, filename=part.filename, content_type=part.headers.get('Content-Type', 'application/octet-stream'))
            
            # 上传到 Wings
            full_url = f"{upload_url}&directory={directory}"
            async with session.post(full_url, data=form, ssl=False) as resp:
                if resp.status in [200, 204]:
                    return web.json_response({'status': 'ok'})
                else:
                    text = await resp.text()
                    return web.json_response({'error': f'上传失败: {text}'}, status=resp.status)
    except Exception as e:
        logger.exception("proxy_upload error")
        return web.json_response({'error': str(e)}, status=500)

async def compress_files(request):
    data = await request.json()
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{get_base_url(request)}/compress"
            async with session.post(url, json=data, headers=get_headers(request), ssl=False) as resp:
                if resp.status in [200, 204]:
                    result = await resp.json()
                    return web.json_response(result)
                else:
                    text = await resp.text()
                    return web.json_response({'error': text}, status=resp.status)
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)

async def decompress_file(request):
    data = await request.json()
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{get_base_url(request)}/decompress"
            async with session.post(url, json=data, headers=get_headers(request), ssl=False) as resp:
                if resp.status in [200, 204]:
                    return web.json_response({'status': 'ok'})
                else:
                    text = await resp.text()
                    return web.json_response({'error': text}, status=resp.status)
    except Exception as e:
        return web.json_response({'error': str(e)}, status=500)

app = web.Application(client_max_size=1024**3, middlewares=[cors_middleware])
app.router.add_get('/', index)
app.router.add_route('OPTIONS', '/api/files/{tail:.*}', lambda r: web.Response())  # CORS preflight
app.router.add_get('/api/files/list', list_files)
app.router.add_get('/api/files/contents', get_file_contents)
app.router.add_post('/api/files/write', write_file)
app.router.add_post('/api/files/delete', delete_files)
app.router.add_post('/api/files/rename', rename_file)
app.router.add_post('/api/files/create-folder', create_folder)
app.router.add_get('/api/files/download', download_file)
app.router.add_get('/api/files/upload', get_upload_url)
app.router.add_post('/api/files/upload', proxy_upload)
app.router.add_post('/api/files/compress', compress_files)
app.router.add_post('/api/files/decompress', decompress_file)
app.router.add_static('/static/', './static')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    logger.info(f"Starting server on port {port}")
    web.run_app(app, host='0.0.0.0', port=port)
