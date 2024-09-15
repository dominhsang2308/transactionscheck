import os
import pandas as pd
from django.core.paginator import Paginator
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.conf import settings

def saokeapp(request):
    # Kiểm tra nếu người dùng upload file CSV
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'csvs'))
        filename = fs.save(csv_file.name, csv_file)
        csv_file_path = fs.path(filename)

        print(f"File uploaded and saved at: {csv_file_path}")  # Kiểm tra đường dẫn
        # Lưu tên tệp vào session để sử dụng cho các yêu cầu sau
        request.session['csv_filename'] = filename
    else:
        # Kiểm tra nếu có tệp đã được lưu trong session
        if 'csv_filename' in request.session:
            filename = request.session['csv_filename']
            csv_file_path = os.path.join(settings.MEDIA_ROOT, 'csvs', filename)
            
            # Kiểm tra xem tệp có tồn tại hay không
            if not os.path.exists(csv_file_path):
                return render(request, 'index.html', {'error': 'Tệp CSV không tồn tại, vui lòng tải lại.'})
        else:
            return render(request, 'index.html', {'error': 'Chưa có tệp CSV nào được tải lên.'})

    # Đọc file CSV
    df = pd.read_csv(csv_file_path)

    query = request.GET.get('q', '')

    # Chuyển đổi dữ liệu CSV thành danh sách các dictionary
    csv_data = df.to_dict(orient='records')

    # Lọc dữ liệu nếu có từ khóa tìm kiếm
    if query:
        csv_data = [row for row in csv_data if any(query.lower() in str(value).lower() for value in row.values())]

    # Sử dụng Paginator để phân trang
    paginator = Paginator(csv_data, 10)  # Hiển thị 10 hàng mỗi trang
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'columns': df.columns,
        'query': query
    }

    return render(request, 'index.html', context)
