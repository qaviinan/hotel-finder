from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from embedchain.config import BaseLlmConfig
from .services import ec_app
from .utils import load_original, easy_variable_names
from .. import chat_config

@csrf_exempt
@require_http_methods(["POST"])
def chat_view(request):
    data = json.loads(request.body)
    query = data['query']
    
    if query == "firstcall":
        filtered_df = load_original()
        easy_filters = []
    else:
        config = BaseLlmConfig(stream=False, prompt=chat_config.HOTEL_QUERY_PROMPT)
        where_clause = {"index": {"$ne": 0}}
        response = ec_app.chat(query, citations=True, config=config, where=where_clause)
        
        df = load_original()
        local_vars = {'df': df}
        exec_string = "mydf=" + response[0]
        exec(exec_string, globals(), local_vars)
        easy_filters = easy_variable_names(response[0])
        filtered_df = local_vars['mydf']

    filter_df = filtered_df[['idStr', 'name', 'sectionedDescription/summary', 'url', 
                            'photos/0/thumbnailUrl', 'pricing/rate/amount', 'stars', 
                            'reviewDetailsInterface/reviewCount', 'Accuracy', 'Communication', 
                            'Cleanliness', 'Location', 'Check-in', 'Value']].rename(columns={
        "photos/0/thumbnailUrl": "image_url",
        "pricing/rate/amount": "price",
        "sectionedDescription/summary": "description",
        'reviewDetailsInterface/reviewCount': "review_count",
        'Check-in': "checkIn"
    })
    
    filter_df.index.name = "index"
    response_data = {
        "filters": easy_filters,
        "listings": filter_df.fillna("").to_dict('records')
    }
    
    return JsonResponse(response_data, json_dumps_params={'ensure_ascii': False})
