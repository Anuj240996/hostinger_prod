
from io import BytesIO
import barcode
import qrcode
from barcode.writer import ImageWriter
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.encoding import smart_str
from django.views import static

from dashboard.models import staff_Notification
from detect_barcodes.models import BarcodeImage
from django.template.defaultfilters import safe

import re
import barcode
import qrcode
from barcode.writer import ImageWriter
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.encoding import smart_str
from detect_barcodes.models import BarcodeImage



#from barcode import Code39
from barcode.writer import ImageWriter
from io import BytesIO
from io import BytesIO
import barcode
import qrcode
from barcode.writer import ImageWriter
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.encoding import smart_str
from detect_barcodes.models import BarcodeImage

from django.shortcuts import render
from django.http import HttpResponse
from django.utils.encoding import smart_str
from io import BytesIO
import barcode
from barcode.writer import ImageWriter
import qrcode

from django.shortcuts import render
from django.http import HttpResponse
from django.utils.encoding import smart_str
from io import BytesIO
import barcode
from barcode.writer import ImageWriter
import qrcode

from django.shortcuts import render
from django.http import HttpResponse
from django.utils.encoding import smart_str
from io import BytesIO
import barcode
from barcode.writer import ImageWriter
import qrcode

from django.shortcuts import render
from django.http import HttpResponse
from django.utils.encoding import smart_str
from io import BytesIO
import barcode
from barcode.writer import ImageWriter
import qrcode
import os
from django.conf import settings

import os
import itertools
from django.shortcuts import render
from detect_barcodes.models import BarcodeImage
import qrcode
#import barcodefrom inventoryproject import settings
from barcode.writer import ImageWriter
from io import BytesIO
import os
from django.core.files.base import ContentFile

@login_required(login_url='user-login')
def generate_file(barcode_file):
    output = HttpResponse(content_type="image/jpeg")
    barcode_file.seek(0)  # Reset the file pointer
    output.write(barcode_file.read())  # Read the file-like object and write its contents to the HttpResponse
    output['Content-Disposition'] = 'attachment; filename=%s' % smart_str('barcode.jpg')
    return output



import os
from django.core.files import File
from django.core.files.uploadedfile import InMemoryUploadedFile

import os
from django.core.files import File
from django.core.files.uploadedfile import InMemoryUploadedFile

import os
from django.core.files import File
from django.core.files.uploadedfile import InMemoryUploadedFile

import os
from django.core.files import File
from django.core.files.uploadedfile import InMemoryUploadedFile

import os
from django.core.files import File


from django.core.files.base import ContentFile

from django.core.files.base import ContentFile
import os
from django.core.files import File
from django.core.files.uploadedfile import InMemoryUploadedFile


import os
from io import BytesIO
import qrcode
import barcode
from barcode.writer import ImageWriter
from django.shortcuts import render

@login_required(login_url='user-login')
def generate(request):
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    companies = BarcodeImage.objects.order_by().values_list('company', flat=True).distinct()
    selected_company = request.POST.get('company')

    if selected_company:
        barcode_images = BarcodeImage.objects.filter(company=selected_company)
        barcodes = []

        # Count the occurrences of each barcode type
        barcode_type_counts = {}

        for barcode_image in barcode_images:
            b_data = barcode_image.barcode_data
            b_type = barcode_image.barcode_type or 'CODE128'  # Default barcode type if barcode_type is null

            if not barcode_image.barcode_path:  # Check if barcode_path is null
                if b_type not in barcode_type_counts:
                    barcode_type_counts[b_type] = 1
                else:
                    barcode_type_counts[b_type] += 1

                # Generate the image name with the barcode type and sequential number
                image_filename = f"{b_type}_{barcode_type_counts[b_type]}.png"
                existing_images = BarcodeImage.objects.filter(barcode_type=b_type, barcode_path__contains=image_filename)

                # Check if a file with the same name already exists
                while existing_images.exists():
                    barcode_type_counts[b_type] += 1
                    image_filename = f"{b_type}_{barcode_type_counts[b_type]}.png"
                    existing_images = BarcodeImage.objects.filter(barcode_type=b_type, barcode_path__contains=image_filename)

                if b_type == 'QRCODE':
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=1,
                    )
                    qr.add_data(b_data)
                    qr.make(fit=True)
                    qr_file = qr.make_image(fill_color="black", back_color="white")  # Render QR code image

                    with BytesIO() as qr_bytes:
                        qr_file.save(qr_bytes, format='PNG')  # Save the QR code image to a BytesIO object
                        qr_bytes.seek(0)  # Reset the file pointer

                        barcode_image.barcode_path.save(image_filename, qr_bytes, save=True)  # Save the image to the model

                else:
                    bar = barcode.get_barcode(name=b_type, code=b_data, writer=ImageWriter())
                    barcode_file = bar.render()  # Create a PIL class image object

                    with BytesIO() as barcode_bytes:
                        barcode_file.save(barcode_bytes, format='PNG')  # Save the barcode image to a BytesIO object
                        barcode_bytes.seek(0)  # Reset the file pointer

                        barcode_image.barcode_path.save(image_filename, barcode_bytes, save=True)  # Save the image to the model

                # Generate and save the barcode image path
                relative_image_path = os.path.join('static/barcode_images', image_filename)
                barcode_image.barcode_path = relative_image_path
                barcode_image.save()

            # Check if the 'image' attribute exists and has a file associated with it
            if barcode_image.image:
                image_url = barcode_image.image.url
            else:
                image_url = None

            # Add barcode data, barcode type, and barcode image URL to the list
            barcodes.append((b_data, b_type, image_url, barcode_image.barcode_path.url))

        return render(request, 'generate_barcodes/generate.html', {
            'companies': companies,
            'selected_company': selected_company,
            'barcode_images': barcode_images,
            'barcodes': barcodes,
            'count1':count1,
            'notification1':notification1,
        })

    else:
        return render(request, 'generate_barcodes/generate.html', {
            'companies': companies,
            'count1': count1,
            'notification1': notification1,
            'selected_company': None
        })

