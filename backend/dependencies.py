from fastapi import Request

def get_arq_pool(request: Request):
    return request.app.state.arq_pool