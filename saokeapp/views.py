import os
import pandas as pd
import pdfplumber
from django.core.paginator import Paginator
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.conf import settings

def saokeapp(request):
    file_type = None
    content = None

    
    if request.method == 'POST' and request.FILES.get('csv_file'):
        uploaded_file = request.FILES['csv_file']
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'uploads'))
        filename = fs.save(uploaded_file.name, uploaded_file)
        file_path = fs.path(filename)

       
        request.session['uploaded_filename'] = filename

        # Kiểm tra loại file dựa trên phần mở rộng
        if filename.endswith('.csv'):
            file_type = 'csv'
            df = pd.read_csv(file_path)
            
            content = df.to_dict(orient='records') 
            columns = df.columns
        elif filename.endswith('.pdf'):
            file_type = 'pdf'
            with pdfplumber.open(file_path) as pdf:
                content = [page.extract_text() for page in pdf.pages]  # Trích xuất văn bản từ mỗi trang PDF
                columns = ['PDF Content']  # Giả sử chỉ có một cột là nội dung PDF
        else:
            return render(request, 'index.html', {'error': 'Định dạng file không được hỗ trợ.'})
    else:
        
        if 'uploaded_filename' in request.session:
            filename = request.session['uploaded_filename']
            file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', filename)

            if not os.path.exists(file_path):
                return render(request, 'index.html', {'error': 'Tệp không tồn tại, vui lòng tải lên tệp mới.'})

            
            if filename.endswith('.csv'):
                file_type = 'csv'
                df = pd.read_csv(file_path)
               
                content = df.to_dict(orient='records')
                columns = df.columns
            elif filename.endswith('.pdf'):
                file_type = 'pdf'
                with pdfplumber.open(file_path) as pdf:
                    content = [page.extract_text() for page in pdf.pages]
                    columns = ['PDF Content']
        else:
            return render(request, 'index.html', {'error': 'Chưa có tệp nào được tải lên.'})

    query = request.GET.get('q', '')

    # Lọc dữ liệu cho file CSV
    if query and file_type == 'csv':
        content = [row for row in content if any(query.lower() in str(value).lower() for value in row.values())]

    # Sử dụng Paginator cho cả CSV và PDF
    paginator = Paginator(content, 10)  # Hiển thị 10 hàng hoặc trang mỗi trang
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'columns': columns,
        'query': query,
        'file_type': file_type
    }

    return render(request, 'index.html', context)
