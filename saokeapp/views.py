import os
import pandas as pd
from django.core.paginator import Paginator
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.conf import settings

def saokeapp(request):
    
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'csvs'))
        filename = fs.save(csv_file.name, csv_file)
        csv_file_path = fs.path(filename)

        print(f"File uploaded and saved at: {csv_file_path}")  
        request.session['csv_filename'] = filename
    else:
        
        if 'csv_filename' in request.session:
            filename = request.session['csv_filename']
            csv_file_path = os.path.join(settings.MEDIA_ROOT, 'csvs', filename)
            
            
            if not os.path.exists(csv_file_path):
                return render(request, 'index.html', {'error': 'Tệp CSV không tồn tại, vui lòng tải lại.'})
        else:
            return render(request, 'index.html', {'error': 'Chưa có tệp CSV nào được tải lên.'})

    
    df = pd.read_csv(csv_file_path)

    query = request.GET.get('q', '')

    
    csv_data = df.to_dict(orient='records')

    
    if query:
        csv_data = [row for row in csv_data if any(query.lower() in str(value).lower() for value in row.values())]

    
    paginator = Paginator(csv_data, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'columns': df.columns,
        'query': query
    }

    return render(request, 'index.html', context)
