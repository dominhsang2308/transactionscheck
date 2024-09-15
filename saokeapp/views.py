import pandas as pd
from django.core.paginator import Paginator
from django.shortcuts import render

def saokeapp(request):
    csv_file_path = 'transactions.csv'
    df = pd.read_csv(csv_file_path)

    query = request.GET.get('q','')
    

    csv_data = df.to_dict(orient='records')
    if query:
        csv_data = [row for row in csv_data if any(query.lower() in str(value).lower() for value in row.values())]
    paginator = Paginator(csv_data,10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'colums': df.columns,
        'query': query
    }
    return render(request, 'index.html', context)
