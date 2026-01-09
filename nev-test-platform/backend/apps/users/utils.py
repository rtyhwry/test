"""Utility functions for users app."""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """Custom exception handler for API responses."""
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response_data = {
            'success': False,
            'message': '',
            'errors': None
        }
        
        if isinstance(response.data, dict):
            if 'detail' in response.data:
                custom_response_data['message'] = response.data['detail']
            else:
                custom_response_data['errors'] = response.data
                custom_response_data['message'] = '请求参数错误'
        elif isinstance(response.data, list):
            custom_response_data['message'] = response.data[0] if response.data else '未知错误'
        else:
            custom_response_data['message'] = str(response.data)
        
        response.data = custom_response_data
    
    return response
