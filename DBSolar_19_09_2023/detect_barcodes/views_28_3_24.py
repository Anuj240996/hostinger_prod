

import time
from datetime import datetime
from urllib import response

import barcode
from django.contrib import messages
from django.contrib.auth.models import User
from reportlab.graphics.barcode.common import Barcode

from user.models import Profile


import cv2
import numpy as np
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import render
from PIL import Image
from pyzbar.pyzbar import decode

from PyPDF2 import PdfFileReader
from pyzbar.pyzbar import decode
from PIL import Image

from customer.models import Customer
import json
from django.http import HttpResponse, JsonResponse

from dashboard.models import staff_Notification
from .models import BarcodeImage, InverterImage
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
#from utils.camera_streaming_widget import CameraStreamingWidget
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
import base64
import cv2
import numpy as np
import pytz
from pyzbar import pyzbar
from .models import BarcodeImage
from .models import Customer
from django.contrib.auth.models import User  # Import the User model


import base64
import cv2
import numpy as np
from django.http import JsonResponse
from pyzbar import pyzbar
from django.utils import timezone
import pytz

import base64
import cv2
import numpy as np
from django.http import JsonResponse
from django.shortcuts import render
from pyzbar import pyzbar

from django.shortcuts import render
from django.http import JsonResponse
from .models import BarcodeImage
from django.utils import timezone
import base64
import cv2
import numpy as np
from pyzbar import pyzbar

from django.shortcuts import render
from django.http import JsonResponse
import cv2
from pyzbar import pyzbar
import base64



@login_required(login_url='user-login')

# Camera feed
def camera_feed(request):
    stream = CameraStreamingWidget()
    frames = stream.get_frames()

    # if ajax request is sent
    if request.is_ajax():
        print('Ajax request received')
        time_stamp = str(datetime.now().strftime("%d-%m-%y"))
        image = os.path.join(os.getcwd(), "media",
                             "images", f"img_{time_stamp}.png")
        if os.path.exists(image):
            # open image if exists
            im = Image.open(image)
            # decode barcode
            if decode(im):
                for barcode in decode(im):
                    barcode_data = (barcode.data).decode('utf-8')
                    file_saved_at = time.ctime(os.path.getmtime(image))
                    # return decoded barcode as json response
                    return JsonResponse(data={'barcode_data': barcode_data, 'file_saved_at': file_saved_at})
            else:
                return JsonResponse(data={'barcode_data': None})
        else:
            return JsonResponse(data={'barcode_data': None})
    # else stream the frames from camera feed
    else:
        return StreamingHttpResponse(frames, content_type='multipart/x-mixed-replace; boundary=frame')


# def detect(request):
#     stream = CameraStreamingWidget()
#     success, frame = stream.camera.read()
#     if success:
#         status = True
#     else:
#         status = False
#     return render(request, 'detect_barcodes/detect.html', context={'cam_status': status})


# def detect(request):
#     camera_value = os.environ.get('CAMERA')
#     if camera_value is not None:
#         camera = int(camera_value)
#     else:
#         camera = 0  # Assign a default camera value, such as 0 or another appropriate value
#
#     stream = CameraStreamingWidget(camera)
#     success, frame = stream.camera.read()
#     if success:
#         status = True
#     else:
#         status = False
#     return render(request, 'detect_barcodes/detect.html', context={'cam_status': status})


@login_required(login_url='user-login')
class CameraStreamingWidget:
    def __init__(self, camera):
        self.camera = cv2.VideoCapture(camera)

@login_required(login_url='user-login')
def detect(request):
    camera_value = os.environ.get('CAMERA')
    if camera_value is not None:
        try:
            camera = int(camera_value)
        except ValueError:
            # Handle the case when the camera value is not a valid integer
            # Assign a default camera value or take appropriate action
            camera = 0
    else:
        camera = 0  # Assign a default camera value, such as 0 or another appropriate value

    stream = CameraStreamingWidget(camera)
    success, frame = stream.camera.read()
    if success:
        status = True
    else:
        status = False
    return render(request, 'detect_barcodes/detect.html', context={'cam_status': status})


# def detect_barcode(request):
#     if request.method == 'POST':
#         image = request.FILES['image']
#         image_data = image.read()
#         image_base64 = base64.b64encode(image_data).decode('utf-8')
#
#         nparr = np.frombuffer(image_data, np.uint8)
#         img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#
#         barcodes = pyzbar.decode(img)
#         if barcodes:
#             barcode_data = barcodes[0].data.decode('utf-8')
#             # Process the barcode data as needed
#             # Save the image or perform any other operations
#
#             response = {
#                 'barcode_data': barcode_data,
#                 'file_saved_at': '2023-06-06 10:30:00'  # Replace with the actual timestamp of the saved image
#             }
#         else:
#             response = {
#                 'barcode_data': None,
#                 'file_saved_at': None
#             }
#
#         return JsonResponse(response)
#
#     return render(request, 'detect_barcodes/detect_barcodes.html')

# def detect_barcode(request):
#     if request.method == 'POST':
#         response = []
#         images = request.FILES.getlist('image')  # Retrieve multiple uploaded images
#
#         for image in images:
#             image_data = image.read()
#             image_base64 = base64.b64encode(image_data).decode('utf-8')
#
#             nparr = np.frombuffer(image_data, np.uint8)
#             img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#
#             barcodes = pyzbar.decode(img)
#             if barcodes:
#                 barcode_data = barcodes[0].data.decode('utf-8')
#                 # Process the barcode data as needed
#                 # Save the image or perform any other operations
#
#                 response.append({
#                     'barcode_data': barcode_data,
#                     'file_saved_at': '2023-06-06 10:30:00'  # Replace with the actual timestamp of the saved image
#                 })
#             else:
#                 response.append({
#                     'barcode_data': None,
#                     'file_saved_at': None
#                 })
#
#         return JsonResponse(response, safe=False)
#
#     return render(request, 'detect_barcodes/detect_barcodes.html')



# def detect_barcode(request):
#     if request.method == 'POST':
#         images = request.FILES.getlist('image')  # Get list of uploaded images
#
#         detected_barcodes = []
#
#         for image in images:
#             image_data = image.read()
#             image_base64 = base64.b64encode(image_data).decode('utf-8')
#
#             nparr = np.frombuffer(image_data, np.uint8)
#             img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#
#             barcodes = pyzbar.decode(img)
#             if barcodes:
#                 barcode_data = barcodes[0].data.decode('utf-8')
#                 # Process the barcode data as needed
#                 # Save the image or perform any other operations
#
#                 detected_barcodes.append({
#                     'barcode_data': barcode_data,
#                     'file_saved_at': '2023-06-06 10:30:00'  # Replace with the actual timestamp of the saved image
#                 })
#             else:
#                 detected_barcodes.append({
#                     'barcode_data': None,
#                     'file_saved_at': None
#                 })
#
#         return JsonResponse(detected_barcodes, safe=False)
#
#     return render(request, 'detect_barcodes/detect_barcodes.html')






# def detect_barcode(request):
#     if request.method == 'POST':
#         images = request.FILES.getlist('image')  # Get list of uploaded images
#
#         detected_barcodes = []
#
#         for image in images:
#             image_data = image.read()
#             image_base64 = base64.b64encode(image_data).decode('utf-8')
#
#             nparr = np.frombuffer(image_data, np.uint8)
#             img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#
#             barcodes = pyzbar.decode(img)
#             if barcodes:
#                 barcode_data = barcodes[0].data.decode('utf-8')
#                 # Process the barcode data as needed
#                 # Save the image or perform any other operations
#
#                 tz = pytz.timezone('Asia/Kolkata')  # Set the timezone to IST (Indian Standard Time)
#                 file_saved_at = timezone.now().astimezone(tz).strftime('%Y-%m-%d %H:%M:%S')
#
#                 detected_barcodes.append({
#                     'barcode_data': barcode_data,
#                     'file_saved_at': file_saved_at
#                 })
#             else:
#                 detected_barcodes.append({
#                     'barcode_data': None,
#                     'file_saved_at': None
#                 })
#
#         return JsonResponse(detected_barcodes, safe=False)
#
#     return render(request, 'detect_barcodes/detect_barcodes.html')


# def detect_barcode(request):
#     if request.method == 'POST':
#         images = request.FILES.getlist('image')  # Get list of uploaded images
#
#         detected_barcodes = []
#
#         for image in images:
#             image_data = image.read()
#             image_base64 = base64.b64encode(image_data).decode('utf-8')
#
#             nparr = np.frombuffer(image_data, np.uint8)
#             img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#
#             barcodes = pyzbar.decode(img)
#             if barcodes:
#                 barcode_data = barcodes[0].data.decode('utf-8')
#
#                 tz = pytz.timezone('Asia/Kolkata')  # Set the timezone to IST (Indian Standard Time)
#                 file_saved_at = timezone.now().astimezone(tz)
#
#                 barcode_image = BarcodeImage.objects.create(
#                     barcode_data=barcode_data,
#                     file_saved_at=file_saved_at,
#                     image=image
#                 )
#
#                 detected_barcodes.append({
#                     'barcode_data': barcode_data,
#                     'file_saved_at': file_saved_at.strftime('%Y-%m-%d %H:%M:%S'),
#                     'image_url': barcode_image.image.url
#                 })
#             else:
#                 detected_barcodes.append({
#                     'barcode_data': None,
#                     'file_saved_at': None,
#                     'image_url': None
#                 })
#
#         return JsonResponse(detected_barcodes, safe=False)
#
#     return render(request, 'detect_barcodes/detect_barcodes.html')






# import base64
# import cv2
# import numpy as np
# from django.shortcuts import render
# from django.http import JsonResponse
# from django.utils import timezone
# import pytz
# from pyzbar import pyzbar
# from .models import BarcodeImage
#
# def detect_barcode(request):
#     if request.method == 'POST':
#         images = request.FILES.getlist('image')  # Get list of uploaded images
#
#         detected_barcodes = []
#
#         for image in images:
#             image_data = image.read()
#             image_base64 = base64.b64encode(image_data).decode('utf-8')
#
#             nparr = np.frombuffer(image_data, np.uint8)
#             img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#
#             barcodes = pyzbar.decode(img)
#             if barcodes:
#                 for barcode in barcodes:
#                     barcode_data = barcode.data.decode('utf-8')
#                     barcode_type = barcode.type
#
#                     existing_barcode = BarcodeImage.objects.filter(barcode_data=barcode_data).first()
#
#                     if existing_barcode:
#                         detected_barcodes.append({
#                             'barcode_data': barcode_data,
#                             'barcode_type': barcode_type,
#                             'message': 'Barcode data already exists in the database.',
#                         })
#                     else:
#                         tz = pytz.timezone('Asia/Kolkata')  # Set the timezone to IST (Indian Standard Time)
#                         file_saved_at = timezone.now().astimezone(tz)
#
#                         barcode_image = BarcodeImage.objects.create(
#                             barcode_data=barcode_data,
#                             barcode_type=barcode_type,
#                             file_saved_at=file_saved_at,
#                             image=image
#                         )
#
#                         detected_barcodes.append({
#                             'barcode_data': barcode_data,
#                             'barcode_type': barcode_type,
#                             'file_saved_at': file_saved_at.strftime('%Y-%m-%d %H:%M:%S'),
#                             'image_url': barcode_image.image.url,
#                             'message': 'Barcode data saved successfully.',
#                         })
#             else:
#                 detected_barcodes.append({
#                     'barcode_data': None,
#                     'barcode_type': None,
#                     'message': 'No barcode detected in the image.',
#                 })
#
#         return JsonResponse(detected_barcodes, safe=False)
#
#     return render(request, 'detect_barcodes/detect_barcodes.html')



# def detect_barcode(request):
#
#     if request.method == 'POST':
#         images = request.FILES.getlist('image')  # Get list of uploaded images
#
#         detected_barcodes = []
#
#         for image in images:
#             company = request.POST.get('solarPlateCompany')  # Get the value of the company field
#             wattage = request.POST.get('wattage')  # Get the value of the wattage field
#             new_customer_id = request.POST.get('new_customer_id')
#             #assign_to_user = User.objects.get(id=new_customer)
#             company_name = request.POST.get('phone')
#             print(new_customer_id)
#             image_data = image.read()
#             image_base64 = base64.b64encode(image_data).decode('utf-8')
#
#             nparr = np.frombuffer(image_data, np.uint8)
#             img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#
#             barcodes = pyzbar.decode(img)
#             if barcodes:
#                 for barcode in barcodes:
#                     barcode_data = barcode.data.decode('utf-8')
#                     barcode_type = barcode.type
#
#                     existing_barcode = BarcodeImage.objects.filter(barcode_data=barcode_data).first()
#
#                     if existing_barcode:
#                         detected_barcodes.append({
#                             'barcode_data': barcode_data,
#                             'barcode_type': barcode_type,
#                             'message': 'Barcode data already exists in the database.',
#                         })
#                     else:
#                         tz = pytz.timezone('Asia/Kolkata')  # Set the timezone to IST (Indian Standard Time)
#                         file_saved_at = timezone.now().astimezone(tz)
#
#                         barcode_image = BarcodeImage.objects.create(
#                             barcode_data=barcode_data,
#                             barcode_type=barcode_type,
#                             company=company,  # Save the company value
#                             wattage=wattage,  # Save the wattage value
#                             file_saved_at=file_saved_at,
#                             image=image,
#                             AssignTo=new_customer_id,
#                             #AssignTo=assign_to_user,
#                             AssignBy=request.user.id,
#                             company_name=company_name,
#
#                         )
#
#                         detected_barcodes.append({
#                             'barcode_data': barcode_data,
#                             'barcode_type': barcode_type,
#                             'file_saved_at': file_saved_at.strftime('%Y-%m-%d %H:%M:%S'),
#                             'image_url': barcode_image.image.url,
#                             'message': 'Barcode data saved successfully.',
#                         })
#             else:
#                 detected_barcodes.append({
#                     'barcode_data': None,
#                     'barcode_type': None,
#                     'message': 'No barcode detected in the image.',
#                 })
#
#         return JsonResponse(detected_barcodes, safe=False)
#
#     # return render(request, 'detect_barcodes/detect_barcodes.html')
#
#     companies = Customer.objects.all()
#     return render(request, 'detect_barcodes/detect_barcodes.html', {'companies': companies})




#
# @login_required(login_url='user-login')
#
#
# def detect_barcode(request):
#     count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#     notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#     if request.method == 'POST':
#         barcode_option = request.POST.get('barcodeOption')  # Get the selected barcode option
#         print("Barcode Option:", barcode_option)
#
#         if barcode_option == 'uploadBarcode':
#             images = request.FILES.getlist('image')  # Get list of uploaded images
#             detected_barcodes = []
#             product_name = None
#
#             # Determine the product_name based on the template being used
#             if request.path == '/detect_barcodes/detect_barcodes/':
#                 product_name = 'SolarPanel'
#             elif request.path == '/detect_barcodes/detect_inverter/':
#                 product_name = 'Inverter'
#
#             for image in images:
#                 company = request.POST.get('solarPlateCompany')  # Get the value of the company field
#                 wattage = request.POST.get('wattage')  # Get the value of the wattage field
#                 new_customer_id = request.POST.get('new_customer_id')
#                 comp_name = request.POST.get('comp_name')  # Get the value of the dynamically changing textbox
#
#                 if comp_name:
#                     customer = Customer.objects.get(new_customer_id=comp_name)
#                     company_name = customer.Comp_name
#
#                 image_data = image.read()
#                 image_base64 = base64.b64encode(image_data).decode('utf-8')
#
#                 nparr = np.frombuffer(image_data, np.uint8)
#                 img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#
#                 barcodes = pyzbar.decode(img)
#                 if barcodes:
#                     for barcode in barcodes:
#                         barcode_data = barcode.data.decode('utf-8')
#                         barcode_type = barcode.type
#
#                         existing_barcode = BarcodeImage.objects.filter(barcode_data=barcode_data).first()
#
#                         if existing_barcode:
#                             detected_barcodes.append({
#                                 'barcode_data': barcode_data,
#                                 'barcode_type': barcode_type,
#                                 'message': 'Barcode data already exists in the database.',
#                             })
#                         else:
#                             tz = pytz.timezone('Asia/Kolkata')  # Set the timezone to IST (Indian Standard Time)
#                             file_saved_at = timezone.now().astimezone(tz)
#
#                             if new_customer_id.isdigit():
#                                 assign_to_user = User.objects.get(id=new_customer_id)
#                             else:
#                                 assign_to_user = None
#
#                             barcode_image = BarcodeImage.objects.create(
#                                 barcode_data=barcode_data,
#                                 barcode_type=barcode_type,
#                                 company=company_name,  # Save the company value
#                                 wattage=wattage,  # Save the wattage value
#                                 file_saved_at=file_saved_at,
#                                 image=image,
#                                 AssignTo=assign_to_user,
#                                 AssignBy=request.user.id,
#                                 company_name=company,  # Save the value of the dynamically changing textbox
#                                 product_name=product_name,  # Set the product_name
#                             )
#
#                             detected_barcodes.append({
#                                 'barcode_data': barcode_data,
#                                 'barcode_type': barcode_type,
#                                 'file_saved_at': file_saved_at.strftime('%Y-%m-%d %H:%M:%S'),
#                                 # 'image_url': barcode_image.image.url,
#                                 'message': 'Barcode data saved successfully.',
#                             })
#                 else:
#                     detected_barcodes.append({
#                         'barcode_data': None,
#                         'barcode_type': None,
#                         'message': 'No barcode detected in the image.',
#                     })
#
#             return JsonResponse(detected_barcodes, safe=False)
#
#         elif barcode_option == 'writeSerialNumber':
#             # Handle serial number input
#             serial_numbers = request.POST.getlist('serialNumber')  # Get list of serial numbers
#             print("Serial Number:", serial_numbers)
#             detected_serial_numbers = []
#
#             for serial_number in serial_numbers:
#                 company = request.POST.get('solarPlateCompany')  # Get the value of the company field
#                 wattage = request.POST.get('wattage')  # Get the value of the wattage field
#                 new_customer_id = request.POST.get('new_customer_id')
#                 comp_name = request.POST.get('comp_name')  # Get the value of the dynamically changing textbox
#
#                 if comp_name:
#                     customer = Customer.objects.get(new_customer_id=comp_name)
#                     company_name = customer.Comp_name
#
#                 # Process serial_number as needed
#
#                 # Save the serial number in BarcodeImage table
#                 tz = pytz.timezone('Asia/Kolkata')  # Set the timezone to IST (Indian Standard Time)
#                 file_saved_at = timezone.now().astimezone(tz)
#
#                 if new_customer_id.isdigit():
#                     assign_to_user = User.objects.get(id=new_customer_id)
#                 else:
#                     assign_to_user = None
#
#                 barcode_image = BarcodeImage.objects.create(
#                     barcode_data=serial_number,
#                     barcode_type='Serial Number',  # Set the barcode_type for serial numbers
#                     company=company_name,  # Save the company value
#                     wattage=wattage,  # Save the wattage value
#                     file_saved_at=file_saved_at,
#                     AssignTo=assign_to_user,
#                     AssignBy=request.user.id,
#                     company_name=company,  # Save the value of the dynamically changing textbox
#                     product_name='SolarPanel',  # Set the product_name
#                 )
#
#                 detected_serial_numbers.append({
#                     'serial_number': serial_number,
#                     'file_saved_at': file_saved_at.strftime('%Y-%m-%d %H:%M:%S'),
#                     'message': 'Serial number saved successfully.',
#                 })
#
#             return JsonResponse(detected_serial_numbers, safe=False)
#
#     companies = Customer.objects.all()
#     for company in companies:
#         deployed_solarpanel_count = BarcodeImage.objects.filter(AssignTo_id=company.new_customer_id,
#                                                               product_name="SolarPanel").count()
#         remaining_solarpanel_count = company.qunt_solar - deployed_solarpanel_count
#         company.remaining_solarpanel_count = remaining_solarpanel_count
#
#     # Filter companies based on remaining_inverter_count
#     filtered_companies = [company for company in companies if company.remaining_solarpanel_count > 0]
#
#     context = {
#         'filtered_companies': filtered_companies,
#         'count1': count1,
#         'notification1': notification1,
#         'companies': companies,
#     }
#     return render(request, 'detect_barcodes/detect_barcodes.html', context)




def detect_barcode(request):
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')

    if request.method == 'POST':
        barcode_option = request.POST.get('barcodeOption')  # Get the selected barcode option
        print("barcodeOption", barcode_option)
        if barcode_option == 'uploadBarcode':
            # Handle barcode image upload
            images = request.FILES.getlist('image')  # Get list of uploaded images
            detected_barcodes = []

            for image in images:
                company = request.POST.get('solarPlateCompany')  # Get the value of the company field
                wattage = request.POST.get('wattage')  # Get the value of the wattage field
                new_customer_id = request.POST.get('new_customer_id')
                comp_name = request.POST.get('comp_name')  # Get the value of the dynamically changing textbox

                if comp_name:
                    customer = Customer.objects.get(new_customer_id=comp_name)
                    company_name = customer.Comp_name

                image_data = image.read()
                image_base64 = base64.b64encode(image_data).decode('utf-8')

                nparr = np.frombuffer(image_data, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                barcodes = pyzbar.decode(img)
                if barcodes:
                    for barcode in barcodes:
                        barcode_data = barcode.data.decode('utf-8')
                        barcode_type = barcode.type

                        existing_barcode = BarcodeImage.objects.filter(barcode_data=barcode_data).first()

                        if existing_barcode:
                            detected_barcodes.append({
                                'barcode_data': barcode_data,
                                'barcode_type': barcode_type,
                                'message': 'Barcode data already exists in the database.',
                            })
                        else:
                            tz = pytz.timezone('Asia/Kolkata')  # Set the timezone to IST (Indian Standard Time)
                            file_saved_at = timezone.now().astimezone(tz)

                            if new_customer_id.isdigit():
                                assign_to_user = User.objects.get(id=new_customer_id)
                            else:
                                assign_to_user = None

                            barcode_image = BarcodeImage.objects.create(
                                barcode_data=barcode_data,
                                barcode_type=barcode_type,
                                company=company_name,  # Save the company value
                                wattage=wattage,  # Save the wattage value
                                file_saved_at=file_saved_at,
                                # image=image,
                                AssignTo=assign_to_user,
                                AssignBy=request.user.id,
                                company_name=company,  # Save the value of the dynamically changing textbox
                                product_name='SolarPanel',  # Set the product_name
                            )

                            detected_barcodes.append({
                                'barcode_data': barcode_data,
                                'barcode_type': barcode_type,
                                'file_saved_at': file_saved_at.strftime('%Y-%m-%d %H:%M:%S'),
                                'message': 'Barcode data saved successfully.',
                            })
                else:
                    detected_barcodes.append({
                        'barcode_data': None,
                        'barcode_type': None,
                        'message': 'No barcode detected in the image.',
                    })

            return JsonResponse(detected_barcodes, safe=False)
        elif barcode_option == 'writeSerialNumber':
            # Handle serial number input
            print("barcodeOption", barcode_option)
            # serial_numbers = request.POST.get('serial')
            # serial_numbers = json.loads(serial_numbers_str) if serial_numbers_str else []
            serial_numbers_str = request.POST.get('serialNumbers')
            serial_numbers = json.loads(serial_numbers_str) if serial_numbers_str else []

            detected_barcodes = []
            print("serial_numbers", serial_numbers)
            for serial_number in serial_numbers:
                company = request.POST.get('solarPlateCompany')  # Get the value of the company field
                wattage = request.POST.get('wattage')  # Get the value of the wattage field
                new_customer_id = request.POST.get('new_customer_id')
                comp_name = request.POST.get('comp_name')  # Get the value of the dynamically changing textbox

                if comp_name:
                    customer = Customer.objects.get(new_customer_id=comp_name)
                    company_name = customer.Comp_name

                # Process serial_number as needed

                # Save the serial number in BarcodeImage table
                tz = pytz.timezone('Asia/Kolkata')  # Set the timezone to IST (Indian Standard Time)
                file_saved_at = timezone.now().astimezone(tz)

                if new_customer_id.isdigit():
                    assign_to_user = User.objects.get(id=new_customer_id)
                else:
                    assign_to_user = None

                barcode_image = BarcodeImage.objects.create(
                    barcode_data=serial_number,
                    barcode_type='Serial Number',  # Set the barcode_type for serial numbers
                    company=company_name,  # Save the company value
                    wattage=wattage,  # Save the wattage value
                    file_saved_at=file_saved_at,
                    AssignTo=assign_to_user,
                    AssignBy=request.user.id,
                    company_name=company,  # Save the value of the dynamically changing textbox
                    product_name='SolarPanel',  # Set the product_name
                )

                detected_barcodes.append({
                    'serial_number': serial_number,
                    'message': 'Serial number saved successfully.',
                })

            return JsonResponse(detected_barcodes, safe=False)

    companies = Customer.objects.all()
    for company in companies:
        deployed_solarpanel_count = BarcodeImage.objects.filter(AssignTo_id=company.new_customer_id,
                                                              product_name="SolarPanel").count()
        remaining_solarpanel_count = company.qunt_solar - deployed_solarpanel_count
        company.remaining_solarpanel_count = remaining_solarpanel_count

    # Filter companies based on remaining_solarpanel_count
    filtered_companies = [company for company in companies if company.remaining_solarpanel_count > 0]

    context = {
        'filtered_companies': filtered_companies,
        'count1': count1,
        'notification1': notification1,
        'companies': companies,
    }
    return render(request, 'detect_barcodes/detect_barcodes.html', context)




from django.http import JsonResponse
from django.shortcuts import render
# from .models import BarcodeImage, Customer, staff_Notification
# from django.utils import timezone
# import base64
# import cv2
# import numpy as np
# from pyzbar import pyzbar
# import pytz
# @login_required(login_url='user-login')
# def detect_barcode(request):
#     count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#     notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#
#     if request.method == 'POST':
#         barcode_option = request.POST.get('barcodeOption')  # Get the selected barcode option
#
#         if barcode_option == 'uploadBarcode':
#             # Handle barcode image upload
#             images = request.FILES.getlist('image')  # Get list of uploaded images
#             detected_barcodes = []
#
#             for image in images:
#                 company = request.POST.get('solarPlateCompany')  # Get the value of the company field
#                 wattage = request.POST.get('wattage')  # Get the value of the wattage field
#                 new_customer_id = request.POST.get('new_customer_id')
#                 comp_name = request.POST.get('comp_name')  # Get the value of the dynamically changing textbox
#
#                 if comp_name:
#                     customer = Customer.objects.get(new_customer_id=comp_name)
#                     company_name = customer.Comp_name
#
#                 image_data = image.read()
#                 image_base64 = base64.b64encode(image_data).decode('utf-8')
#
#                 nparr = np.frombuffer(image_data, np.uint8)
#                 img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#
#                 barcodes = pyzbar.decode(img)
#                 if barcodes:
#                     for barcode in barcodes:
#                         barcode_data = barcode.data.decode('utf-8')
#                         barcode_type = barcode.type
#
#                         existing_barcode = BarcodeImage.objects.filter(barcode_data=barcode_data).first()
#
#                         if existing_barcode:
#                             detected_barcodes.append({
#                                 'barcode_data': barcode_data,
#                                 'barcode_type': barcode_type,
#                                 'message': 'Barcode data already exists in the database.',
#                             })
#                         else:
#                             tz = pytz.timezone('Asia/Kolkata')  # Set the timezone to IST (Indian Standard Time)
#                             file_saved_at = timezone.now().astimezone(tz)
#
#                             if new_customer_id.isdigit():
#                                 assign_to_user = User.objects.get(id=new_customer_id)
#                             else:
#                                 assign_to_user = None
#
#                             barcode_image = BarcodeImage.objects.create(
#                                 barcode_data=barcode_data,
#                                 barcode_type=barcode_type,
#                                 company=company_name,  # Save the company value
#                                 wattage=wattage,  # Save the wattage value
#                                 file_saved_at=file_saved_at,
#                                 image=image,
#                                 AssignTo=assign_to_user,
#                                 AssignBy=request.user.id,
#                                 company_name=company,  # Save the value of the dynamically changing textbox
#                                 product_name='SolarPanel',  # Set the product_name
#                             )
#
#                             detected_barcodes.append({
#                                 'barcode_data': barcode_data,
#                                 'barcode_type': barcode_type,
#                                 'file_saved_at': file_saved_at.strftime('%Y-%m-%d %H:%M:%S'),
#                                 'message': 'Barcode data saved successfully.',
#                             })
#                 else:
#                     detected_barcodes.append({
#                         'barcode_data': None,
#                         'barcode_type': None,
#                         'message': 'No barcode detected in the image.',
#                     })
#
#             return JsonResponse(detected_barcodes, safe=False)
#
#         elif barcode_option == 'writeSerialNumber':
#             # Handle serial number input
#             serial_numbers = request.POST.getlist('serialNumber')  # Get list of serial numbers
#             detected_serial_numbers = []
#
#             for serial_number in serial_numbers:
#                 company = request.POST.get('solarPlateCompany')  # Get the value of the company field
#                 wattage = request.POST.get('wattage')  # Get the value of the wattage field
#                 new_customer_id = request.POST.get('new_customer_id')
#                 comp_name = request.POST.get('comp_name')  # Get the value of the dynamically changing textbox
#
#                 if comp_name:
#                     customer = Customer.objects.get(new_customer_id=comp_name)
#                     company_name = customer.Comp_name
#
#                 # Process serial_number as needed
#
#                 # Save the serial number in BarcodeImage table
#                 tz = pytz.timezone('Asia/Kolkata')  # Set the timezone to IST (Indian Standard Time)
#                 file_saved_at = timezone.now().astimezone(tz)
#
#                 if new_customer_id.isdigit():
#                     assign_to_user = User.objects.get(id=new_customer_id)
#                 else:
#                     assign_to_user = None
#
#                 barcode_image = BarcodeImage.objects.create(
#                     barcode_data=serial_number,
#                     barcode_type='Serial Number',  # Set the barcode_type for serial numbers
#                     company=company_name,  # Save the company value
#                     wattage=wattage,  # Save the wattage value
#                     file_saved_at=file_saved_at,
#                     AssignTo=assign_to_user,
#                     AssignBy=request.user.id,
#                     company_name=company,  # Save the value of the dynamically changing textbox
#                     product_name='SolarPanel',  # Set the product_name
#                 )
#
#                 detected_serial_numbers.append({
#                     'serial_number': serial_number,
#                     'file_saved_at': file_saved_at.strftime('%Y-%m-%d %H:%M:%S'),
#                     'message': 'Serial number saved successfully.',
#                 })
#
#             return JsonResponse(detected_serial_numbers, safe=False)
#
#     companies = Customer.objects.all()
#     for company in companies:
#         deployed_solarpanel_count = BarcodeImage.objects.filter(AssignTo_id=company.new_customer_id,
#                                                               product_name="SolarPanel").count()
#         remaining_solarpanel_count = company.qunt_solar - deployed_solarpanel_count
#         company.remaining_solarpanel_count = remaining_solarpanel_count
#
#     # Filter companies based on remaining_solarpanel_count
#     filtered_companies = [company for company in companies if company.remaining_solarpanel_count > 0]
#
#     context = {
#         'filtered_companies': filtered_companies,
#         'count1': count1,
#         'notification1': notification1,
#         'companies': companies,
#     }
#     return render(request, 'detect_barcodes/detect_barcodes.html', context)


# def detect_barcode(request):
#     count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#     notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#     if request.method == 'POST':
#         images = request.FILES.getlist('image')  # Get list of uploaded images
#         detected_barcodes = []
#         product_name = None
#
#         # Determine the product_name based on the template being used
#         if request.path == '/detect_barcodes/detect_barcodes/':
#             product_name = 'SolarPanel'
#         elif request.path == '/detect_barcodes/detect_inverter/':
#             product_name = 'Inverter'
#
#         for image in images:
#             company = request.POST.get('solarPlateCompany')  # Get the value of the company field
#             wattage = request.POST.get('wattage')  # Get the value of the wattage field
#             new_customer_id = request.POST.get('new_customer_id')
#             comp_name = request.POST.get('comp_name')  # Get the value of the dynamically changing textbox
#
#             if comp_name:
#                 # company_name = Customer.objects.filter(Comp_name=comp_name)
#                 # company_name = Customer.objects.get(new_customer_id=comp_name)
#                 customer = Customer.objects.get(new_customer_id=comp_name)
#                 company_name = customer.Comp_name
#             # print(company_name)
#
#             image_data = image.read()
#             image_base64 = base64.b64encode(image_data).decode('utf-8')
#
#             nparr = np.frombuffer(image_data, np.uint8)
#             img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#
#             barcodes = pyzbar.decode(img)
#             if barcodes:
#                 for barcode in barcodes:
#                     barcode_data = barcode.data.decode('utf-8')
#                     barcode_type = barcode.type
#
#                     existing_barcode = BarcodeImage.objects.filter(barcode_data=barcode_data).first()
#
#                     if existing_barcode:
#                         detected_barcodes.append({
#                             'barcode_data': barcode_data,
#                             'barcode_type': barcode_type,
#                             'message': 'Barcode data already exists in the database.',
#                         })
#                     else:
#                         tz = pytz.timezone('Asia/Kolkata')  # Set the timezone to IST (Indian Standard Time)
#                         file_saved_at = timezone.now().astimezone(tz)
#
#                         if new_customer_id.isdigit():
#                             assign_to_user = User.objects.get(id=new_customer_id)
#                         else:
#                             assign_to_user = None
#
#                         barcode_image = BarcodeImage.objects.create(
#                             barcode_data=barcode_data,
#                             barcode_type=barcode_type,
#                             company=company_name,  # Save the company value
#                             wattage=wattage,  # Save the wattage value
#                             file_saved_at=file_saved_at,
#                             image=image,
#                             AssignTo=assign_to_user,
#                             AssignBy=request.user.id,
#                             company_name=company,  # Save the value of the dynamically changing textbox
#                             product_name=product_name,  # Set the product_name
#                         )
#
#                         detected_barcodes.append({
#                             'barcode_data': barcode_data,
#                             'barcode_type': barcode_type,
#                             'file_saved_at': file_saved_at.strftime('%Y-%m-%d %H:%M:%S'),
#                             'image_url': barcode_image.image.url,
#                             'message': 'Barcode data saved successfully.',
#                         })
#             else:
#                 detected_barcodes.append({
#                     'barcode_data': None,
#                     'barcode_type': None,
#                     'message': 'No barcode detected in the image.',
#                 })
#
#         return JsonResponse(detected_barcodes, safe=False)

#     companies = Customer.objects.all()
#     for company in companies:
#         deployed_solarpanel_count = BarcodeImage.objects.filter(AssignTo_id=company.new_customer_id,
#                                                               product_name="SolarPanel").count()
#         remaining_solarpanel_count = company.qunt_solar - deployed_solarpanel_count
#         company.remaining_solarpanel_count = remaining_solarpanel_count
#
#     # Filter companies based on remaining_inverter_count
#     filtered_companies = [company for company in companies if company.remaining_solarpanel_count > 0]
#
#     context = {
#         'filtered_companies': filtered_companies,
#         'count1': count1,
#         'notification1': notification1,
#         'companies': companies,
#     }
#     return render(request, 'detect_barcodes/detect_barcodes.html', context)


@login_required(login_url='user-login')
def detect_inverter(request):
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    if request.method == 'POST':
        images = request.FILES.getlist('image')  # Get list of uploaded images
        detected_barcodes = []
        product_name = None

        # Determine the product_name based on the template being used
        if request.path == '/detect_barcodes/detect_barcodes/':
            product_name = 'SolarPanel'
        elif request.path == '/detect_barcodes/detect_inverter/':
            product_name = 'Inverter'

        for image in images:
            company = request.POST.get('solarPlateCompany')  # Get the value of the company field
            wattage = request.POST.get('wattage')  # Get the value of the wattage field
            new_customer_id = request.POST.get('new_customer_id')
            comp_name = request.POST.get('comp_name')  # Get the value of the dynamically changing textbox

            if comp_name:
                # company_name = Customer.objects.filter(Comp_name=comp_name)
                # company_name = Customer.objects.get(new_customer_id=comp_name)
                customer = Customer.objects.get(new_customer_id=comp_name)
                company_name = customer.Comp_name

            image_data = image.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')

            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            barcodes = pyzbar.decode(img)
            if barcodes:
                for barcode in barcodes:
                    barcode_data = barcode.data.decode('utf-8')
                    barcode_type = barcode.type

                    existing_barcode = BarcodeImage.objects.filter(barcode_data=barcode_data).first()

                    if existing_barcode:
                        detected_barcodes.append({
                            'barcode_data': barcode_data,
                            'barcode_type': barcode_type,
                            'message': 'Barcode data already exists in the database.',
                        })
                    else:
                        tz = pytz.timezone('Asia/Kolkata')  # Set the timezone to IST (Indian Standard Time)
                        file_saved_at = timezone.now().astimezone(tz)

                        if new_customer_id.isdigit():
                            assign_to_user = User.objects.get(id=new_customer_id)
                        else:
                            assign_to_user = None

                        barcode_image = BarcodeImage.objects.create(
                            barcode_data=barcode_data,
                            barcode_type=barcode_type,
                            company=company_name,  # Save the company value
                            wattage=wattage,  # Save the wattage value
                            file_saved_at=file_saved_at,
                            # image=image,
                            AssignTo=assign_to_user,
                            AssignBy=request.user.id,
                            company_name=company,  # Save the value of the dynamically changing textbox
                            product_name=product_name  # Set the product_name
                        )

                        detected_barcodes.append({
                            'barcode_data': barcode_data,
                            'barcode_type': barcode_type,
                            'file_saved_at': file_saved_at.strftime('%Y-%m-%d %H:%M:%S'),
                            # 'image_url': barcode_image.image.url,
                            'message': 'Barcode data saved successfully.',
                        })
            else:
                detected_barcodes.append({
                    'barcode_data': None,
                    'barcode_type': None,
                    'message': 'No barcode detected in the image.',
                })

        return JsonResponse(detected_barcodes, safe=False)

    companies = Customer.objects.all()
    # Calculate remaining_inverter_count for each company
    for company in companies:
        deployed_inverter_count = BarcodeImage.objects.filter(AssignTo_id=company.new_customer_id,
                                                              product_name="Inverter").count()
        remaining_inverter_count = company.qunt_inv - deployed_inverter_count
        company.remaining_inverter_count = remaining_inverter_count

    # Filter companies based on remaining_inverter_count
    filtered_companies = [company for company in companies if company.remaining_inverter_count > 0]

    context = {
        'filtered_companies': filtered_companies,
        'count1': count1,
        'notification1': notification1,
        'companies': companies,
    }
    return render(request, 'detect_barcodes/detect_inverter.html', context)


# def detect_barcode(request):
#     if request.method == 'POST':
#         images = request.FILES.getlist('image')  # Get list of uploaded images
#         detected_barcodes = []
#
#         for image in images:
#             company = request.POST.get('solarPlateCompany')  # Get the value of the company field
#             wattage = request.POST.get('wattage')  # Get the value of the wattage field
#             new_customer_id = request.POST.get('new_customer_id')
#             company_name = request.POST.get('comp_name')  # Get the value of the dynamically changing textbox
#             #print(company_name)
#             image_data = image.read()
#             image_base64 = base64.b64encode(image_data).decode('utf-8')
#
#             nparr = np.frombuffer(image_data, np.uint8)
#             img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#
#             barcodes = pyzbar.decode(img)
#             if barcodes:
#                 for barcode in barcodes:
#                     barcode_data = barcode.data.decode('utf-8')
#                     barcode_type = barcode.type
#
#                     existing_barcode = BarcodeImage.objects.filter(barcode_data=barcode_data).first()
#
#                     if existing_barcode:
#                         detected_barcodes.append({
#                             'barcode_data': barcode_data,
#                             'barcode_type': barcode_type,
#                             'message': 'Barcode data already exists in the database.',
#                         })
#                     else:
#                         tz = pytz.timezone('Asia/Kolkata')  # Set the timezone to IST (Indian Standard Time)
#                         file_saved_at = timezone.now().astimezone(tz)
#
#                         if new_customer_id.isdigit():
#                             #assign_to_user = int(new_customer_id)
#                             assign_to_user = User.objects.get(id=new_customer_id)
#                         else:
#                             assign_to_user = None
#
#                         barcode_image = BarcodeImage.objects.create(
#                             barcode_data=barcode_data,
#                             barcode_type=barcode_type,
#                             company=company_name,  # Save the company value
#                             wattage=wattage,  # Save the wattage value
#                             file_saved_at=file_saved_at,
#                             image=image,
#                             AssignTo=assign_to_user,
#                             AssignBy=request.user.id,
#                             company_name=company,  # Save the value of the dynamically changing textbox
#                             product_name='SolarPanel'
#                         )
#
#                         detected_barcodes.append({
#                             'barcode_data': barcode_data,
#                             'barcode_type': barcode_type,
#                             'file_saved_at': file_saved_at.strftime('%Y-%m-%d %H:%M:%S'),
#                             'image_url': barcode_image.image.url,
#                             'message': 'Barcode data saved successfully.',
#                         })
#             else:
#                 detected_barcodes.append({
#                     'barcode_data': None,
#                     'barcode_type': None,
#                     'message': 'No barcode detected in the image.',
#                 })
#
#         return JsonResponse(detected_barcodes, safe=False)
#
#     companies = Customer.objects.all()
#     return render(request, 'detect_barcodes/detect_barcodes.html', {'companies': companies})
#


@login_required(login_url='user-login')
def get_customer_details(request):
    if request.method == 'GET':
        new_customer_id = request.GET.get('new_customer_id')
        if new_customer_id:
            customer = Customer.objects.filter(new_customer=new_customer_id).first()
            print(new_customer_id)
            # customers = Customer.objects.filter(new_customer__username=comp_name)

            if customer:
                # Now that you have the Customer instance, use it to fetch the related User instance
                user = User.objects.filter(id=customer.new_customer_id).first()
                if user:
                    # Use the User instance to filter BarcodeImage
                    deployed_solar_panel_count = BarcodeImage.objects.filter(AssignTo_id=user,
                                                                             product_name="SolarPanel").count()

            data = {
                    'Comp_name': customer.Comp_name,
                    'phone': customer.phone,
                    'Address': customer.Address,
                    'City': customer.City,
                    'Plant_Capacity': customer.Plant_Capacity,
                    'new_customer_id': customer.new_customer_id,  # Add the new field here
                    'qunt_solar': customer.qunt_solar,
                    'deployed_solar_panel_count': deployed_solar_panel_count,  # Add deployed count
                    'remaining_solar_panel_count': customer.qunt_solar - deployed_solar_panel_count,  # Calculate remaining count
                    # Add other fields here
                }
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse(json.dumps({}), content_type='application/json')


@login_required(login_url='user-login')
def get_inverter_details(request):
    if request.method == 'GET':
        new_customer_id = request.GET.get('new_customer_id')
        if new_customer_id:
            # customer = Customer.objects.filter(Comp_name=comp_name).first()
            customer = Customer.objects.filter(new_customer=new_customer_id).first()
            if customer:
                # Now that you have the Customer instance, use it to fetch the related User instance
                user = User.objects.filter(id=customer.new_customer_id).first()
                if user:
                    # Use the User instance to filter BarcodeImage
                    deployed_inverter_count = BarcodeImage.objects.filter(AssignTo_id=user,
                                                                             product_name="Inverter").count()

                data = {
                    'Comp_name': customer.Comp_name,
                    'phone': customer.phone,
                    'Address': customer.Address,
                    'City': customer.City,
                    'Plant_Capacity': customer.Plant_Capacity,
                    'new_customer_id': customer.new_customer_id,  # Add the new field here
                    'qunt_inv': customer.qunt_inv,
                    'deployed_inverter_count': deployed_inverter_count,  # Add deployed count
                    'remaining_inverter_count': customer.qunt_inv - deployed_inverter_count,
                    # Calculate remaining count

                }
                return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponse(json.dumps({}), content_type='application/json')

#
#
# def pdf_barcode_create(request,pk):
#          panel = BarcodeImage.objects.filter(AssignTo=pk)
#          template_path = 'detect_barcodes/barcodepdf.html'
#          context = {'panel': panel}
#          response = HttpResponse(content_type='application/pdf')
#          #response['Content-Disposition'] = 'filename="report.pdf"'
#          response['Content-Disposition'] = 'attachment; filename="report.pdf"'
#          template = get_template(template_path)
#          html = template.render(context)
#          pisa_status = pisa.CreatePDF(html, dest=response, link_callback=link_callback)
#
#          if pisa_status.err:
#              return HttpResponse('we had some errors <pre>' + html + '</pre>')
#          return response
#
# #         images = request.FILES.getlist('image')  # Get list of uploaded images
# #         detected_barcodes = []
# #
# #         for image in images:
# #             # Image processing code here
# #
# #             # Barcode detection and handling code here
# #
# #             template_path = 'detect_barcodes/barcodepdf.html'
# #             context = {'detected_barcodes': detected_barcodes}
# #             response = HttpResponse(content_type='application/pdf')
# #             response['Content-Disposition'] = 'filename="report.pdf"'
# #             template = get_template(template_path)
# #             html = template.render(context)
# #
# #             pisa_status = pisa.CreatePDF(html, dest=response)
# #             if pisa_status.err:
# #                 return HttpResponse('We had some errors <pre>' + html + '</pre>')
# #
# #         return response  # Move the return statement outside the loop
#
#

# from django.shortcuts import render
# from django.http import HttpResponse
# from django.template.loader import get_template
# from django.template import Context
# from reportlab.pdfgen import canvas


from django.http import HttpResponse
from django.template.loader import get_template
from io import BytesIO
from xhtml2pdf import pisa


from io import BytesIO
from django.template.loader import get_template
from xhtml2pdf import pisa

from django.shortcuts import render
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import io

@login_required(login_url='user-login')
def generate_pdf(request):
    # Retrieve the data from the previous HTML template
    detected_barcodes = request.session.get('detected_barcodes', [])
    duplicate_barcodes_count = request.session.get('duplicate_barcodes_count', 0)

    # Generate the PDF page using the data
    template = get_template('detect_barcodes/pdf_template.html')
    context = {
        'detected_barcodes': detected_barcodes,
        'duplicate_barcodes_count': duplicate_barcodes_count,
    }
    rendered_template = template.render(context)

    # Create a BytesIO stream to receive the PDF output
    result = BytesIO()

    # Create the PDF document
    pdf = pisa.CreatePDF(BytesIO(rendered_template.encode('UTF-8')), dest=result)

    if not pdf.err:
        # Set the response headers for the PDF file
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="barcode_results.pdf"'

        # Get the PDF content from the BytesIO stream
        pdf_data = result.getvalue()
        result.close()

        # Write the PDF content to the response
        response.write(pdf_data)

        return response
    else:
        return HttpResponse("Error generating PDF", status=500)


@login_required(login_url='user-login')
def barcode_image_view(request):
    companies = BarcodeImage.objects.order_by().values_list('company', flat=True).distinct()
    return render(request, 'detect_barcodes/barcodepdf.html', {'companies': companies})

@login_required(login_url='user-login')
def get_images(request):
    selected_company = request.GET.get('selected_company')
    barcode_images = BarcodeImage.objects.filter(company=selected_company)
    inverter_images = InverterImage.objects.filter(company=selected_company)

    barcode_data = [image.barcode_data for image in barcode_images]
    barcode_paths = [image.barcode_path.url for image in barcode_images]
    inverter_paths = [image.barcode_path.url for image in inverter_images]

    data = {
        'barcode_data': barcode_data,
        'barcode_paths': barcode_paths,
        'inverter_paths': inverter_paths,
    }
    return JsonResponse(data)

# def generate1_pdf(request):
#     selected_companies = request.GET.getlist('selectedCompanies[]')
#     # Logic to generate PDF using a library like reportlab or weasyprint
#     # Create a PDF with the selected companies and their related images
#     # Return the PDF file or its download link
#     # Example: https://www.reportlab.com/docs/reportlab-userguide.pdf
#     # For this example, we'll just return a placeholder message.
#     response_data = {'message': 'PDF generated successfully'}
#     return JsonResponse(response_data)

from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from django.http import HttpResponse
from reportlab.pdfgen import canvas

@login_required(login_url='user-login')
def generate1_pdf(request):
    selected_companies = request.GET.getlist('selectedCompanies[]')
    # Generate the PDF content using reportlab or any other library
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="generated.pdf"'

    # Generate the PDF content and save it to the response
    p = canvas.Canvas(response)
    # Add content to the PDF
    p.drawString(100, 750, "Hello, world.")
    # Save the PDF content
    p.showPage()
    p.save()
    return response


from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Count, Sum


# def search_view(request):
#     companies = BarcodeImage.objects.values_list('company', flat=True).distinct()
#     product_names = BarcodeImage.objects.values_list('product_name', flat=True).distinct()
#     items = []
#     solar_items = []
#     inverter_items = []
#
#     solar_panel_total_quantity = 0  # Initialize as an integer
#     solar_panel_quantity_by_wattage = []
#     unique_wattages = []
#     wattage_quantity_dict = {}
#
#     if request.method == 'POST':
#         selected_company = request.POST.get('company')
#         selected_product = request.POST.get('product')
#
#         if selected_product == 'All':
#             items = BarcodeImage.objects.filter(company=selected_company)
#             solar_items = items.filter(product_name='SolarPanel')
#             inverter_items = items.filter(product_name='Inverter')
#         elif selected_product == 'SolarPanel':
#             items = BarcodeImage.objects.filter(company=selected_company)
#             solar_items = items.filter(product_name='SolarPanel')
#         else:
#             items = BarcodeImage.objects.filter(company=selected_company)
#             inverter_items = items.filter(product_name='Inverter')
#
#
#         # Calculate total quantity for Solar Panel items
#         solar_panel_total_quantity = solar_items.count()
#
#         # Calculate total quantity for each unique wattage value
#         solar_panel_quantity_by_wattage = solar_items.values('wattage').annotate(total_quantity=Count('id'))
#
#         # Create a dictionary to store quantities by wattage
#         wattage_quantity_dict = {item['wattage']: item['total_quantity'] for item in solar_panel_quantity_by_wattage}
#
#         # Get unique wattage values for Solar Panel items
#         unique_wattages = {item['wattage'] for item in solar_panel_quantity_by_wattage}
#
#     return render(request, 'detect_barcodes/search_form.html',
#                   {'companies': companies, 'product_names': product_names, 'items': items,
#                    'solar_items': solar_items, 'inverter_items': inverter_items,
#                    'solar_panel_total_quantity': solar_panel_total_quantity, 'solar_panel_quantity_by_wattage': solar_panel_quantity_by_wattage,
#                    'unique_wattages': unique_wattages, 'wattage_quantity_dict': wattage_quantity_dict})

@login_required(login_url='user-login')
def search_view(request):
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    companies = BarcodeImage.objects.values_list('company', flat=True).distinct()
    product_names = BarcodeImage.objects.values_list('product_name', flat=True).distinct()
    items1 = BarcodeImage.objects.all()
    items = []
    solar_items = []
    inverter_items = []
    solar_panel_total_quantity = 0  # Initialize as an integer
    solar_panel_quantity_by_wattage = []
    unique_wattages = []
    inverter_wattages = []
    inverter_panel_quantity_by_wattage = []
    inverter_panel_total_quantity = 0
    wattage1_quantity_dict = []

    wattage_quantity_dict = {}

    if request.method == 'POST':
        selected_company = request.POST.get('company')
        selected_product = request.POST.get('product')

        if selected_product == 'All':
            items = BarcodeImage.objects.filter(company=selected_company)
            solar_items = items.filter(product_name='SolarPanel')
            inverter_items = items.filter(product_name='Inverter')
            # Calculate total quantity for Solar Panel items
            solar_panel_total_quantity = solar_items.count()

            # Calculate total quantity for each unique wattage value
            solar_panel_quantity_by_wattage = solar_items.values('wattage').annotate(total_quantity=Count('id'))

            # Calculate total quantity for Solar Panel items
            inverter_panel_total_quantity = inverter_items.count()

            # Calculate total quantity for each unique wattage value
            inverter_panel_quantity_by_wattage = inverter_items.values('wattage').annotate(total_quantity=Count('id'))


        elif selected_product == 'SolarPanel':
            items = BarcodeImage.objects.filter(company=selected_company)
            solar_items = items.filter(product_name='SolarPanel')
            # Calculate total quantity for Solar Panel items
            solar_panel_total_quantity = solar_items.count()

            # Calculate total quantity for each unique wattage value
            solar_panel_quantity_by_wattage = solar_items.values('wattage').annotate(total_quantity=Count('id'))
        elif selected_product == 'Inverter':
            items = BarcodeImage.objects.filter(company=selected_company)
            inverter_items = items.filter(product_name='Inverter')

            # Calculate total quantity for Solar Panel items
            inverter_panel_total_quantity = inverter_items.count()

            # Calculate total quantity for each unique wattage value
            inverter_panel_quantity_by_wattage = inverter_items.values('wattage').annotate(total_quantity=Count('id'))



        # Create a dictionary to store quantities by wattage
        #wattage_quantity_dict = {item['wattage']: item['total_quantity'] for item in solar_panel_quantity_by_wattage}
        #wattage1_quantity_dict = {item['wattage']: item['total_quantity'] for item in inverter_panel_quantity_by_wattage}

        # Get unique wattage values for Solar Panel items
        unique_wattages = {item['wattage'] for item in solar_panel_quantity_by_wattage}
        inverter_wattages = {item['wattage'] for item in inverter_panel_quantity_by_wattage}

    return render(request, 'detect_barcodes/search_form.html',
                  {'companies': companies, 'product_names': product_names, 'items': items,
                   'solar_items': solar_items, 'inverter_items': inverter_items,
                   'solar_panel_total_quantity': solar_panel_total_quantity, 'solar_panel_quantity_by_wattage': solar_panel_quantity_by_wattage,
                   'unique_wattages': unique_wattages, 'wattage_quantity_dict': wattage_quantity_dict,'inverter_wattages': inverter_wattages,
                   'inverter_panel_total_quantity': inverter_panel_total_quantity,'wattage1_quantity_dict': wattage1_quantity_dict,
                   'inverter_panel_quantity_by_wattage': inverter_panel_quantity_by_wattage, 'items1': items1, 'notification1': notification1,
                   'count1': count1,})


# views.py
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from io import BytesIO

# views.py
from django.http import HttpResponse
from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa
from io import BytesIO

# views.py
from django.http import HttpResponse
from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa
from io import BytesIO
from .models import BarcodeImage

# views.py
from django.http import HttpResponse
from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa
from io import BytesIO
from django.utils.encoding import smart_str

# views.py
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa
from io import BytesIO
from django.utils.encoding import smart_str
from .models import BarcodeImage  # Make sure to import your model here

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import BarcodeImage


# def GeneratePDF(request):
#   if request.method == 'POST':
#     selected_company = request.POST.get('selected_company')
#     print(selected_company)
#     #selected_company = BarcodeImage.objects.get(AssignTo=pid)
#    # selected_company = request.GET.get('company')  # Get the selected company from the request
#     #print(selected_company)
#     companies = BarcodeImage.objects.values_list('company', flat=True).distinct()
#    # selected_company = BarcodeImage.objects.filter(AssignTo=pk)
#
#     product_names = BarcodeImage.objects.values_list('product_name', flat=True).distinct()
#
#
#     # Query the database to get data for the selected company
#     solar_items = BarcodeImage.objects.filter(company=selected_company, product_name='SolarPanel')
#     inverter_items = BarcodeImage.objects.filter(company=selected_company, product_name='Inverter')
#
#     #solar_items = BarcodeImage.objects.filter(product_name='SolarPanel')
#     #inverter_items = BarcodeImage.objects.filter(product_name='Inverter')
#
#     inverter_panel_quantity_by_wattage = inverter_items.values('wattage').annotate(total_quantity=Count('id'))
#     solar_panel_quantity_by_wattage = solar_items.values('wattage').annotate(total_quantity=Count('id'))
#     unique_wattages = {item['wattage'] for item in solar_panel_quantity_by_wattage}
#     inverter_wattages = {item['wattage'] for item in inverter_panel_quantity_by_wattage}
#     inverter_panel_total_quantity = inverter_items.count()
#     solar_panel_total_quantity = solar_items.count()
#
#     # Prepare the context
#     context = {
#         'companies': companies,
#         'product_names': product_names,
#         'solar_items': solar_items,
#         'inverter_items': inverter_items,
#         'unique_wattages': unique_wattages,
#         'inverter_wattages': inverter_wattages,
#         'inverter_panel_total_quantity': inverter_panel_total_quantity,
#         'solar_panel_total_quantity': solar_panel_total_quantity,
#         'inverter_panel_quantity_by_wattage': inverter_panel_quantity_by_wattage,
#         'solar_panel_quantity_by_wattage': solar_panel_quantity_by_wattage,
#     }
#
#     # Generate the PDF
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = 'attachment; filename="pdf_template.pdf"'
#     #response['Content-Disposition'] = f'filename="{selected_company}_pdf_template.pdf"'
#
#     template_path = 'detect_barcodes/pdf_template.html'
#     template = get_template(template_path)
#     html = template.render(context)
#     pisa_status = pisa.CreatePDF(html, dest=response)
#
#     if pisa_status.err:
#         return HttpResponse('PDF generation failed <pre>' + html + '</pre>')
#     return response


from PIL import Image



@login_required(login_url='user-login')
def GeneratePDF(request):
        selected_company = request.POST.get('selected_company')
        selected_product = request.POST.get('selected_product')
        # selected_company = request.POST.get('selectedCompanySpan')
        # selected_product = request.POST.get('selectedProduct')
        invoice_number = request.POST.get('invoice_number')
        print("Selected Company:", selected_company)  # Print the value for debugging
        print("selected_product:", selected_product)  # Print the value for debugging
        selected_no = request.POST.get('selected_no')  # Get the selected radio button value
        print("selected_no:", selected_no)

        companies = BarcodeImage.objects.values_list('company', flat=True).distinct()
        product_names = BarcodeImage.objects.values_list('product_name', flat=True).distinct()
        items = []
        solar_items = []
        inverter_items = []
        solar_panel_total_quantity = 0  # Initialize as an integer
        solar_panel_quantity_by_wattage = []
        unique_wattages = []
        inverter_wattages = []
        inverter_panel_quantity_by_wattage = []
        inverter_panel_total_quantity = 0
        wattage1_quantity_dict = []

        wattage_quantity_dict = {}

        #solar_items = BarcodeImage.objects.filter(company=selected_company, product_name='SolarPanel')
        #inverter_items = BarcodeImage.objects.filter(company=selected_company, product_name='Inverter')


        if selected_product == 'All':
            items = BarcodeImage.objects.filter(company=selected_company)
            solar_items = items.filter(product_name='SolarPanel')
            inverter_items = items.filter(product_name='Inverter')
            inverter_panel_quantity_by_wattage = inverter_items.values('wattage').annotate(total_quantity=Count('id'))
            solar_panel_quantity_by_wattage = solar_items.values('wattage').annotate(total_quantity=Count('id'))
            unique_wattages = {item['wattage'] for item in solar_panel_quantity_by_wattage}
            inverter_wattages = {item['wattage'] for item in inverter_panel_quantity_by_wattage}
            inverter_panel_total_quantity = inverter_items.count()
            solar_panel_total_quantity = solar_items.count()



        elif selected_product == 'SolarPanel':
            items = BarcodeImage.objects.filter(company=selected_company)
            solar_items = items.filter(product_name='SolarPanel')
            solar_panel_quantity_by_wattage = solar_items.values('wattage').annotate(total_quantity=Count('id'))
            unique_wattages = {item['wattage'] for item in solar_panel_quantity_by_wattage}
            solar_panel_total_quantity = solar_items.count()

        else:
            items = BarcodeImage.objects.filter(company=selected_company)
            inverter_items = items.filter(product_name='Inverter')
            inverter_panel_quantity_by_wattage = inverter_items.values('wattage').annotate(total_quantity=Count('id'))
            inverter_wattages = {item['wattage'] for item in inverter_panel_quantity_by_wattage}
            inverter_panel_total_quantity = inverter_items.count()

        paired_solar_items = []
        serial_number = 1
        for i in range(0, len(solar_items), 2):
            if i + 1 < len(solar_items):
                pair = [
                    {'serial_number': serial_number, 'item': solar_items[i]},
                    {'serial_number': serial_number + 1, 'item': solar_items[i + 1]}
                ]
            else:
                pair = [
                    {'serial_number': serial_number, 'item': solar_items[i]},
                    {'serial_number': serial_number + 1, 'item': None}
                ]
            paired_solar_items.append(pair)
            serial_number += 2



        paired_inverter_items = []
        serial_number = 1
        for i in range(0, len(inverter_items), 2):
            if i + 1 < len(inverter_items):
                pair = [
                    {'serial_number': serial_number, 'item': inverter_items[i]},
                    {'serial_number': serial_number + 1, 'item': inverter_items[i + 1]}
                ]
            else:
                pair = [
                    {'serial_number': serial_number, 'item': inverter_items[i]},
                    {'serial_number': serial_number + 1, 'item': None}
                ]
            paired_inverter_items.append(pair)
            serial_number += 2





        # paired_inverter_items = []
        # serial_number = 1
        # for i in range(0, len(inverter_items), 2):
        #     pair = [
        #         {'serial_number': serial_number, 'item': inverter_items[i]},
        #         {'serial_number': serial_number + 1,
        #          'item': inverter_items[i + 1] if i + 1 < len(inverter_items) else {'dummy': True}}
        #     ]
        #     paired_inverter_items.append(pair)
        #     serial_number += 2

          # Get the Profile object associated with the selected company
        customer = Customer.objects.filter(Comp_name=selected_company).first()


        user = items.first().AssignTo_id  # Assuming AssignTo is a ForeignKey to User model
        profile = Profile.objects.get(customer_id=user)
        date = datetime.now()
        # date1 = datetime.today().strftime("%d /%m /%Y")
        date1 = datetime.today().strftime("%d %b %Y")
        # image_url = request.build_absolute_uri(settings.MEDIA_URL + 'static/images/dblogo2001.png')
        image_url = request.build_absolute_uri(settings.MEDIA_URL + 'static/images/DB SOLAR PNG LOGO 3 (6).png')
        context = {
            'image_url': image_url,
            'customer': customer,
            'date': date,
            'date1': date1,
            'profile': profile,
            'invoice_number': invoice_number,
            'companies': companies,
            'product_names': product_names,
            'solar_items1': solar_items,
            'inverter_items': inverter_items,
            'unique_wattages': unique_wattages,
            'inverter_wattages': inverter_wattages,
            'inverter_panel_total_quantity': inverter_panel_total_quantity,
            'solar_panel_total_quantity': solar_panel_total_quantity,
            'inverter_panel_quantity_by_wattage': inverter_panel_quantity_by_wattage,
            'solar_panel_quantity_by_wattage': solar_panel_quantity_by_wattage,
            'items': items,
            'solar_items': paired_solar_items,
            'inverter_items1': paired_inverter_items,
            'selected_no': selected_no,
        }

        response = HttpResponse(content_type='application/pdf')
        # response['Content-Disposition'] = 'attachment; filename="pdf_template.pdf"'


        # Modify the filename to use the selected_company
        filename = f"{selected_company}_invoice.pdf"

        # Set the Content-Disposition header with the modified filename
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        template_path = 'detect_barcodes/pdf_template.html'
        template = get_template(template_path)
        html = template.render(context)
        pisa_status = pisa.CreatePDF(html, dest=response)


        if pisa_status.err:
            return HttpResponse('PDF generation failed <pre>' + html + '</pre>', content_type='text/html')

        return response

# def editbarcode(request):
#     count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#     notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#     companies = BarcodeImage.objects.values_list('company', flat=True).distinct()
#     product_names = BarcodeImage.objects.values_list('product_name', flat=True).distinct()
#     items1 = BarcodeImage.objects.all()
#     items = []
#     solar_items = []
#     inverter_items = []
#     solar_panel_total_quantity = 0  # Initialize as an integer
#     solar_panel_quantity_by_wattage = []
#     unique_wattages = []
#     inverter_wattages = []
#     inverter_panel_quantity_by_wattage = []
#     inverter_panel_total_quantity = 0
#     wattage1_quantity_dict = []
#
#     wattage_quantity_dict = {}
#
#     if request.method == 'POST':
#         selected_company = request.POST.get('company')
#         selected_product = request.POST.get('product')
#
#         if selected_product == 'All':
#             items = BarcodeImage.objects.filter(company=selected_company)
#             solar_items = items.filter(product_name='SolarPanel')
#             inverter_items = items.filter(product_name='Inverter')
#             # Calculate total quantity for Solar Panel items
#             solar_panel_total_quantity = solar_items.count()
#
#             # Calculate total quantity for each unique wattage value
#             solar_panel_quantity_by_wattage = solar_items.values('wattage').annotate(total_quantity=Count('id'))
#
#             # Calculate total quantity for Solar Panel items
#             inverter_panel_total_quantity = inverter_items.count()
#
#             # Calculate total quantity for each unique wattage value
#             inverter_panel_quantity_by_wattage = inverter_items.values('wattage').annotate(total_quantity=Count('id'))
#
#
#         elif selected_product == 'SolarPanel':
#             items = BarcodeImage.objects.filter(company=selected_company)
#             solar_items = items.filter(product_name='SolarPanel')
#             # Calculate total quantity for Solar Panel items
#             solar_panel_total_quantity = solar_items.count()
#
#             # Calculate total quantity for each unique wattage value
#             solar_panel_quantity_by_wattage = solar_items.values('wattage').annotate(total_quantity=Count('id'))
#         else:
#             items = BarcodeImage.objects.filter(company=selected_company)
#             inverter_items = items.filter(product_name='Inverter')
#
#             # Calculate total quantity for Solar Panel items
#             inverter_panel_total_quantity = inverter_items.count()
#
#             # Calculate total quantity for each unique wattage value
#             inverter_panel_quantity_by_wattage = inverter_items.values('wattage').annotate(total_quantity=Count('id'))
#
#
#         # Create a dictionary to store quantities by wattage
#         #wattage_quantity_dict = {item['wattage']: item['total_quantity'] for item in solar_panel_quantity_by_wattage}
#         #wattage1_quantity_dict = {item['wattage']: item['total_quantity'] for item in inverter_panel_quantity_by_wattage}
#
#         # Get unique wattage values for Solar Panel items
#         unique_wattages = {item['wattage'] for item in solar_panel_quantity_by_wattage}
#         inverter_wattages = {item['wattage'] for item in inverter_panel_quantity_by_wattage}
#
#     return render(request, 'detect_barcodes/edit_barcode.html',
#                   {'companies': companies, 'product_names': product_names, 'items': items,
#                    'solar_items': solar_items, 'inverter_items': inverter_items,
#                    'solar_panel_total_quantity': solar_panel_total_quantity, 'solar_panel_quantity_by_wattage': solar_panel_quantity_by_wattage,
#                    'unique_wattages': unique_wattages, 'wattage_quantity_dict': wattage_quantity_dict,'inverter_wattages': inverter_wattages,
#                    'inverter_panel_total_quantity': inverter_panel_total_quantity,'wattage1_quantity_dict': wattage1_quantity_dict,
#                    'inverter_panel_quantity_by_wattage': inverter_panel_quantity_by_wattage, 'items1': items1, 'notification1': notification1,
#                    'count1': count1,})


from django.shortcuts import render, redirect
from django.db.models import Count
from .models import BarcodeImage  # Import your BarcodeImage model

# def editbarcode(request):
#     count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#     notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#     companies = BarcodeImage.objects.values_list('company', flat=True).distinct()
#     product_names = BarcodeImage.objects.values_list('product_name', flat=True).distinct()
#     items1 = BarcodeImage.objects.all()
#     items = []
#     solar_items = []
#     inverter_items = []
#     replace_items = []
#     solar_panel_total_quantity = 0
#     solar_panel_quantity_by_wattage = []
#     unique_wattages = []
#     inverter_wattages = []
#     inverter_panel_quantity_by_wattage = []
#     inverter_panel_total_quantity = 0
#     replace_wattages =[]
#     replace_panel_quantity_by_wattage = []
#     replace_panel_total_quantity = 0
#
#     if request.method == 'POST':
#         selected_company = request.POST.get('company')
#         selected_product = request.POST.get('product')
#
#         # Check if the form was submitted with edited values
#         if 'selected_items' in request.POST:
#             for item_id in request.POST.getlist('selected_items'):
#                 # Get the edited values from the form
#                 company_name = request.POST.get(f'company_name_{item_id}')
#                 wattage = request.POST.get(f'wattage_{item_id}')
#                 product_name = request.POST.get(f'product1_{item_id}')
#
#                 # Update the corresponding BarcodeImage record in the database if any values have changed
#                 try:
#                     barcode_image = BarcodeImage.objects.get(pk=item_id)
#                     if barcode_image.company_name != company_name:
#                         print(f'Company Name updated: {barcode_image.company_name} -> {company_name}')
#                         barcode_image.company_name = company_name
#                     if barcode_image.wattage != wattage:
#                         print(f'Wattage updated: {barcode_image.wattage} -> {wattage}')
#                         barcode_image.wattage = wattage
#                     # if barcode_image.product_name != product_name:
#                     #     print(f'Product Name updated: {barcode_image.product_name} -> {product_name}')
#                     #     barcode_image.product_name = product_name
#                         # Set the previous value of product1 if it's None or blank
#                         if not product_name:
#                             product_name = barcode_image.product_name
#                         elif barcode_image.product_name != product_name:
#                             print(f'Product Name updated: {barcode_image.product_name} -> {product_name}')
#                         barcode_image.product_name = product_name
#                     barcode_image.save()
#                 except BarcodeImage.DoesNotExist:
#                     # Handle the case where the item is not found in the database
#                     pass
#
#             # Redirect to the same page after processing the form
#             return redirect('editbarcode')  # Replace 'editbarcode' with your actual view name
#
#         if selected_product == 'All':
#             items = BarcodeImage.objects.filter(company=selected_company)
#             solar_items = items.filter(product_name='SolarPanel')
#             inverter_items = items.filter(product_name='Inverter')
#             replace_items = items.filter(product_names='Replace')
#             solar_panel_total_quantity = solar_items.count()
#             solar_panel_quantity_by_wattage = solar_items.values('wattage').annotate(total_quantity=Count('id'))
#             inverter_panel_total_quantity = inverter_items.count()
#             inverter_panel_quantity_by_wattage = inverter_items.values('wattage').annotate(total_quantity=Count('id'))
#             replace_panel_total_quantity = inverter_items.count()
#             replace_panel_quantity_by_wattage = inverter_items.values('wattage').annotate(total_quantity=Count('id'))
#         elif selected_product == 'SolarPanel':
#             items = BarcodeImage.objects.filter(company=selected_company)
#             solar_items = items.filter(product_name='SolarPanel')
#             solar_panel_total_quantity = solar_items.count()
#             solar_panel_quantity_by_wattage = solar_items.values('wattage').annotate(total_quantity=Count('id'))
#         elif selected_product == 'Inverter':
#             items = BarcodeImage.objects.filter(company=selected_company)
#             inverter_items = items.filter(product_name='Inverter')
#             inverter_panel_total_quantity = inverter_items.count()
#             inverter_panel_quantity_by_wattage = inverter_items.values('wattage').annotate(total_quantity=Count('id'))
#         else:
#             items = BarcodeImage.objects.filter(company=selected_company)
#             replace_items = items.filter(product_name='Replace')
#             replace_panel_total_quantity = replace_items.count()
#             replace_panel_quantity_by_wattage = replace_items.values('wattage').annotate(total_quantity=Count('id'))
#
#         unique_wattages = {item['wattage'] for item in solar_panel_quantity_by_wattage}
#         inverter_wattages = {item['wattage'] for item in inverter_panel_quantity_by_wattage}
#         replace_wattages = {item['wattage'] for item in replace_panel_quantity_by_wattage}
#     return render(request, 'detect_barcodes/edit_barcode.html',
#                   {'companies': companies, 'product_names': product_names, 'items': items,
#                    'solar_items': solar_items, 'inverter_items': inverter_items, 'replace_items': replace_items,
#                    'solar_panel_total_quantity': solar_panel_total_quantity, 'solar_panel_quantity_by_wattage': solar_panel_quantity_by_wattage,
#                    'unique_wattages': unique_wattages, 'inverter_wattages': inverter_wattages,
#                    'inverter_panel_total_quantity': inverter_panel_total_quantity,
#                    'inverter_panel_quantity_by_wattage': inverter_panel_quantity_by_wattage, 'items1': items1,
#
#                    'replace_panel_total_quantity': replace_panel_total_quantity,
#                    'replace_panel_quantity_by_wattage': replace_panel_quantity_by_wattage,
#                    'replace_wattages': replace_wattages,
#
#                    'notification1': notification1, 'count1': count1})

@login_required(login_url='user-login')
def editbarcode(request):
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    companies = BarcodeImage.objects.values_list('company', flat=True).distinct()
    product_names = BarcodeImage.objects.values_list('product_name', flat=True).distinct()
    items1 = BarcodeImage.objects.all()
    items = []
    solar_items = []
    inverter_items = []
    replace_items = []
    solar_panel_total_quantity = 0
    solar_panel_quantity_by_wattage = []
    unique_wattages = []
    inverter_wattages = []
    inverter_panel_quantity_by_wattage = []
    inverter_panel_total_quantity = 0
    replace_wattages = []
    replace_panel_quantity_by_wattage = []
    replace_panel_total_quantity = 0

    if request.method == 'POST':
        selected_company = request.POST.get('company')
        selected_product = request.POST.get('product')

        # Check if the form was submitted with edited values
        if 'selected_items' in request.POST:
            for item_id in request.POST.getlist('selected_items'):
                # Get the edited values from the form
                company_name = request.POST.get(f'company_name_{item_id}')
                wattage = request.POST.get(f'wattage_{item_id}')
                product_name = request.POST.get(f'product1_{item_id}')

                # Update the corresponding BarcodeImage record in the database if any values have changed
                try:
                    barcode_image = BarcodeImage.objects.get(pk=item_id)
                    if barcode_image.company_name != company_name:
                        print(f'Company Name updated: {barcode_image.company_name} -> {company_name}')
                        barcode_image.company_name = company_name
                    if barcode_image.wattage != wattage:
                        print(f'Wattage updated: {barcode_image.wattage} -> {wattage}')
                        barcode_image.wattage = wattage
                    # Set the previous value of product1 if it's None or blank
                    if not product_name:
                        product_name = barcode_image.product_name
                    elif barcode_image.product_name != product_name:
                        print(f'Product Name updated: {barcode_image.product_name} -> {product_name}')
                    barcode_image.product_name = product_name
                    barcode_image.save()

                    messages.success(request, f'Data updated successfully for item ID {item_id}')  # Display success message
                except BarcodeImage.DoesNotExist:
                    # Handle the case where the item is not found in the database
                    messages.error(request, 'Data update failed. Item not found.')  # Display error message

                    # Handle the case where the item is not found in the database
                    pass

            # Redirect to the same page after processing the form
            return redirect('editbarcode')  # Replace 'editbarcode' with your actual view name

        if selected_product == 'All':
            items = BarcodeImage.objects.filter(company=selected_company)
            solar_items = items.filter(product_name='SolarPanel')
            inverter_items = items.filter(product_name='Inverter')
            replace_items = items.filter(product_name='Replace')
            solar_panel_total_quantity = solar_items.count()
            solar_panel_quantity_by_wattage = solar_items.values('wattage').annotate(total_quantity=Count('id'))
            inverter_panel_total_quantity = inverter_items.count()
            inverter_panel_quantity_by_wattage = inverter_items.values('wattage').annotate(total_quantity=Count('id'))
            replace_panel_total_quantity = replace_items.count()
            replace_panel_quantity_by_wattage = replace_items.values('wattage').annotate(total_quantity=Count('id'))
        elif selected_product == 'SolarPanel':
            items = BarcodeImage.objects.filter(company=selected_company)
            solar_items = items.filter(product_name='SolarPanel')
            solar_panel_total_quantity = solar_items.count()
            solar_panel_quantity_by_wattage = solar_items.values('wattage').annotate(total_quantity=Count('id'))
        elif selected_product == 'Inverter':
            items = BarcodeImage.objects.filter(company=selected_company)
            inverter_items = items.filter(product_name='Inverter')
            inverter_panel_total_quantity = inverter_items.count()
            inverter_panel_quantity_by_wattage = inverter_items.values('wattage').annotate(total_quantity=Count('id'))
        else:
            items = BarcodeImage.objects.filter(company=selected_company)
            replace_items = items.filter(product_name='Replace')
            replace_panel_total_quantity = replace_items.count()
            replace_panel_quantity_by_wattage = replace_items.values('wattage').annotate(total_quantity=Count('id'))

        unique_wattages = {item['wattage'] for item in solar_panel_quantity_by_wattage}
        inverter_wattages = {item['wattage'] for item in inverter_panel_quantity_by_wattage}
        replace_wattages = {item['wattage'] for item in replace_panel_quantity_by_wattage}
    return render(request, 'detect_barcodes/edit_barcode.html',
                  {'companies': companies, 'product_names': product_names, 'items': items,
                   'solar_items': solar_items, 'inverter_items': inverter_items, 'replace_items': replace_items,
                   'solar_panel_total_quantity': solar_panel_total_quantity, 'solar_panel_quantity_by_wattage': solar_panel_quantity_by_wattage,
                   'unique_wattages': unique_wattages, 'inverter_wattages': inverter_wattages,
                   'inverter_panel_total_quantity': inverter_panel_total_quantity,
                   'inverter_panel_quantity_by_wattage': inverter_panel_quantity_by_wattage, 'items1': items1,

                   'replace_panel_total_quantity': replace_panel_total_quantity,
                   'replace_panel_quantity_by_wattage': replace_panel_quantity_by_wattage,
                   'replace_wattages': replace_wattages,

                   'notification1': notification1, 'count1': count1})


# @login_required(login_url='user-login')
# def displayproduct(request):
#     count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#     notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#     companies = BarcodeImage.objects.values_list('company', flat=True).distinct()
#     product_names = BarcodeImage.objects.values_list('product_name', flat=True).distinct()
#     items1 = BarcodeImage.objects.all()
#     items = []
#     solar_items = []
#     inverter_items = []
#     replace_items = []
#     solar_panel_total_quantity = 0
#     solar_panel_quantity_by_wattage = []
#     unique_wattages = []
#     inverter_wattages = []
#     inverter_panel_quantity_by_wattage = []
#     inverter_panel_total_quantity = 0
#     replace_wattages = []
#     replace_panel_quantity_by_wattage = []
#     replace_panel_total_quantity = 0
#     user_record = Customer.objects.get(new_customer_id=request.user.id)
#
#
#
#     if request.method == 'POST':
#         # selected_company = request.POST.get('company')

#         selected_company = user_record.Comp_name
#         selected_product = request.POST.get('product')
#
#         items = BarcodeImage.objects.filter(company=selected_company)
#         solar_items = items.filter(product_name='SolarPanel')
#         inverter_items = items.filter(product_name='Inverter')
#         replace_items = items.filter(product_name='Replace')
#         solar_panel_total_quantity = solar_items.count()
#         solar_panel_quantity_by_wattage = solar_items.values('wattage').annotate(total_quantity=Count('id'))
#         inverter_panel_total_quantity = inverter_items.count()
#         inverter_panel_quantity_by_wattage = inverter_items.values('wattage').annotate(total_quantity=Count('id'))
#         replace_panel_total_quantity = replace_items.count()
#         replace_panel_quantity_by_wattage = replace_items.values('wattage').annotate(total_quantity=Count('id'))
#
#         # Check if the form was submitted with edited values
#         if 'selected_items' in request.POST:
#             for item_id in request.POST.getlist('selected_items'):
#                 # Get the edited values from the form
#                 company_name = request.POST.get(f'company_name_{item_id}')
#                 wattage = request.POST.get(f'wattage_{item_id}')
#                 product_name = request.POST.get(f'product1_{item_id}')
#
#                 # # Update the corresponding BarcodeImage record in the database if any values have changed
#                 # try:
#                 #     barcode_image = BarcodeImage.objects.get(pk=item_id)
#                 #     if barcode_image.company_name != company_name:
#                 #         print(f'Company Name updated: {barcode_image.company_name} -> {company_name}')
#                 #         barcode_image.company_name = company_name
#                 #     if barcode_image.wattage != wattage:
#                 #         print(f'Wattage updated: {barcode_image.wattage} -> {wattage}')
#                 #         barcode_image.wattage = wattage
#                 #     # Set the previous value of product1 if it's None or blank
#                 #     if not product_name:
#                 #         product_name = barcode_image.product_name
#                 #     elif barcode_image.product_name != product_name:
#                 #         print(f'Product Name updated: {barcode_image.product_name} -> {product_name}')
#                 #     barcode_image.product_name = product_name
#                 #     barcode_image.save()
#                 #
#                 #     messages.success(request, f'Data updated successfully for item ID {item_id}')  # Display success message
#                 # except BarcodeImage.DoesNotExist:
#                 #     # Handle the case where the item is not found in the database
#                 #     messages.error(request, 'Data update failed. Item not found.')  # Display error message
#                 #
#                 #     # Handle the case where the item is not found in the database
#                 #     pass
#
#             # Redirect to the same page after processing the form
#             return redirect('displayproduct')  # Replace 'editbarcode' with your actual view name
#
#         if selected_product == 'All':
#             items = BarcodeImage.objects.filter(company=selected_company)
#             solar_items = items.filter(product_name='SolarPanel')
#             inverter_items = items.filter(product_name='Inverter')
#             replace_items = items.filter(product_name='Replace')
#             solar_panel_total_quantity = solar_items.count()
#             solar_panel_quantity_by_wattage = solar_items.values('wattage').annotate(total_quantity=Count('id'))
#             inverter_panel_total_quantity = inverter_items.count()
#             inverter_panel_quantity_by_wattage = inverter_items.values('wattage').annotate(total_quantity=Count('id'))
#             replace_panel_total_quantity = replace_items.count()
#             replace_panel_quantity_by_wattage = replace_items.values('wattage').annotate(total_quantity=Count('id'))
#         elif selected_product == 'SolarPanel':
#             items = BarcodeImage.objects.filter(company=selected_company)
#             solar_items = items.filter(product_name='SolarPanel')
#             solar_panel_total_quantity = solar_items.count()
#             solar_panel_quantity_by_wattage = solar_items.values('wattage').annotate(total_quantity=Count('id'))
#         elif selected_product == 'Inverter':
#             items = BarcodeImage.objects.filter(company=selected_company)
#             inverter_items = items.filter(product_name='Inverter')
#             inverter_panel_total_quantity = inverter_items.count()
#             inverter_panel_quantity_by_wattage = inverter_items.values('wattage').annotate(total_quantity=Count('id'))
#         else:
#             items = BarcodeImage.objects.filter(company=selected_company)
#             replace_items = items.filter(product_name='Replace')
#             replace_panel_total_quantity = replace_items.count()
#             replace_panel_quantity_by_wattage = replace_items.values('wattage').annotate(total_quantity=Count('id'))
#
#         unique_wattages = {item['wattage'] for item in solar_panel_quantity_by_wattage}
#         inverter_wattages = {item['wattage'] for item in inverter_panel_quantity_by_wattage}
#         replace_wattages = {item['wattage'] for item in replace_panel_quantity_by_wattage}
#     return render(request, 'detect_barcodes/display_product.html',
#                   {'companies': companies, 'product_names': product_names, 'items': items,
#                    'solar_items': solar_items, 'inverter_items': inverter_items, 'replace_items': replace_items,
#                    'solar_panel_total_quantity': solar_panel_total_quantity, 'solar_panel_quantity_by_wattage': solar_panel_quantity_by_wattage,
#                    'unique_wattages': unique_wattages, 'inverter_wattages': inverter_wattages,
#                    'inverter_panel_total_quantity': inverter_panel_total_quantity,
#                    'inverter_panel_quantity_by_wattage': inverter_panel_quantity_by_wattage, 'items1': items1,
#                    'replace_panel_total_quantity': replace_panel_total_quantity,
#                    'replace_panel_quantity_by_wattage': replace_panel_quantity_by_wattage,
#                    'replace_wattages': replace_wattages,
#                    'notification1': notification1, 'count1': count1, 'user_record': user_record,})




@login_required(login_url='user-login')
def displayproduct(request):
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    companies = BarcodeImage.objects.values_list('company', flat=True).distinct()
    product_names = BarcodeImage.objects.values_list('product_name', flat=True).distinct()
    items1 = BarcodeImage.objects.all()
    items = []
    solar_items = []
    inverter_items = []
    replace_items = []
    solar_panel_total_quantity = 0
    solar_panel_quantity_by_wattage = []
    unique_wattages = []
    inverter_wattages = []
    inverter_panel_quantity_by_wattage = []
    inverter_panel_total_quantity = 0
    replace_wattages = []
    replace_panel_quantity_by_wattage = []
    replace_panel_total_quantity = 0
    user_record = Customer.objects.get(new_customer_id=request.user.id)

    if request.method == 'POST':

        selected_company = user_record.Comp_name
        # selected_company = request.POST.get('company')
        selected_product = request.POST.get('product')

        # Check if the form was submitted with edited values
        if 'selected_items' in request.POST:
            for item_id in request.POST.getlist('selected_items'):
                # Get the edited values from the form
                company_name = request.POST.get(f'company_name_{item_id}')
                wattage = request.POST.get(f'wattage_{item_id}')
                product_name = request.POST.get(f'product1_{item_id}')

                # Update the corresponding BarcodeImage record in the database if any values have changed
                try:
                    barcode_image = BarcodeImage.objects.get(pk=item_id)
                    if barcode_image.company_name != company_name:
                        print(f'Company Name updated: {barcode_image.company_name} -> {company_name}')
                        barcode_image.company_name = company_name
                    if barcode_image.wattage != wattage:
                        print(f'Wattage updated: {barcode_image.wattage} -> {wattage}')
                        barcode_image.wattage = wattage
                    # Set the previous value of product1 if it's None or blank
                    if not product_name:
                        product_name = barcode_image.product_name
                    elif barcode_image.product_name != product_name:
                        print(f'Product Name updated: {barcode_image.product_name} -> {product_name}')
                    barcode_image.product_name = product_name
                    barcode_image.save()

                    messages.success(request, f'Data updated successfully for item ID {item_id}')  # Display success message
                except BarcodeImage.DoesNotExist:
                    # Handle the case where the item is not found in the database
                    messages.error(request, 'Data update failed. Item not found.')  # Display error message

                    # Handle the case where the item is not found in the database
                    pass

            # Redirect to the same page after processing the form
            return redirect('displayproduct')  # Replace 'editbarcode' with your actual view name

        if selected_product == 'All':
            items = BarcodeImage.objects.filter(company=selected_company)
            solar_items = items.filter(product_name='SolarPanel')
            inverter_items = items.filter(product_name='Inverter')
            replace_items = items.filter(product_name='Replace')
            solar_panel_total_quantity = solar_items.count()
            solar_panel_quantity_by_wattage = solar_items.values('wattage').annotate(total_quantity=Count('id'))
            inverter_panel_total_quantity = inverter_items.count()
            inverter_panel_quantity_by_wattage = inverter_items.values('wattage').annotate(total_quantity=Count('id'))
            replace_panel_total_quantity = replace_items.count()
            replace_panel_quantity_by_wattage = replace_items.values('wattage').annotate(total_quantity=Count('id'))
        elif selected_product == 'SolarPanel':
            items = BarcodeImage.objects.filter(company=selected_company)
            solar_items = items.filter(product_name='SolarPanel')
            solar_panel_total_quantity = solar_items.count()
            solar_panel_quantity_by_wattage = solar_items.values('wattage').annotate(total_quantity=Count('id'))
        elif selected_product == 'Inverter':
            items = BarcodeImage.objects.filter(company=selected_company)
            inverter_items = items.filter(product_name='Inverter')
            inverter_panel_total_quantity = inverter_items.count()
            inverter_panel_quantity_by_wattage = inverter_items.values('wattage').annotate(total_quantity=Count('id'))
        else:
            items = BarcodeImage.objects.filter(company=selected_company)
            replace_items = items.filter(product_name='Replace')
            replace_panel_total_quantity = replace_items.count()
            replace_panel_quantity_by_wattage = replace_items.values('wattage').annotate(total_quantity=Count('id'))

        unique_wattages = {item['wattage'] for item in solar_panel_quantity_by_wattage}
        inverter_wattages = {item['wattage'] for item in inverter_panel_quantity_by_wattage}
        replace_wattages = {item['wattage'] for item in replace_panel_quantity_by_wattage}
    return render(request, 'detect_barcodes/display_product.html',
                  {'companies': companies, 'product_names': product_names, 'items': items,
                   'solar_items': solar_items, 'inverter_items': inverter_items, 'replace_items': replace_items,
                   'solar_panel_total_quantity': solar_panel_total_quantity, 'solar_panel_quantity_by_wattage': solar_panel_quantity_by_wattage,
                   'unique_wattages': unique_wattages, 'inverter_wattages': inverter_wattages,
                   'inverter_panel_total_quantity': inverter_panel_total_quantity,
                   'inverter_panel_quantity_by_wattage': inverter_panel_quantity_by_wattage, 'items1': items1,
                   'replace_panel_total_quantity': replace_panel_total_quantity,
                   'replace_panel_quantity_by_wattage': replace_panel_quantity_by_wattage,
                   'replace_wattages': replace_wattages,
                   'notification1': notification1, 'count1': count1, 'user_record': user_record})




from django.shortcuts import render, redirect
from django.db.models import Count
from .models import BarcodeImage  # Import your BarcodeImage model

from django.shortcuts import render, redirect
from django.db.models import Count
from .models import BarcodeImage  # Import your BarcodeImage model

#
# def editbarcode(request):
#     count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#     notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#     companies = BarcodeImage.objects.values_list('company', flat=True).distinct()
#     product_names = BarcodeImage.objects.values_list('product_name', flat=True).distinct()
#     items1 = BarcodeImage.objects.all()
#     items = []
#     solar_items = []
#     inverter_items = []
#     solar_panel_total_quantity = 0
#     solar_panel_quantity_by_wattage = []
#     unique_wattages = []
#     inverter_wattages = []
#     inverter_panel_quantity_by_wattage = []
#     inverter_panel_total_quantity = 0
#
#     if request.method == 'POST':
#         selected_company = request.POST.get('company')
#         selected_product = request.POST.get('product')
#
#         # Check if the form was submitted with edited values
#         if 'selected_items' in request.POST:
#             selected_item_ids = request.POST.getlist('selected_items')
#
#             for item_id in selected_item_ids:
#                 # Get the edited values from the form
#                 company_name = request.POST.get(f'company_name_{item_id}')
#                 wattage = request.POST.get(f'wattage_{item_id}')
#                 product_name = request.POST.get(f'product_name_{item_id}')
#
#                 # Update the corresponding BarcodeImage record in the database
#                 try:
#                     barcode_image = BarcodeImage.objects.get(pk=item_id)
#                     if barcode_image.company_name != company_name:
#                         print(f'Company Name updated: {barcode_image.company_name} -> {company_name}')
#                         barcode_image.company_name = company_name
#                     if barcode_image.wattage != wattage:
#                         print(f'Wattage updated: {barcode_image.wattage} -> {wattage}')
#                         barcode_image.wattage = wattage
#                     if barcode_image.product_name != product_name:
#                         print(f'Product Name updated: {barcode_image.product_name} -> {product_name}')
#                         barcode_image.product_name = product_name
#                     barcode_image.save()
#                 except BarcodeImage.DoesNotExist:
#                     # Handle the case where the item is not found in the database
#                     pass
#
#             # Redirect to the same page after processing the form
#             return redirect('editbarcode')  # Replace 'editbarcode' with your actual view name
#
#         if selected_product == 'All':
#             items = BarcodeImage.objects.filter(company=selected_company)
#             solar_items = items.filter(product_name='SolarPanel')
#             inverter_items = items.filter(product_name='Inverter')
#             solar_panel_total_quantity = solar_items.count()
#             solar_panel_quantity_by_wattage = solar_items.values('wattage').annotate(total_quantity=Count('id'))
#             inverter_panel_total_quantity = inverter_items.count()
#             inverter_panel_quantity_by_wattage = inverter_items.values('wattage').annotate(total_quantity=Count('id'))
#         elif selected_product == 'SolarPanel':
#             items = BarcodeImage.objects.filter(company=selected_company)
#             solar_items = items.filter(product_name='SolarPanel')
#             solar_panel_total_quantity = solar_items.count()
#             solar_panel_quantity_by_wattage = solar_items.values('wattage').annotate(total_quantity=Count('id'))
#         else:
#             items = BarcodeImage.objects.filter(company=selected_company)
#             inverter_items = items.filter(product_name='Inverter')
#             inverter_panel_total_quantity = inverter_items.count()
#             inverter_panel_quantity_by_wattage = inverter_items.values('wattage').annotate(total_quantity=Count('id'))
#
#     return render(request, 'detect_barcodes/edit_barcode.html',
#                   {'companies': companies, 'product_names': product_names, 'items': items,
#                    'solar_items': solar_items, 'inverter_items': inverter_items,
#                    'solar_panel_total_quantity': solar_panel_total_quantity,
#                    'solar_panel_quantity_by_wattage': solar_panel_quantity_by_wattage,
#                    'unique_wattages': unique_wattages, 'inverter_wattages': inverter_wattages,
#                    'inverter_panel_total_quantity': inverter_panel_total_quantity,
#                    'inverter_panel_quantity_by_wattage': inverter_panel_quantity_by_wattage, 'items1': items1,
#                    'notification1': notification1, 'count1': count1})


# class GeneratePDF(View):
#     template_path = 'detect_barcodes/pdf_template.html'
#
#     def get(self, request, *args, **kwargs):
#         template = get_template(self.template_path)
#         context = {
#             'solar_items': BarcodeImage.objects.filter(product_name='SolarPanel'),
#             'inverter_items': BarcodeImage.objects.filter(product_name='Inverter'),
#         }
#         html = template.render(context)
#         pdf_file = BytesIO()
#
#         pisa_status = pisa.CreatePDF(smart_str(html), dest=pdf_file)
#         if pisa_status.err:
#             return HttpResponse('PDF generation failed', content_type='text/plain')
#
#         response = HttpResponse(pdf_file.getvalue(), content_type='application/pdf')
#         response['Content-Disposition'] = 'attachment; filename="barcode_items.pdf"'
#         return response



# def upload_barcode(request):
#     return render(request, 'detect_barcodes/detect_barcodes1.html')
#
# def detect_barcodes(file_path):
#     image = Image.open(file_path)
#     decoded_barcodes = decode(image)
#     return [barcode.data.decode('utf-8') for barcode in decoded_barcodes]
#
# def ajax_handle_upload(request):
#     if request.method == 'POST' and request.FILES['file']:
#         uploaded_file = request.FILES['file']
#         fs = FileSystemStorage()
#         filename = fs.save(uploaded_file.name, uploaded_file)
#         file_path = fs.url(filename)
#
#         # Process the uploaded file and detect barcodes
#         barcodes = detect_barcodes(file_path)
#         for code in barcodes:
#             barcode_image = BarcodeImage.objects.create(
#                 image=code,
#                 # barcode_type=barcode_type,
#                 # company=company_name,  # Save the company value
#                 # wattage=wattage,  # Save the wattage value
#                 # file_saved_at=file_saved_at,
#                 # image=image,
#                 # AssignTo=assign_to_user,
#                 # AssignBy=request.user.id,
#                 # company_name=company,  # Save the value of the dynamically changing textbox
#                 # product_name=product_name  # Set the product_name
#             )
#
#             # Barcode.objects.create(code=code)
#
#         return JsonResponse({'success': True, 'barcode_image': barcode_image})
#
#     return JsonResponse({'success': False})


# import os
# from io import BytesIO
#
# from django.shortcuts import render, redirect
# from django.core.files.storage import FileSystemStorage
# from django.http import JsonResponse
# from PyPDF2 import PdfReader
# from pyzbar.pyzbar import decode
# from PIL import Image
# from datetime import datetime
# from .models import BarcodeImage
#
# def upload_barcode(request):
#     return render(request, 'detect_barcodes/detect_barcodes1.html')
#
# def detect_barcodes(file_path):
#     _, file_extension = os.path.splitext(file_path)
#     if file_extension.lower() == '.pdf':
#         return detect_barcodes_from_pdf(file_path)
#     else:
#         return detect_barcodes_from_image(file_path)
#
# def detect_barcodes_from_image(file_path):
#     image = Image.open(file_path)
#     decoded_barcodes = decode(image)
#     return [barcode.data.decode('utf-8') for barcode in decoded_barcodes]
#
# def detect_barcodes_from_pdf(file_path):
#     barcodes = []
#     pdf_reader = PdfReader(file_path)
#     for page in pdf_reader.pages:
#         xObject = page['/Resources']['/XObject'].get_object()
#         for obj in xObject:
#             if xObject[obj]['/Subtype'] == '/Image':
#                 size = (xObject[obj]['/Width'], xObject[obj]['/Height'])
#                 data = xObject[obj].get_object()
#                 if data.get('/Filter') == '/DCTDecode':  # JPEG image
#                     image_data = data.get_object().get_data()
#                 else:
#                     image_data = data.get_object().get_object().get_data()
#
#                 image = Image.open(BytesIO(image_data))
#                 decoded_barcodes = decode(image)
#                 barcodes.extend([barcode.data.decode('utf-8') for barcode in decoded_barcodes])
#     return barcodes
#
# def ajax_handle_upload(request):
#     if request.method == 'POST' and request.FILES['file']:
#         uploaded_file = request.FILES['file']
#         fs = FileSystemStorage()
#         filename = fs.save(uploaded_file.name, uploaded_file)
#         file_path = fs.path(filename)  # Use fs.path() instead of fs.url()
#
#         # Set the file_saved_at field to the current datetime
#         file_saved_at = datetime.now()
#
#         # Process the uploaded file and detect barcodes
#         barcodes = detect_barcodes(file_path)
#         for code in barcodes:
#             BarcodeImage.objects.create(barcode_data=code, file_saved_at=file_saved_at,
#                                         image=uploaded_file, barcode_path=file_path)
#
#         return JsonResponse({'success': True, 'barcodes': barcodes})
#
#     return JsonResponse({'success': False})

import os
from io import BytesIO

from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from PyPDF2 import PdfReader
from pyzbar.pyzbar import decode
from PIL import Image

from .models import BarcodeImage

@login_required(login_url='user-login')
def upload_barcode(request):
    return render(request, 'detect_barcodes/detect_barcodes1.html')

@login_required(login_url='user-login')
def detect_barcodes(file_path):
    _, file_extension = os.path.splitext(file_path)
    if file_extension.lower() == '.pdf':
        return detect_barcodes_from_pdf(file_path)
    else:
        return detect_barcodes_from_image(file_path)

@login_required(login_url='user-login')
def detect_barcodes_from_image(file_path):
    image = Image.open(file_path)
    decoded_barcodes = decode(image)
    return [barcode.data.decode('utf-8') for barcode in decoded_barcodes]

@login_required(login_url='user-login')
def detect_barcodes_from_pdf(file_path):
    barcodes = []
    pdf_reader = PdfReader(file_path)
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        xObject = page['/Resources']['/XObject'].get_object()
        for obj in xObject:
            if xObject[obj]['/Subtype'] == '/Image':
                size = (xObject[obj]['/Width'], xObject[obj]['/Height'])
                data = xObject[obj].get_object()
                if data.get('/Filter') == '/DCTDecode':  # JPEG image
                    image_data = data.get_object().get_data()
                else:
                    image_data = data.get_object().get_object().get_data()

                image = Image.open(BytesIO(image_data))
                decoded_barcodes = decode(image)
                barcodes.extend([barcode.data.decode('utf-8') for barcode in decoded_barcodes])
    return barcodes

@login_required(login_url='user-login')
def ajax_handle_upload(request):
    if request.method == 'POST' and request.FILES['file']:
        uploaded_file = request.FILES['file']
        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        file_path = fs.path(filename)  # Use fs.path() instead of fs.url()

        # Set the file_saved_at field to the current datetime
        file_saved_at = datetime.now()

        # Process the uploaded file and detect barcodes
        barcodes = detect_barcodes(file_path)
        for code in barcodes:
            BarcodeImage.objects.create(barcode_data=code, file_saved_at=file_saved_at,
                                        image=uploaded_file, barcode_path=file_path)

        return JsonResponse({'success': True, 'barcodes': barcodes})

    return JsonResponse({'success': False})

#
# @login_required(login_url='user-login')
# def deletebarcode(request):
#     count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#     notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#     companies = BarcodeImage.objects.values_list('company', flat=True).distinct()
#     product_names = BarcodeImage.objects.values_list('product_name', flat=True).distinct()
#     items1 = BarcodeImage.objects.all()
#     items = []
#     solar_items = []
#     inverter_items = []
#     replace_items = []
#     solar_panel_total_quantity = 0
#     solar_panel_quantity_by_wattage = []
#     unique_wattages = []
#     inverter_wattages = []
#     inverter_panel_quantity_by_wattage = []
#     inverter_panel_total_quantity = 0
#     replace_wattages = []
#     replace_panel_quantity_by_wattage = []
#     replace_panel_total_quantity = 0
#     selected_product = []
#     selected_company = []
#
#     if request.method == 'POST':
#         selected_company = request.POST.get('company')
#         selected_product = request.POST.get('product')
#
#         # Check if the form was submitted with edited values
#         if 'selected_items' in request.POST:
#             for item_id in request.POST.getlist('selected_items'):
#                 # Get the edited values from the form
#                 company_name = request.POST.get(f'company_name_{item_id}')
#                 wattage = request.POST.get(f'wattage_{item_id}')
#                 product_name = request.POST.get(f'product1_{item_id}')
#
#                 # Update the corresponding BarcodeImage record in the database if any values have changed
#                 # try:
#                 #     barcode_image = BarcodeImage.objects.get(pk=item_id)
#                     # if barcode_image.company_name != company_name:
#                     #     print(f'Company Name updated: {barcode_image.company_name} -> {company_name}')
#                     #     barcode_image.company_name = company_name
#                     # if barcode_image.wattage != wattage:
#                     #     print(f'Wattage updated: {barcode_image.wattage} -> {wattage}')
#                     #     barcode_image.wattage = wattage
#                     # # Set the previous value of product1 if it's None or blank
#                     # if not product_name:
#                     #     product_name = barcode_image.product_name
#                     # elif barcode_image.product_name != product_name:
#                     #     print(f'Product Name updated: {barcode_image.product_name} -> {product_name}')
#                     # barcode_image.product_name = product_name
#                     # barcode_image.save()
#
#                 #     messages.success(request, 'Data updated successfully')  # Display success message
#                 # except BarcodeImage.DoesNotExist:
#                 #     # Handle the case where the item is not found in the database
#                 #     messages.error(request, 'Data update failed. Item not found.')  # Display error message
#                 #
#                 #     # Handle the case where the item is not found in the database
#                 #     pass
#                 selected_item_ids = request.POST.getlist('selected_items')
#                 selected_items = BarcodeImage.objects.filter(pk__in=selected_item_ids)
#                 return render(request, 'detect_barcodes/selected_records.html', {'selected_items': selected_items})
#         #     # Redirect to the same page after processing the form
#         # return redirect('deletebarcode')  # Replace 'editbarcode' with your actual view name
#
#         if 'confirm_delete' in request.POST:
#                         # Get selected item IDs
#                         selected_item_ids = request.POST.getlist('selected_items')
#
#                         # Fetch selected items from the database
#                         selected_items = BarcodeImage.objects.filter(pk__in=selected_item_ids)
#
#                         # Delete the selected items from the database
#                         selected_items.delete()
#
#                         # Remove related images from the folder
#                         for item in selected_items:
#                             # Construct the path to the image file (change it based on your folder structure)
#                             image = os.path.join(settings.MEDIA_ROOT, item.image.name)
#
#
#                             # Check if the file exists and delete it
#                             if os.path.exists(image):
#                                 os.remove(image)
#
#                         messages.success(request, 'Selected records deleted successfully and related images removed.')
#         # return render(request, 'detect_barcodes/delete_barcodes.html')
#             #             # Redirect to the same page after processing the form
#             #             return redirect('deletebarcode')
#             #
#
#
#     # if request.method == 'POST':
#     #         selected_company = request.POST.get('company')
#     #         selected_product = request.POST.get('product')
#     #         selected_item_ids = request.POST.getlist('selected_items')
#     #         selected_items = BarcodeImage.objects.filter(pk__in=selected_item_ids)
#     #         return render(request, 'detect_barcodes/selected_records.html', {'selected_items': selected_items})
#
#     if selected_product == 'All':
#             items = BarcodeImage.objects.filter(company=selected_company)
#             solar_items = items.filter(product_name='SolarPanel')
#             inverter_items = items.filter(product_name='Inverter')
#             replace_items = items.filter(product_name='Replace')
#             solar_panel_total_quantity = solar_items.count()
#             solar_panel_quantity_by_wattage = solar_items.values('wattage').annotate(total_quantity=Count('id'))
#             inverter_panel_total_quantity = inverter_items.count()
#             inverter_panel_quantity_by_wattage = inverter_items.values('wattage').annotate(total_quantity=Count('id'))
#             replace_panel_total_quantity = replace_items.count()
#             replace_panel_quantity_by_wattage = replace_items.values('wattage').annotate(total_quantity=Count('id'))
#     elif selected_product == 'SolarPanel':
#             items = BarcodeImage.objects.filter(company=selected_company)
#             solar_items = items.filter(product_name='SolarPanel')
#             solar_panel_total_quantity = solar_items.count()
#             solar_panel_quantity_by_wattage = solar_items.values('wattage').annotate(total_quantity=Count('id'))
#     elif selected_product == 'Inverter':
#             items = BarcodeImage.objects.filter(company=selected_company)
#             inverter_items = items.filter(product_name='Inverter')
#             inverter_panel_total_quantity = inverter_items.count()
#             inverter_panel_quantity_by_wattage = inverter_items.values('wattage').annotate(total_quantity=Count('id'))
#     else:
#             items = BarcodeImage.objects.filter(company=selected_company)
#             replace_items = items.filter(product_name='Replace')
#             replace_panel_total_quantity = replace_items.count()
#             replace_panel_quantity_by_wattage = replace_items.values('wattage').annotate(total_quantity=Count('id'))
#
#             unique_wattages = {item['wattage'] for item in solar_panel_quantity_by_wattage}
#             inverter_wattages = {item['wattage'] for item in inverter_panel_quantity_by_wattage}
#             replace_wattages = {item['wattage'] for item in replace_panel_quantity_by_wattage}
#     return render(request, 'detect_barcodes/delete_barcode.html',
#                       {'companies': companies, 'product_names': product_names, 'items': items,
#                    'solar_items': solar_items, 'inverter_items': inverter_items, 'replace_items': replace_items,
#                    'solar_panel_total_quantity': solar_panel_total_quantity, 'solar_panel_quantity_by_wattage': solar_panel_quantity_by_wattage,
#                    'unique_wattages': unique_wattages, 'inverter_wattages': inverter_wattages,
#                    'inverter_panel_total_quantity': inverter_panel_total_quantity,
#                    'inverter_panel_quantity_by_wattage': inverter_panel_quantity_by_wattage, 'items1': items1,
#
#                    'replace_panel_total_quantity': replace_panel_total_quantity,
#                    'replace_panel_quantity_by_wattage': replace_panel_quantity_by_wattage,
#                    'replace_wattages': replace_wattages,
#
#                    'notification1': notification1, 'count1': count1})




# @login_required(login_url='user-login')
# def deletebarcode(request):
#     count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#     notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#     companies = BarcodeImage.objects.values_list('company', flat=True).distinct()
#     product_names = BarcodeImage.objects.values_list('product_name', flat=True).distinct()
#     items1 = BarcodeImage.objects.all()
#     items = []
#     solar_items = []
#     inverter_items = []
#     replace_items = []
#     solar_panel_total_quantity = 0
#     solar_panel_quantity_by_wattage = []
#     unique_wattages = []
#     inverter_wattages = []
#     inverter_panel_quantity_by_wattage = []
#     inverter_panel_total_quantity = 0
#     replace_wattages = []
#     replace_panel_quantity_by_wattage = []
#     replace_panel_total_quantity = 0
#     selected_product = []
#     selected_company = []
#
#     if request.method == 'POST':
#         selected_company = request.POST.get('company')
#         selected_product = request.POST.get('product')
#
#         if 'selected_items' in request.POST:
#             selected_item_ids = request.POST.getlist('selected_items')
#             selected_items = BarcodeImage.objects.filter(pk__in=selected_item_ids)
#             return render(request, 'detect_barcodes/selected_records.html', {'selected_items': selected_items})
#
#         if 'confirm_delete' in request.POST:
#             selected_item_ids = request.POST.getlist('selected_items')
#             selected_items = BarcodeImage.objects.filter(pk__in=selected_item_ids)
#             selected_items.delete()
#
#             for item in selected_items:
#                 image = os.path.join(settings.MEDIA_ROOT, item.image.name)
#
#                 if os.path.exists(image):
#                     os.remove(image)
#
#             messages.success(request, 'Selected records deleted successfully and related images removed.')
#             return redirect('deletebarcode')  # Redirect back to the deletebarcode page after deletion.
#
#     if selected_product == 'All':
#         items = BarcodeImage.objects.filter(company=selected_company)
#         solar_items = items.filter(product_name='SolarPanel')
#         inverter_items = items.filter(product_name='Inverter')
#         replace_items = items.filter(product_name='Replace')
#         solar_panel_total_quantity = solar_items.count()
#         solar_panel_quantity_by_wattage = solar_items.values('wattage').annotate(total_quantity=Count('id'))
#         inverter_panel_total_quantity = inverter_items.count()
#         inverter_panel_quantity_by_wattage = inverter_items.values('wattage').annotate(total_quantity=Count('id'))
#         replace_panel_total_quantity = replace_items.count()
#         replace_panel_quantity_by_wattage = replace_items.values('wattage').annotate(total_quantity=Count('id'))
#     elif selected_product == 'SolarPanel':
#         items = BarcodeImage.objects.filter(company=selected_company)
#         solar_items = items.filter(product_name='SolarPanel')
#         solar_panel_total_quantity = solar_items.count()
#         solar_panel_quantity_by_wattage = solar_items.values('wattage').annotate(total_quantity=Count('id'))
#     elif selected_product == 'Inverter':
#         items = BarcodeImage.objects.filter(company=selected_company)
#         inverter_items = items.filter(product_name='Inverter')
#         inverter_panel_total_quantity = inverter_items.count()
#         inverter_panel_quantity_by_wattage = inverter_items.values('wattage').annotate(total_quantity=Count('id'))
#     else:
#         items = BarcodeImage.objects.filter(company=selected_company)
#         replace_items = items.filter(product_name='Replace')
#         replace_panel_total_quantity = replace_items.count()
#         replace_panel_quantity_by_wattage = replace_items.values('wattage').annotate(total_quantity=Count('id'))
#
#         unique_wattages = {item['wattage'] for item in solar_panel_quantity_by_wattage}
#         inverter_wattages = {item['wattage'] for item in inverter_panel_quantity_by_wattage}
#         replace_wattages = {item['wattage'] for item in replace_panel_quantity_by_wattage}
#
#     return render(request, 'detect_barcodes/delete_barcode.html', {
#         'companies': companies,
#         'product_names': product_names,
#         'items': items,
#         'solar_items': solar_items,
#         'inverter_items': inverter_items,
#         'replace_items': replace_items,
#         'solar_panel_total_quantity': solar_panel_total_quantity,
#         'solar_panel_quantity_by_wattage': solar_panel_quantity_by_wattage,
#         'unique_wattages': unique_wattages,
#         'inverter_wattages': inverter_wattages,
#         'inverter_panel_total_quantity': inverter_panel_total_quantity,
#         'inverter_panel_quantity_by_wattage': inverter_panel_quantity_by_wattage,
#         'items1': items1,
#         'replace_panel_total_quantity': replace_panel_total_quantity,
#         'replace_panel_quantity_by_wattage': replace_panel_quantity_by_wattage,
#         'replace_wattages': replace_wattages,
#         'notification1': notification1,
#         'count1': count1
#     })


# @login_required(login_url='user-login')
# def deletebarcode(request):
#     count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#     notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#     companies = BarcodeImage.objects.values_list('company', flat=True).distinct()
#     product_names = BarcodeImage.objects.values_list('product_name', flat=True).distinct()
#     items1 = BarcodeImage.objects.all()
#     items = []
#     solar_items = []
#     inverter_items = []
#     replace_items = []
#     solar_panel_total_quantity = 0
#     solar_panel_quantity_by_wattage = []
#     unique_wattages = []
#     inverter_wattages = []
#     inverter_panel_quantity_by_wattage = []
#     inverter_panel_total_quantity = 0
#     replace_wattages = []
#     replace_panel_quantity_by_wattage = []
#     replace_panel_total_quantity = 0
#     selected_product = ''
#     selected_company = ''
#
#     if request.method == 'POST':
#         selected_company = request.POST.get('company')
#         selected_product = request.POST.get('product')
#
#         if 'selected_items' in request.POST:
#             selected_item_ids = request.POST.getlist('selected_items')
#             selected_items = BarcodeImage.objects.filter(pk__in=selected_item_ids)
#
#
#             # Remove related images from the folder
#             for item in selected_items:
#                 # # Construct the path to the image file (change it based on your folder structure)
#                 # image_path = os.path.join(settings.MEDIA_ROOT, item.image.name)
#                 #
#                 # # Check if the file exists and delete it
#                 # if os.path.exists(image_path):
#                 #     os.remove(image_path)
#
#                 image_path = item.image.path
#                 barcode_path = item.barcode_path.path
#
#                 # Check if the image files exist before attempting deletion
#                 if os.path.exists(image_path):
#                     os.remove(image_path)
#                     print(f"Image file exist at {image_path}")
#                 else:
#                     print(f"Image file does not exist at {image_path}")
#
#                 if os.path.exists(barcode_path):
#                     os.remove(barcode_path)
#                     print(f"Barcode file exist at {barcode_path}")
#                 else:
#                     print(f"Barcode file does not exist at {barcode_path}")
#
#                 # Delete the selected item
#                 item.delete()
#                 selected_items.delete()
#             messages.success(request, 'Selected records deleted successfully and related images removed.')
#             return redirect('deletebarcode')  # Redirect back to the deletebarcode page after deletion.
#
#     if selected_product == 'All':
#         items = BarcodeImage.objects.filter(company=selected_company)
#         solar_items = items.filter(product_name='SolarPanel')
#         inverter_items = items.filter(product_name='Inverter')
#         replace_items = items.filter(product_name='Replace')
#         solar_panel_total_quantity = solar_items.count()
#         solar_panel_quantity_by_wattage = solar_items.values('wattage').annotate(total_quantity=Count('id'))
#         inverter_panel_total_quantity = inverter_items.count()
#         inverter_panel_quantity_by_wattage = inverter_items.values('wattage').annotate(total_quantity=Count('id'))
#         replace_panel_total_quantity = replace_items.count()
#         replace_panel_quantity_by_wattage = replace_items.values('wattage').annotate(total_quantity=Count('id'))
#     elif selected_product == 'SolarPanel':
#         items = BarcodeImage.objects.filter(company=selected_company)
#         solar_items = items.filter(product_name='SolarPanel')
#         solar_panel_total_quantity = solar_items.count()
#         solar_panel_quantity_by_wattage = solar_items.values('wattage').annotate(total_quantity=Count('id'))
#     elif selected_product == 'Inverter':
#         items = BarcodeImage.objects.filter(company=selected_company)
#         inverter_items = items.filter(product_name='Inverter')
#         inverter_panel_total_quantity = inverter_items.count()
#         inverter_panel_quantity_by_wattage = inverter_items.values('wattage').annotate(total_quantity=Count('id'))
#     else:
#         items = BarcodeImage.objects.filter(company=selected_company)
#         replace_items = items.filter(product_name='Replace')
#         replace_panel_total_quantity = replace_items.count()
#         replace_panel_quantity_by_wattage = replace_items.values('wattage').annotate(total_quantity=Count('id'))
#
#         unique_wattages = {item['wattage'] for item in solar_panel_quantity_by_wattage}
#         inverter_wattages = {item['wattage'] for item in inverter_panel_quantity_by_wattage}
#         replace_wattages = {item['wattage'] for item in replace_panel_quantity_by_wattage}
#
#     return render(request, 'detect_barcodes/delete_barcode.html', {
#         'companies': companies,
#         'product_names': product_names,
#         'items': items,
#         'solar_items': solar_items,
#         'inverter_items': inverter_items,
#         'replace_items': replace_items,
#         'solar_panel_total_quantity': solar_panel_total_quantity,
#         'solar_panel_quantity_by_wattage': solar_panel_quantity_by_wattage,
#         'unique_wattages': unique_wattages,
#         'inverter_wattages': inverter_wattages,
#         'inverter_panel_total_quantity': inverter_panel_total_quantity,
#         'inverter_panel_quantity_by_wattage': inverter_panel_quantity_by_wattage,
#         'items1': items1,
#         'replace_panel_total_quantity': replace_panel_total_quantity,
#         'replace_panel_quantity_by_wattage': replace_panel_quantity_by_wattage,
#         'replace_wattages': replace_wattages,
#         'notification1': notification1,
#         'count1': count1,
#         'selected_product': selected_product,
#         'selected_company': selected_company,
#     })


def deletebarcode(request):
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    companies = BarcodeImage.objects.values_list('company', flat=True).distinct()
    product_names = BarcodeImage.objects.values_list('product_name', flat=True).distinct()
    items1 = BarcodeImage.objects.all()
    items = []
    solar_items = []
    inverter_items = []
    replace_items = []
    solar_panel_total_quantity = 0
    solar_panel_quantity_by_wattage = []
    unique_wattages = []
    inverter_wattages = []
    inverter_panel_quantity_by_wattage = []
    inverter_panel_total_quantity = 0
    replace_wattages = []
    replace_panel_quantity_by_wattage = []
    replace_panel_total_quantity = 0
    selected_product = []
    selected_company = []

    # if request.method == 'POST':
    #     selected_company = request.POST.get('company')
    #     selected_product = request.POST.get('product')
    #
    #     if 'selected_items' in request.POST:
    #         selected_item_ids = request.POST.getlist('selected_items')
    #         selected_items = BarcodeImage.objects.filter(pk__in=selected_item_ids)
    #         return render(request, 'detect_barcodes/selected_records.html', {'selected_items': selected_items})
    #
    #     if 'confirm_delete' in request.POST:
    #         selected_item_ids = request.POST.getlist('selected_items')
    #         # print(selected_item_ids)
    #         selected_items = BarcodeImage.objects.filter(pk__in=selected_item_ids)
    #         # selected_items.delete()
    #
    #         # Remove related images from the folder
    #         for item in selected_items:
    #             # # Construct the path to the image file (change it based on your folder structure)
    #             # image_path = os.path.join(settings.MEDIA_ROOT, item.image.name)
    #             #
    #             # # Check if the file exists and delete it
    #             # if os.path.exists(image_path):
    #             #     os.remove(image_path)
    #             #
    #             # image_path = item.image.path
    #             # barcode_path = item.barcode_path.path
    #             #
    #             # # Check if the image files exist before attempting deletion
    #             # if os.path.exists(image_path):
    #             #     os.remove(image_path)
    #             #     print(f"Image file exist at {image_path}")
    #             # else:
    #             #     print(f"Image file does not exist at {image_path}")
    #             #
    #             # if os.path.exists(barcode_path):
    #             #     os.remove(barcode_path)
    #             #     print(f"Barcode file exist at {barcode_path}")
    #             # else:
    #             #     print(f"Barcode file does not exist at {barcode_path}")
    #             #
    #             # # Delete the selected item
    #             # item.delete()
    #             # selected_items.delete()
    #         messages.success(request, 'Selected records deleted successfully and related images removed.')
    #         return redirect('deletebarcode')  # Redirect back to the deletebarcode page after deletion.

    if request.method == 'POST':
        selected_company = request.POST.get('company')
        selected_product = request.POST.get('product')

        if 'selected_items' in request.POST:
            selected_item_ids = request.POST.getlist('selected_items')
            selected_items = BarcodeImage.objects.filter(pk__in=selected_item_ids)
            return render(request, 'detect_barcodes/selected_records.html', {'selected_items': selected_items})

        # if 'confirm_delete' in request.POST:
        #     selected_item_ids = request.POST.getlist('selected_item_ids')  # Note the change here
        #     selected_items = BarcodeImage.objects.filter(pk__in=selected_item_ids)
        #     # selected_items.delete()

        #     # for item in selected_items:
        #     #     image = os.path.join(settings.MEDIA_ROOT, item.image.name)
        #     #
        #     #     if os.path.exists(image):
        #     #         os.remove(image)
        #     for item in selected_items:
        #     # # Construct the path to the image file (change it based on your folder structure)
        #                 image_path = os.path.join(settings.MEDIA_ROOT, item.image.name)


        #                 # Check if the file exists and delete it
        #                 if os.path.exists(image_path):
        #                     os.remove(image_path)

        #                 image_path = item.image.path
        #                 barcode_path = item.barcode_path.path if item.barcode_path else None  # Handle empty barcode_path

        #                 # Check if the image files exist before attempting deletion
        #                 if os.path.exists(image_path):
        #                     os.remove(image_path)
        #                     print(f"Image file exist at {image_path}")
        #                 else:
        #                     print(f"Image file does not exist at {image_path}")


        #                     # Check if barcode_path is not None and not an empty string
        #                     if barcode_path and barcode_path.strip() and os.path.exists(barcode_path):
        #                         os.remove(barcode_path)
        #                         print(f"Barcode file exist at {barcode_path}")
        #                     elif barcode_path:
        #                         print(f"Barcode file does not exist at {barcode_path}")
        #                     else:
        #                         print("Barcode path is None or empty")
        #     # Delete the selected item
        #                 item.delete()
        #                 selected_items.delete()


        #     messages.success(request, 'Selected records deleted successfully and related images removed.')
        #     return redirect('deletebarcode')

        if 'confirm_delete' in request.POST:
            selected_item_ids = request.POST.getlist('selected_item_ids')  # Note the change here
            selected_items = BarcodeImage.objects.filter(pk__in=selected_item_ids)

            for item in selected_items:
                # Construct the path to the image file
                image_path = os.path.join(settings.MEDIA_ROOT, item.image.name) if item.image else None

                # Check if the file exists and delete it
                if image_path and os.path.exists(image_path):
                    os.remove(image_path)
                    print(f"Image file exist at {image_path}")
                elif image_path:
                    print(f"Image file does not exist at {image_path}")

                # Check if barcode_path is not None and not an empty string
                barcode_path = item.barcode_path.path if item.barcode_path else None
                if barcode_path and os.path.exists(barcode_path):
                    os.remove(barcode_path)
                    print(f"Barcode file exist at {barcode_path}")
                elif barcode_path:
                    print(f"Barcode file does not exist at {barcode_path}")
                else:
                    print("Barcode path is None or empty")

            # Delete the selected items
            selected_items.delete()

            messages.success(request, 'Selected records deleted successfully and related images removed.')
            return redirect('deletebarcode')



    if selected_product == 'All':
        items = BarcodeImage.objects.filter(company=selected_company)
        solar_items = items.filter(product_name='SolarPanel')
        inverter_items = items.filter(product_name='Inverter')
        replace_items = items.filter(product_name='Replace')
        solar_panel_total_quantity = solar_items.count()
        solar_panel_quantity_by_wattage = solar_items.values('wattage').annotate(total_quantity=Count('id'))
        inverter_panel_total_quantity = inverter_items.count()
        inverter_panel_quantity_by_wattage = inverter_items.values('wattage').annotate(total_quantity=Count('id'))
        replace_panel_total_quantity = replace_items.count()
        replace_panel_quantity_by_wattage = replace_items.values('wattage').annotate(total_quantity=Count('id'))
    elif selected_product == 'SolarPanel':
        items = BarcodeImage.objects.filter(company=selected_company)
        solar_items = items.filter(product_name='SolarPanel')
        solar_panel_total_quantity = solar_items.count()
        solar_panel_quantity_by_wattage = solar_items.values('wattage').annotate(total_quantity=Count('id'))
    elif selected_product == 'Inverter':
        items = BarcodeImage.objects.filter(company=selected_company)
        inverter_items = items.filter(product_name='Inverter')
        inverter_panel_total_quantity = inverter_items.count()
        inverter_panel_quantity_by_wattage = inverter_items.values('wattage').annotate(total_quantity=Count('id'))
    else:
        items = BarcodeImage.objects.filter(company=selected_company)
        replace_items = items.filter(product_name='Replace')
        replace_panel_total_quantity = replace_items.count()
        replace_panel_quantity_by_wattage = replace_items.values('wattage').annotate(total_quantity=Count('id'))

        unique_wattages = {item['wattage'] for item in solar_panel_quantity_by_wattage}
        inverter_wattages = {item['wattage'] for item in inverter_panel_quantity_by_wattage}
        replace_wattages = {item['wattage'] for item in replace_panel_quantity_by_wattage}

    return render(request, 'detect_barcodes/delete_barcode.html', {
        'companies': companies,
        'product_names': product_names,
        'items': items,
        'solar_items': solar_items,
        'inverter_items': inverter_items,
        'replace_items': replace_items,
        'solar_panel_total_quantity': solar_panel_total_quantity,
        'solar_panel_quantity_by_wattage': solar_panel_quantity_by_wattage,
        'unique_wattages': unique_wattages,
        'inverter_wattages': inverter_wattages,
        'inverter_panel_total_quantity': inverter_panel_total_quantity,
        'inverter_panel_quantity_by_wattage': inverter_panel_quantity_by_wattage,
        'items1': items1,
        'replace_panel_total_quantity': replace_panel_total_quantity,
        'replace_panel_quantity_by_wattage': replace_panel_quantity_by_wattage,
        'replace_wattages': replace_wattages,
        'notification1': notification1,
        'count1': count1,
    })





#
# @login_required(login_url='user-login')
# def deletebarcodeconfirm(request):
#     # ... (your existing code)
#     count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#     notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#     companies = BarcodeImage.objects.values_list('company', flat=True).distinct()
#     product_names = BarcodeImage.objects.values_list('product_name', flat=True).distinct()
#     items1 = BarcodeImage.objects.all()
#     items = []
#     solar_items = []
#     inverter_items = []
#     replace_items = []
#     solar_panel_total_quantity = 0
#     solar_panel_quantity_by_wattage = []
#     unique_wattages = []
#     inverter_wattages = []
#     inverter_panel_quantity_by_wattage = []
#     inverter_panel_total_quantity = 0
#     replace_wattages = []
#     replace_panel_quantity_by_wattage = []
#     replace_panel_total_quantity = 0
#     selected_product = []
#     selected_company = []
#
#     if request.method == 'POST':
#         if 'confirm_delete' in request.POST:
#             # Get selected item IDs
#             selected_item_ids = request.POST.getlist('selected_items')
#
#             # Fetch selected items from the database
#             selected_items = BarcodeImage.objects.filter(pk__in=selected_item_ids)
#
#             # Delete the selected items from the database
#             selected_items.delete()
#
#             # Remove related images from the folder
#             for item in selected_items:
#                 # Construct the path to the image file (change it based on your folder structure)
#                 image = os.path.join(settings.MEDIA_ROOT, item.image.name)
#
#
#                 # Check if the file exists and delete it
#                 if os.path.exists(image):
#                     os.remove(image)
#
#             messages.success(request, 'Selected records deleted successfully and related images removed.')
#
#             # Redirect to the same page after processing the form
#             return redirect('deletebarcode')
#
#     # ... (your existing code)
#
#     return render(request, 'detect_barcodes/delete_barcode.html', {
#         'companies': companies,
#         'product_names': product_names,
#         'items': items,
#         'solar_items': solar_items,
#         'inverter_items': inverter_items,
#         'replace_items': replace_items,
#         'solar_panel_total_quantity': solar_panel_total_quantity,
#         'solar_panel_quantity_by_wattage': solar_panel_quantity_by_wattage,
#         'unique_wattages': unique_wattages,
#         'inverter_wattages': inverter_wattages,
#         'inverter_panel_total_quantity': inverter_panel_total_quantity,
#         'inverter_panel_quantity_by_wattage': inverter_panel_quantity_by_wattage,
#         'items1': items1,
#         'replace_panel_total_quantity': replace_panel_total_quantity,
#         'replace_panel_quantity_by_wattage': replace_panel_quantity_by_wattage,
#         'replace_wattages': replace_wattages,
#         'notification1': notification1,
#         'count1': count1
#     })
#



#
# @login_required(login_url='user-login')
# def editbarcode(request):
#     count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#     notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#     companies = BarcodeImage.objects.values_list('company', flat=True).distinct()
#     product_names = BarcodeImage.objects.values_list('product_name', flat=True).distinct()
#     items1 = BarcodeImage.objects.all()
#     items = []
#     solar_items = []
#     inverter_items = []
#     replace_items = []
#     solar_panel_total_quantity = 0
#     solar_panel_quantity_by_wattage = []
#     unique_wattages = []
#     inverter_wattages = []
#     inverter_panel_quantity_by_wattage = []
#     inverter_panel_total_quantity = 0
#     replace_wattages = []
#     replace_panel_quantity_by_wattage = []
#     replace_panel_total_quantity = 0
#     selected_product = []
#     selected_company = []
#
#     # if request.method == 'POST':
#     #     selected_company = request.POST.get('company')
#     #     selected_product = request.POST.get('product')
#     #
#     #     # Check if the form was submitted with edited values
#     #     if 'selected_items' in request.POST:
#     #         for item_id in request.POST.getlist('selected_items'):
#     #             # Get the edited values from the form
#     #             company_name = request.POST.get(f'company_name_{item_id}')
#     #             wattage = request.POST.get(f'wattage_{item_id}')
#     #             product_name = request.POST.get(f'product1_{item_id}')
#     #
#     #             # Update the corresponding BarcodeImage record in the database if any values have changed
#     #             try:
#     #                 barcode_image = BarcodeImage.objects.get(pk=item_id)
#     #                 if barcode_image.company_name != company_name:
#     #                     print(f'Company Name updated: {barcode_image.company_name} -> {company_name}')
#     #                     barcode_image.company_name = company_name
#     #                 if barcode_image.wattage != wattage:
#     #                     print(f'Wattage updated: {barcode_image.wattage} -> {wattage}')
#     #                     barcode_image.wattage = wattage
#     #                 # Set the previous value of product1 if it's None or blank
#     #                 if not product_name:
#     #                     product_name = barcode_image.product_name
#     #                 elif barcode_image.product_name != product_name:
#     #                     print(f'Product Name updated: {barcode_image.product_name} -> {product_name}')
#     #                 barcode_image.product_name = product_name
#     #                 barcode_image.save()
#     #
#     #                 messages.success(request, f'Data updated successfully for item ID {item_id}')  # Display success message
#     #             except BarcodeImage.DoesNotExist:
#     #                 # Handle the case where the item is not found in the database
#     #                 messages.error(request, 'Data update failed. Item not found.')  # Display error message
#     #
#     #                 # Handle the case where the item is not found in the database
#     #                 pass
#     #
#     #         # Redirect to the same page after processing the form
#     #         return redirect('editbarcode')  # Replace 'editbarcode' with your actual view name
#     # After processing the form, redirect to the 'selected_records' page with selected items
#
#     if request.method == 'POST':
#         selected_company = request.POST.get('company')
#         selected_product = request.POST.get('product')
#         selected_item_ids = request.POST.getlist('selected_items')
#         selected_items = BarcodeImage.objects.filter(pk__in=selected_item_ids)
#         return render(request, 'detect_barcodes/selected_records.html', {'selected_items': selected_items})
#
#     if selected_product == 'All':
#         items = BarcodeImage.objects.filter(company=selected_company)
#         solar_items = items.filter(product_name='SolarPanel')
#         inverter_items = items.filter(product_name='Inverter')
#         replace_items = items.filter(product_name='Replace')
#         solar_panel_total_quantity = solar_items.count()
#         solar_panel_quantity_by_wattage = solar_items.values('wattage').annotate(total_quantity=Count('id'))
#         inverter_panel_total_quantity = inverter_items.count()
#         inverter_panel_quantity_by_wattage = inverter_items.values('wattage').annotate(total_quantity=Count('id'))
#         replace_panel_total_quantity = replace_items.count()
#         replace_panel_quantity_by_wattage = replace_items.values('wattage').annotate(total_quantity=Count('id'))
#     elif selected_product == 'SolarPanel':
#         items = BarcodeImage.objects.filter(company=selected_company)
#         solar_items = items.filter(product_name='SolarPanel')
#         solar_panel_total_quantity = solar_items.count()
#         solar_panel_quantity_by_wattage = solar_items.values('wattage').annotate(total_quantity=Count('id'))
#     elif selected_product == 'Inverter':
#         items = BarcodeImage.objects.filter(company=selected_company)
#         inverter_items = items.filter(product_name='Inverter')
#         inverter_panel_total_quantity = inverter_items.count()
#         inverter_panel_quantity_by_wattage = inverter_items.values('wattage').annotate(total_quantity=Count('id'))
#     else:
#         items = BarcodeImage.objects.filter(company=selected_company)
#         replace_items = items.filter(product_name='Replace')
#         replace_panel_total_quantity = replace_items.count()
#         replace_panel_quantity_by_wattage = replace_items.values('wattage').annotate(total_quantity=Count('id'))
#
#         unique_wattages = {item['wattage'] for item in solar_panel_quantity_by_wattage}
#         inverter_wattages = {item['wattage'] for item in inverter_panel_quantity_by_wattage}
#         replace_wattages = {item['wattage'] for item in replace_panel_quantity_by_wattage}
#     return render(request, 'detect_barcodes/edit_barcode.html',
#                   {'companies': companies, 'product_names': product_names, 'items': items,
#                    'solar_items': solar_items, 'inverter_items': inverter_items, 'replace_items': replace_items,
#                    'solar_panel_total_quantity': solar_panel_total_quantity,
#                    'solar_panel_quantity_by_wattage': solar_panel_quantity_by_wattage,
#                    'unique_wattages': unique_wattages, 'inverter_wattages': inverter_wattages,
#                    'inverter_panel_total_quantity': inverter_panel_total_quantity,
#                    'inverter_panel_quantity_by_wattage': inverter_panel_quantity_by_wattage, 'items1': items1,
#
#                    'replace_panel_total_quantity': replace_panel_total_quantity,
#                    'replace_panel_quantity_by_wattage': replace_panel_quantity_by_wattage,
#                    'replace_wattages': replace_wattages,
#
#                    'notification1': notification1, 'count1': count1})


#
# def scan_barcode(request):
#     if request.method == 'POST':
#         barcode_data = request.POST.get('barcode_data')
#         barcode_type = request.POST.get('barcode_type')
#         company = request.POST.get('company')
#         wattage = request.POST.get('wattage')
#         company_name = request.POST.get('company_name')
#         AssignBy = request.user.id
#
#         # Save the data to the BarcodeImage model
#         barcode_image = BarcodeImage(
#             barcode_data=barcode_data,
#             barcode_type=barcode_type,
#             company=company,
#             wattage=wattage,
#             company_name=company_name,
#             AssignBy=AssignBy,
#         )
#         barcode_image.save()
#
#         return JsonResponse({'message': 'Barcode data saved successfully!'})
#
#     return render(request, 'detect_barcodes/scan_barcode.html')

#
# def save_barcodes(request):
#     if request.method == 'POST':
#         barcode_data = request.POST.get('barcodes')
#         if barcode_data:
#             try:
#                 barcodes = json.loads(barcode_data)
#                 for barcode in barcodes:
#                     # Create a BarcodeImage object for each barcode and save it to the database
#                     BarcodeImage.objects.create(
#                         barcode_data=barcode['data'],
#                         barcode_type=barcode['type'],
#                         # Add other fields as needed
#                     )
#                 return JsonResponse({'success': True})
#             except json.JSONDecodeError as e:
#                 return JsonResponse({'success': False, 'error': str(e)})
#         return JsonResponse({'success': False})
#     return render(request, 'detect_barcodes/scan_barcode.html')


# barcode_decoder/views.py

from django.http import JsonResponse
from pyzbar.pyzbar import decode
from PIL import Image
from io import BytesIO
import base64

def realtime_decode(request):
    return render(request, 'detect_barcodes/scan_barcode.html')

def scan_barcode(request):
    image_data = request.POST.get('image_data')
    print("Received image data:", image_data)
    decoded_data = decode_image(image_data)
    print("Decoded data:", decoded_data)
    return JsonResponse({'barcode_value': decoded_data})

def decode_image(image_data):
    image_bytes = base64.b64decode(image_data.split(',')[1])
    img = Image.open(BytesIO(image_bytes))
    decoded_data = decode(img)
    if decoded_data:
        return decoded_data[0].data.decode('utf-8')
    else:
        return None



# # views.py
# from io import BytesIO
# from django.shortcuts import render, redirect
# from .models import BarcodeImage
# from PIL import Image
# import pytesseract
# import re
# import fitz  # PyMuPDF
#
# # Set the Tesseract executable path
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
#
# def extract_text_from_image(image):
#     try:
#         extracted_data = pytesseract.image_to_string(image)
#         return extracted_data
#     except pytesseract.TesseractError as e:
#         print(str(e))
#         return None
#
# def extract_text_from_pdf(pdf_file):
#     try:
#         doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
#         text = ""
#         for page_num in range(doc.page_count):
#             page = doc[page_num]
#             text += page.get_text()
#
#         return text
#     except Exception as e:
#         print(str(e))
#         return None
#
# def process_and_save_barcodes(text):
#     if text:
#         barcode_data_list = re.findall(r'\b[0-9*/\-.]{9,}\b', text)
#
#         # Save each valid barcode as a separate record in the database
#         for valid_barcode in barcode_data_list:
#             BarcodeImage.objects.create(barcode_data=valid_barcode)
#
# def upload_and_display_view(request):
#     if request.method == 'POST':
#         uploaded_file = request.FILES.get('file')
#
#         if uploaded_file:
#             # Extract text from the uploaded image or PDF and save valid barcodes
#             if uploaded_file.name.lower().endswith(('.png', '.jpg', '.jpeg')):
#                 uploaded_image = Image.open(uploaded_file)
#                 text = extract_text_from_image(uploaded_image)
#             elif uploaded_file.name.lower().endswith('.pdf'):
#                 text = extract_text_from_pdf(uploaded_file)
#             else:
#                 # Handle unsupported file types
#                 return render(request, 'error.html', {'error_message': 'Unsupported file type'})
#
#             process_and_save_barcodes(text)
#
#             return redirect('detect_barcodes-serial_barcode')
#
#     # Display all valid barcodes from the database
#     barcode_images = BarcodeImage.objects.all()
#     context = {'barcode_images': barcode_images}
#     return render(request, 'detect_barcodes/serial_barcode.html', context)






# # views.py
# from django.shortcuts import render
# from .models import BarcodeImage
# from PIL import Image
# import pytesseract
# import re
#
# # Set the Tesseract executable path
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
#
# def barcode_exists(barcode):
#     return BarcodeImage.objects.filter(barcode_data=barcode).exists()
#
# # def process_and_save_barcodes(images):
# #     detected_count = 0
# #     non_detected_count = 0
# #     duplicate_count = 0
# #     valid_barcodes = []
# #
# #     for image in images:
# #         try:
# #             uploaded_image = Image.open(image)
# #             extracted_data = pytesseract.image_to_string(uploaded_image)
# #             barcode_data_list = extracted_data.split()
# #
# #             for barcode in barcode_data_list:
# #                 cleaned_barcode = re.sub(r'[^0-9*/.\-a-zA-Z]', '', barcode)
# #                 if len(re.sub(r'[^0-9]', '', cleaned_barcode)) >= 9 and all(char in '*/-.0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ' for char in cleaned_barcode):
# #                     if not barcode_exists(cleaned_barcode):
# #                         # Use save method to handle file storage
# #                         barcode_image = BarcodeImage(barcode_data=cleaned_barcode)
# #                         barcode_image.image.save(image.name, image)
# #                         barcode_image.save()
# #                         detected_count += 1
# #                         valid_barcodes.append((cleaned_barcode, 'Detect', barcode_image))
# #                     else:
# #                         duplicate_count += 1
# #                         valid_barcodes.append((cleaned_barcode, 'Duplicate', None))
# #                 else:
# #                     non_detected_count += 1
# #         except pytesseract.TesseractError as e:
# #             print(str(e))
# #
# #     return detected_count, non_detected_count, duplicate_count, valid_barcodes
#
#
#
# def process_and_save_barcodes(images, company, wattage, comp_name, product_name, AssignBy, AssignTo_id):
#     detected_count = 0
#     non_detected_count = 0
#     duplicate_count = 0
#     valid_barcodes = []
#
#     for image in images:
#         try:
#             uploaded_image = Image.open(image)
#             extracted_data = pytesseract.image_to_string(uploaded_image)
#             barcode_data_list = extracted_data.split()
#
#             for barcode in barcode_data_list:
#                 cleaned_barcode = re.sub(r'[^0-9*/.\-a-zA-Z]', '', barcode)
#                 if len(re.sub(r'[^0-9]', '', cleaned_barcode)) >= 9 and all(char in '*/-.0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ' for char in cleaned_barcode):
#                     if not barcode_exists(cleaned_barcode):
#                         # Use save method to handle file storage
#                         barcode_image = BarcodeImage(
#                             barcode_data=cleaned_barcode,
#                             company=company,
#                             wattage=wattage,
#                             company_name=comp_name,
#                             AssignBy=AssignBy,
#                             product_name=product_name,
#                             AssignTo_id=AssignTo_id,
#                         )
#                         barcode_image.image.save(image.name, image)
#                         barcode_image.save()
#                         detected_count += 1
#                         valid_barcodes.append((cleaned_barcode, 'Detect', barcode_image))
#                     else:
#                         duplicate_count += 1
#                         valid_barcodes.append((cleaned_barcode, 'Duplicate', None))
#                 else:
#                     non_detected_count += 1
#         except pytesseract.TesseractError as e:
#             print(str(e))
#
#     return detected_count, non_detected_count, duplicate_count, valid_barcodes
#
#
# def upload_and_display_view(request):
#     count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#     notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#     detected_count = None
#     non_detected_count = None
#     duplicate_count = None
#     valid_barcodes = None
#     companies = Customer.objects.all()
#
#     # if request.method == 'POST':
#     #     images = request.FILES.getlist('images')
#     #
#     #     product_name = None
#     #
#     #     # Determine the product_name based on the template being used
#     #     if request.path == '/detect_barcodes/detect_barcodes/':
#     #         product_name = 'SolarPanel'
#     #     elif request.path == '/detect_barcodes/detect_inverter/':
#     #         product_name = 'Inverter'
#     #
#     #
#     #     for image in images:
#     #         company = request.POST.get('solarPlateCompany')  # Get the value of the company field
#     #         wattage = request.POST.get('wattage')  # Get the value of the wattage field
#     #         new_customer_id = request.POST.get('new_customer_id')
#     #         comp_name = request.POST.get('comp_name')  # Get the value of the dynamically changing textbox
#     #
#     #         if comp_name:
#     #             customer = Customer.objects.get(new_customer_id=comp_name)
#     #             company_name = customer.Comp_name
#     #
#     #
#     #
#     #     detected_count, non_detected_count, duplicate_count, valid_barcodes = process_and_save_barcodes(images)
#
#     if request.method == 'POST':
#         images = request.FILES.getlist('images')
#         company = request.POST.get('solarPlateCompany')
#         wattage = request.POST.get('wattage')
#         comp_name = request.POST.get('comp_name')
#         product_name = 'SolarPanel'
#
#         # # Determine the product_name based on the template being used
#         # if request.path == '/detect_barcodes/serial_barcode.html/':
#         #     product_name = 'SolarPanel'
#         # elif request.path == '/detect_barcodes/detect_inverter/':
#         #     product_name = 'Inverter'
#
#         AssignBy = request.user.id
#
#         # if new_customer_id.isdigit():
#         # assign_to_user = User.objects.get(id=new_customer_id)
#         #                         else:
#         #                             assign_to_user = None
#         #
#         AssignTo_id = request.POST.get('new_customer_id')
#
#         detected_count, non_detected_count, duplicate_count, valid_barcodes = process_and_save_barcodes(
#             images, company, wattage, comp_name, product_name, AssignBy, AssignTo_id
#         )
#
#         for company in companies:
#             deployed_solarpanel_count = BarcodeImage.objects.filter(AssignTo_id=company.new_customer_id,
#                                                                     product_name="SolarPanel").count()
#             remaining_solarpanel_count = company.qunt_solar - deployed_solarpanel_count
#             company.remaining_solarpanel_count = remaining_solarpanel_count
#
#         # Filter companies based on remaining_inverter_count
#         filtered_companies = [company for company in companies if company.remaining_solarpanel_count > 0]
#         print(request.POST)
#         print(request.FILES)
#
#     context = {
#         'detected_count': detected_count,
#         'non_detected_count': non_detected_count,
#         'duplicate_count': duplicate_count,
#         'valid_barcodes': valid_barcodes,
#         # 'filtered_companies': filtered_companies,
#         'count1': count1,
#         'notification1': notification1,
#         'companies': companies,
#         }
#     return render(request, 'detect_barcodes/serial_barcode.html', context)
#




# views.py
from django.shortcuts import render
from .models import BarcodeImage
from PIL import Image
import pytesseract
import re

# Set the Tesseract executable path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def barcode_exists(barcode):
    return BarcodeImage.objects.filter(barcode_data=barcode).exists()

# def process_and_save_barcodes(images, company, wattage, comp_name, product_name, AssignBy, AssignTo_id, company_name):
#     detected_count = 0
#     non_detected_count = 0
#     duplicate_count = 0
#     valid_barcodes = []
#
#     for image in images:
#         try:
#             uploaded_image = Image.open(image)
#             extracted_data = pytesseract.image_to_string(uploaded_image)
#             barcode_data_list = extracted_data.split()
#
#             for barcode in barcode_data_list:
#                 cleaned_barcode = re.sub(r'[^0-9*/.\-a-zA-Z]', '', barcode)
#                 if len(re.sub(r'[^0-9]', '', cleaned_barcode)) >= 9 and all(char in '*/-.0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ' for char in cleaned_barcode):
#                     if not barcode_exists(cleaned_barcode):
#                         # Use save method to handle file storage
#                         tz = pytz.timezone('Asia/Kolkata')  # Set the timezone to IST (Indian Standard Time)
#                         file_saved_at = timezone.now().astimezone(tz)
#
#                         # if new_customer_id.isdigit():
#                         #     assign_to_user = User.objects.get(id=new_customer_id)
#                         # else:
#                         #     assign_to_user = None
#
#                         barcode_image = BarcodeImage(
#                             barcode_data=cleaned_barcode,
#                             company=company_name,
#                             wattage=wattage,
#                             company_name=company,
#                             AssignBy=AssignBy,
#                             product_name=product_name,
#                             AssignTo_id=AssignTo_id,
#                             file_saved_at=file_saved_at,
#                         )
#                         barcode_image.image.save(image.name, image)
#                         barcode_image.save()
#                         detected_count += 1
#                     #     valid_barcodes.append((cleaned_barcode, 'Detect', barcode_image))
#                     #     print(f"Saved Barcode: {cleaned_barcode} for Company: {company}")
#                     # else:
#                     #     duplicate_count += 1
#                     #     valid_barcodes.append((cleaned_barcode, 'Duplicate', None))
#                     #     print(f"Duplicate Barcode: {cleaned_barcode}")
#
#                         valid_barcodes.append(
#                             (cleaned_barcode, 'Detect', barcode_image, file_saved_at, company, wattage))
#                         print(f"Saved Barcode: {cleaned_barcode} for Company: {company}")
#                     else:
#                         duplicate_count += 1
#                         valid_barcodes.append((cleaned_barcode, 'Duplicate', None, None, None, None))
#                         print(f"Duplicate Barcode: {cleaned_barcode}")
#                 else:
#                     non_detected_count += 1
#         except pytesseract.TesseractError as e:
#             print(str(e))
#
#     return detected_count, non_detected_count, duplicate_count, valid_barcodes

def process_and_save_barcodes(files, company, wattage, comp_name, product_name, AssignBy, AssignTo_id, company_name,
                              serial_number_match=None):
    detected_count = 0
    non_detected_count = 0
    duplicate_count = 0
    valid_barcodes = []

    for file in files:
        try:
            if file.name.endswith('.pdf'):
                # Handle PDF files
                pdf_reader = PdfFileReader(file)
                for page_num in range(pdf_reader.numPages):
                    page = pdf_reader.getPage(page_num)
                    extracted_data = page.extract_text()
                    # barcode_data_list = extracted_data.split()
                    if serial_number_match:
                        cleaned_barcode = re.sub(r'[^0-9*/.\-a-zA-Z]', '', serial_number_match.group())
                    # for barcode in barcode_data_list:
                    #     # The rest of the code remains the same as in the original version
                    #     cleaned_barcode = re.sub(r'[^0-9*/.\-a-zA-Z]', '', barcode)
                        if len(re.sub(r'[^0-9]', '', cleaned_barcode)) >= 9 and all(
                                char in '*/-.0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ' for
                                char in cleaned_barcode):
                            if not barcode_exists(cleaned_barcode):
                                # Use save method to handle file storage
                                tz = pytz.timezone('Asia/Kolkata')  # Set the timezone to IST (Indian Standard Time)
                                file_saved_at = timezone.now().astimezone(tz)

                                # if new_customer_id.isdigit():
                                #     assign_to_user = User.objects.get(id=new_customer_id)
                                # else:
                                #     assign_to_user = None

                                barcode_image = BarcodeImage(
                                    barcode_data=cleaned_barcode,
                                    company=company_name,
                                    wattage=wattage,
                                    company_name=company,
                                    AssignBy=AssignBy,
                                    product_name=product_name,
                                    AssignTo_id=AssignTo_id,
                                    file_saved_at=file_saved_at,
                                )
                                # barcode_image.image.save(file.name, file)
                                barcode_image.save()
                                detected_count += 1
                                #     valid_barcodes.append((cleaned_barcode, 'Detect', barcode_image))
                                #     print(f"Saved Barcode: {cleaned_barcode} for Company: {company}")
                                # else:
                                #     duplicate_count += 1
                                #     valid_barcodes.append((cleaned_barcode, 'Duplicate', None))
                                #     print(f"Duplicate Barcode: {cleaned_barcode}")

                                valid_barcodes.append(
                                    (cleaned_barcode, 'Detect', barcode_image, file_saved_at, company, wattage))
                                print(f"Saved Barcode: {cleaned_barcode} for Company: {company}")
                            else:
                                duplicate_count += 1
                                valid_barcodes.append(
                                    (cleaned_barcode, 'Duplicate', None, None, None, None))
                                print(f"Duplicate Barcode: {cleaned_barcode}")
                        else:
                            non_detected_count += 1

            else:
                # Handle image files
                uploaded_image = Image.open(file)
                extracted_data = pytesseract.image_to_string(uploaded_image)
                barcode_data_list = extracted_data.split()

                for barcode in barcode_data_list:
                    # The rest of the code remains the same as in the original version
                    cleaned_barcode = re.sub(r'[^0-9*/.\-a-zA-Z]', '', barcode)
                    if len(re.sub(r'[^0-9]', '', cleaned_barcode)) >= 9 and all(
                            char in '*/-.0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ' for
                            char in cleaned_barcode):
                        if not barcode_exists(cleaned_barcode):
                            # Use save method to handle file storage
                            tz = pytz.timezone('Asia/Kolkata')  # Set the timezone to IST (Indian Standard Time)
                            file_saved_at = timezone.now().astimezone(tz)

                            # if new_customer_id.isdigit():
                            #     assign_to_user = User.objects.get(id=new_customer_id)
                            # else:
                            #     assign_to_user = None

                            barcode_image = BarcodeImage(
                                barcode_data=cleaned_barcode,
                                company=company_name,
                                wattage=wattage,
                                company_name=company,
                                AssignBy=AssignBy,
                                product_name=product_name,
                                AssignTo_id=AssignTo_id,
                                file_saved_at=file_saved_at,
                            )
                            # barcode_image.image.save(file.name, file)
                            barcode_image.save()
                            detected_count += 1
                            #     valid_barcodes.append((cleaned_barcode, 'Detect', barcode_image))
                            #     print(f"Saved Barcode: {cleaned_barcode} for Company: {company}")
                            # else:
                            #     duplicate_count += 1
                            #     valid_barcodes.append((cleaned_barcode, 'Duplicate', None))
                            #     print(f"Duplicate Barcode: {cleaned_barcode}")

                            valid_barcodes.append(
                                (cleaned_barcode, 'Detect', barcode_image, file_saved_at, company, wattage))
                            print(f"Saved Barcode: {cleaned_barcode} for Company: {company}")
                        else:
                            duplicate_count += 1
                            valid_barcodes.append(
                                (cleaned_barcode, 'Duplicate', None, None, None, None))
                            print(f"Duplicate Barcode: {cleaned_barcode}")
                    else:
                        non_detected_count += 1

        except (pytesseract.TesseractError, Exception) as e:
            print(str(e))

    return detected_count, non_detected_count, duplicate_count, valid_barcodes



def upload_and_display_view(request):
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    detected_count = None
    non_detected_count = None
    duplicate_count = None
    valid_barcodes = None
    companies = Customer.objects.all()
    selected_company_name = None
    uploaded_count = None
    filtered_companies = []  # Initialize with an empty list

    # Determine the product_name based on the template being used
    if request.path == '/detect_barcodes/serial_barcode/':
        for company in companies:
            deployed_solarpanel_count = BarcodeImage.objects.filter(AssignTo_id=company.new_customer_id,
                                                                    product_name="SolarPanel").count()
            remaining_solarpanel_count = company.qunt_solar - deployed_solarpanel_count
            company.remaining_solarpanel_count = remaining_solarpanel_count

    elif request.path == '/detect_barcodes/serial_barcode_inverter/':
        for company in companies:
            deployed_inverter_count = BarcodeImage.objects.filter(AssignTo_id=company.new_customer_id,
                                                                  product_name="Inverter").count()
            remaining_inverter_count = company.qunt_inv - deployed_inverter_count
            company.remaining_inverter_count = remaining_inverter_count

    # Filter companies based on remaining_inverter_count
    filtered_companies = [company for company in companies if company.remaining_solarpanel_count > 0]
    print(request.POST)
    print(request.FILES)

    if request.method == 'POST':
        images = request.FILES.getlist('images')
        company = request.POST.get('solarPlateCompany')
        wattage = request.POST.get('wattage')
        comp_name = request.POST.get('comp_name')
        if comp_name:
            customer = Customer.objects.get(new_customer_id=comp_name)
            company_name = customer.Comp_name
            selected_company_name = company_name  # Set the selected company name
        product_name = None

        # Determine the product_name based on the template being used
        if request.path == '/detect_barcodes/serial_barcode/':
            product_name = 'SolarPanel'
        elif request.path == '/detect_barcodes/serial_barcode_inverter/':
            product_name = 'Inverter'

        AssignBy = request.user.id

        AssignTo_id = request.POST.get('new_customer_id')

        detected_count, non_detected_count, duplicate_count, valid_barcodes = process_and_save_barcodes(
            images, company, wattage, comp_name, product_name, AssignBy, AssignTo_id, company_name
        )

        # messages.success(request, f"Successfully uploaded {len(images)} images.")
        # messages.success(request, f"Detected Barcodes: {detected_count}")
        # messages.success(request, f"Duplicate Barcodes: {duplicate_count}")
        # messages.warning(request, f"Non-Detected Barcodes: {non_detected_count}")
        uploaded_count = len(images)
        detected_count = detected_count
        duplicate_count = duplicate_count
        non_detected_count = non_detected_count


    context = {
        'detected_count': detected_count,
        'non_detected_count': non_detected_count,
        'duplicate_count': duplicate_count,
        'valid_barcodes': valid_barcodes,
        'filtered_companies': filtered_companies,
        'count1': count1,
        'notification1': notification1,
        'companies': companies,
        'selected_company_name': selected_company_name,  # Pass the selected company name to the template
        'uploaded_count': uploaded_count,
    }

    # Determine the product_name based on the template being used
    if request.path == '/detect_barcodes/serial_barcode/':
        return render(request, 'detect_barcodes/serial_barcode.html', context)

    elif request.path == '/detect_barcodes/serial_barcode_inverter/':
        return render(request, 'detect_barcodes/serial_barcode_inverter.html', context)



def manual_serial_barcode(request):
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    detected_count = None
    non_detected_count = None
    duplicate_count = None
    valid_barcodes = None
    companies = Customer.objects.all()
    selected_company_name = None
    uploaded_count = None
    filtered_companies = []  # Initialize with an empty list

    # Determine the product_name based on the template being used
    if request.path == '/detect_barcodes/manual_serial_barcode/':
        for company in companies:
            deployed_solarpanel_count = BarcodeImage.objects.filter(AssignTo_id=company.new_customer_id,
                                                                    product_name="SolarPanel").count()
            remaining_solarpanel_count = company.qunt_solar - deployed_solarpanel_count
            company.remaining_solarpanel_count = remaining_solarpanel_count


    elif request.path == '/detect_barcodes/manual_inverter_barcode/':
        for company in companies:
            deployed_inverter_count = BarcodeImage.objects.filter(AssignTo_id=company.new_customer_id,
                                                                  product_name="Inverter").count()
            remaining_inverter_count = company.qunt_inv - deployed_inverter_count
            company.remaining_inverter_count = remaining_inverter_count

    # Filter companies based on remaining_inverter_count
    if request.path == '/detect_barcodes/manual_serial_barcode/':
        filtered_companies = [company for company in companies if company.remaining_solarpanel_count > 0]
    elif request.path == '/detect_barcodes/manual_inverter_barcode/':
        filtered_companies = [company for company in companies if company.remaining_inverter_count > 0]
    print(request.POST)
    # print(request.FILES)

    if request.method == 'POST':
        barcode_serial_numbers = request.POST.getlist('barcode_serial_numbers[]')
        company = request.POST.get('solarPlateCompany')
        wattage = request.POST.get('wattage')
        comp_name = request.POST.get('comp_name')
        if comp_name:
            customer = Customer.objects.get(new_customer_id=comp_name)
            company_name = customer.Comp_name
            selected_company_name = company_name  # Set the selected company name
            product_name = None

        # Determine the product_name based on the template being used
        if request.path == '/detect_barcodes/manual_serial_barcode/':
            product_name = 'SolarPanel'
        elif request.path == '/detect_barcodes/manual_inverter_barcode/':
            product_name = 'Inverter'

        AssignBy = request.user.id

        AssignTo_id = request.POST.get('new_customer_id')

        detected_count, non_detected_count, duplicate_count, valid_barcodes = process_and_save_barcodesmanual(
             barcode_serial_numbers, company, wattage, comp_name, product_name, AssignBy, AssignTo_id, company_name
        )

        # messages.success(request, f"Successfully uploaded {len(images)} images.")
        # messages.success(request, f"Detected Barcodes: {detected_count}")
        # messages.success(request, f"Duplicate Barcodes: {duplicate_count}")
        # messages.warning(request, f"Non-Detected Barcodes: {non_detected_count}")
        uploaded_count = len(barcode_serial_numbers)
        detected_count = detected_count
        duplicate_count = duplicate_count
        non_detected_count = non_detected_count


    context = {
        'detected_count': detected_count,
        'non_detected_count': non_detected_count,
        'duplicate_count': duplicate_count,
        'valid_barcodes': valid_barcodes,
        'filtered_companies': filtered_companies,
        'count1': count1,
        'notification1': notification1,
        'companies': companies,
        'selected_company_name': selected_company_name,  # Pass the selected company name to the template
        'uploaded_count': uploaded_count,
    }

    # Determine the product_name based on the template being used
    if request.path == '/detect_barcodes/manual_serial_barcode/':
        return render(request, 'detect_barcodes/manual_serial_barcode.html', context)

    elif request.path == '/detect_barcodes/manual_inverter_barcode/':
        return render(request, 'detect_barcodes/manual_inverter_barcode.html', context)


def process_and_save_barcodesmanual(barcode_serial_numbers, company, wattage, comp_name, product_name, AssignBy, AssignTo_id, company_name,
                              serial_number_match=None):
    detected_count = 0
    non_detected_count = 0
    duplicate_count = 0
    valid_barcodes = []
    file_saved_at = None

    for barcode_serial_number in barcode_serial_numbers:
        # Your barcode processing logic here
        # Example: Check if the barcode_serial_number already exists in the database
        if BarcodeImage.objects.filter(barcode_data=barcode_serial_number).exists():
            # Duplicate barcode
            duplicate_count += 1
            status = 'Duplicate'
            # valid_barcodes.append(
            #     (barcode_serial_number, 'Duplicate', None, None, None))
            # print(f"Duplicate Barcode: {barcode_serial_number}")
        else:
            # Use save method to handle file storage
            tz = pytz.timezone('Asia/Kolkata')  # Set the timezone to IST (Indian Standard Time)
            file_saved_at = timezone.now().astimezone(tz)

            # Save the barcode to the database
            barcode_image = BarcodeImage(
                # barcode_data=barcode_serial_number,
                # company=company,
                # wattage=wattage,
                # company_name=comp_name,
                # product_name=product_name,
                # AssignBy=AssignBy,
                # AssignTo_id=AssignTo_id,
                # company_name=company_name,

                barcode_data=barcode_serial_number,
                company=company_name,
                wattage=wattage,
                company_name=company,
                AssignBy=AssignBy,
                product_name=product_name,
                AssignTo_id=AssignTo_id,
                file_saved_at=file_saved_at,
            )
            barcode_image.save()
            detected_count += 1
            status = 'Detected'

        # valid_barcodes.append((barcode_serial_number, status))  # You can include additional information if needed
        valid_barcodes.append((barcode_serial_number, status, file_saved_at, company, wattage))
        print(f"Saved Barcode: {barcode_serial_number} for Company: {company}")

    non_detected_count = len(barcode_serial_numbers) - detected_count

    return detected_count, non_detected_count, duplicate_count, valid_barcodes




# views.py
from django.shortcuts import render
from .models import BarcodeImage
from PIL import Image
import pytesseract
import re

# Set the Tesseract executable path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def barcode_exists(barcode):
    return BarcodeImage.objects.filter(barcode_data=barcode).exists()

# def process_and_save_barcodes(images, company, wattage, comp_name, product_name, AssignBy, AssignTo_id, company_name):
#     detected_count = 0
#     non_detected_count = 0
#     duplicate_count = 0
#     valid_barcodes = []
#
#     for image in images:
#         try:
#             uploaded_image = Image.open(image)
#             extracted_data = pytesseract.image_to_string(uploaded_image)
#             barcode_data_list = extracted_data.split()
#
#             for barcode in barcode_data_list:
#                 cleaned_barcode = re.sub(r'[^0-9*/.\-a-zA-Z]', '', barcode)
#                 if len(re.sub(r'[^0-9]', '', cleaned_barcode)) >= 9 and all(char in '*/-.0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ' for char in cleaned_barcode):
#                     if not barcode_exists(cleaned_barcode):
#                         # Use save method to handle file storage
#                         tz = pytz.timezone('Asia/Kolkata')  # Set the timezone to IST (Indian Standard Time)
#                         file_saved_at = timezone.now().astimezone(tz)
#
#                         # if new_customer_id.isdigit():
#                         #     assign_to_user = User.objects.get(id=new_customer_id)
#                         # else:
#                         #     assign_to_user = None
#
#                         barcode_image = BarcodeImage(
#                             barcode_data=cleaned_barcode,
#                             company=company_name,
#                             wattage=wattage,
#                             company_name=company,
#                             AssignBy=AssignBy,
#                             product_name=product_name,
#                             AssignTo_id=AssignTo_id,
#                             file_saved_at=file_saved_at,
#                         )
#                         barcode_image.image.save(image.name, image)
#                         barcode_image.save()
#                         detected_count += 1
#                     #     valid_barcodes.append((cleaned_barcode, 'Detect', barcode_image))
#                     #     print(f"Saved Barcode: {cleaned_barcode} for Company: {company}")
#                     # else:
#                     #     duplicate_count += 1
#                     #     valid_barcodes.append((cleaned_barcode, 'Duplicate', None))
#                     #     print(f"Duplicate Barcode: {cleaned_barcode}")
#
#                         valid_barcodes.append(
#                             (cleaned_barcode, 'Detect', barcode_image, file_saved_at, company, wattage))
#                         print(f"Saved Barcode: {cleaned_barcode} for Company: {company}")
#                     else:
#                         duplicate_count += 1
#                         valid_barcodes.append((cleaned_barcode, 'Duplicate', None, None, None, None))
#                         print(f"Duplicate Barcode: {cleaned_barcode}")
#                 else:
#                     non_detected_count += 1
#         except pytesseract.TesseractError as e:
#             print(str(e))
#
#     return detected_count, non_detected_count, duplicate_count, valid_barcodes


def process_and_save_barcodes(files, company, wattage, comp_name, product_name, AssignBy, AssignTo_id, company_name,
                              serial_number_match=None):
    detected_count = 0
    non_detected_count = 0
    duplicate_count = 0
    valid_barcodes = []

    for file in files:
        try:
            if file.name.endswith('.pdf'):
                # Handle PDF files
                pdf_reader = PdfFileReader(file)
                for page_num in range(pdf_reader.numPages):
                    page = pdf_reader.getPage(page_num)
                    extracted_data = page.extract_text()
                    # barcode_data_list = extracted_data.split()
                    if serial_number_match:
                        cleaned_barcode = re.sub(r'[^0-9*/.\-a-zA-Z]', '', serial_number_match.group())
                    # for barcode in barcode_data_list:
                    #     # The rest of the code remains the same as in the original version
                    #     cleaned_barcode = re.sub(r'[^0-9*/.\-a-zA-Z]', '', barcode)
                        if len(re.sub(r'[^0-9]', '', cleaned_barcode)) >= 9 and all(
                                char in '*/-.0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ' for
                                char in cleaned_barcode):
                            if not barcode_exists(cleaned_barcode):
                                # Use save method to handle file storage
                                tz = pytz.timezone('Asia/Kolkata')  # Set the timezone to IST (Indian Standard Time)
                                file_saved_at = timezone.now().astimezone(tz)

                                # if new_customer_id.isdigit():
                                #     assign_to_user = User.objects.get(id=new_customer_id)
                                # else:
                                #     assign_to_user = None

                                barcode_image = BarcodeImage(
                                    barcode_data=cleaned_barcode,
                                    company=company_name,
                                    wattage=wattage,
                                    company_name=company,
                                    AssignBy=AssignBy,
                                    product_name=product_name,
                                    AssignTo_id=AssignTo_id,
                                    file_saved_at=file_saved_at,
                                )
                                # barcode_image.image.save(file.name, file)
                                barcode_image.save()
                                detected_count += 1
                                #     valid_barcodes.append((cleaned_barcode, 'Detect', barcode_image))
                                #     print(f"Saved Barcode: {cleaned_barcode} for Company: {company}")
                                # else:
                                #     duplicate_count += 1
                                #     valid_barcodes.append((cleaned_barcode, 'Duplicate', None))
                                #     print(f"Duplicate Barcode: {cleaned_barcode}")

                                valid_barcodes.append(
                                    (cleaned_barcode, 'Detect', barcode_image, file_saved_at, company, wattage))
                                print(f"Saved Barcode: {cleaned_barcode} for Company: {company}")
                            else:
                                duplicate_count += 1
                                valid_barcodes.append(
                                    (cleaned_barcode, 'Duplicate', None, None, None, None))
                                print(f"Duplicate Barcode: {cleaned_barcode}")
                        else:
                            non_detected_count += 1

            else:
                # Handle image files
                uploaded_image = Image.open(file)
                extracted_data = pytesseract.image_to_string(uploaded_image)
                barcode_data_list = extracted_data.split()

                for barcode in barcode_data_list:
                    # The rest of the code remains the same as in the original version
                    cleaned_barcode = re.sub(r'[^0-9*/.\-a-zA-Z]', '', barcode)
                    if len(re.sub(r'[^0-9]', '', cleaned_barcode)) >= 9 and all(
                            char in '*/-.0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ' for
                            char in cleaned_barcode):
                        if not barcode_exists(cleaned_barcode):
                            # Use save method to handle file storage
                            tz = pytz.timezone('Asia/Kolkata')  # Set the timezone to IST (Indian Standard Time)
                            file_saved_at = timezone.now().astimezone(tz)

                            # if new_customer_id.isdigit():
                            #     assign_to_user = User.objects.get(id=new_customer_id)
                            # else:
                            #     assign_to_user = None

                            barcode_image = BarcodeImage(
                                barcode_data=cleaned_barcode,
                                company=company_name,
                                wattage=wattage,
                                company_name=company,
                                AssignBy=AssignBy,
                                product_name=product_name,
                                AssignTo_id=AssignTo_id,
                                file_saved_at=file_saved_at,
                            )
                            # barcode_image.image.save(file.name, file)
                            barcode_image.save()
                            detected_count += 1
                            #     valid_barcodes.append((cleaned_barcode, 'Detect', barcode_image))
                            #     print(f"Saved Barcode: {cleaned_barcode} for Company: {company}")
                            # else:
                            #     duplicate_count += 1
                            #     valid_barcodes.append((cleaned_barcode, 'Duplicate', None))
                            #     print(f"Duplicate Barcode: {cleaned_barcode}")

                            valid_barcodes.append(
                                (cleaned_barcode, 'Detect', barcode_image, file_saved_at, company, wattage))
                            print(f"Saved Barcode: {cleaned_barcode} for Company: {company}")
                        else:
                            duplicate_count += 1
                            valid_barcodes.append(
                                (cleaned_barcode, 'Duplicate', None, None, None, None))
                            print(f"Duplicate Barcode: {cleaned_barcode}")
                    else:
                        non_detected_count += 1

        except (pytesseract.TesseractError, Exception) as e:
            print(str(e))

    return detected_count, non_detected_count, duplicate_count, valid_barcodes



#
# def upload_and_display_view_inverter(request):
#     count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
#     notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
#     detected_count = None
#     non_detected_count = None
#     duplicate_count = None
#     valid_barcodes = None
#     companies = Customer.objects.all()
#     selected_company_name = None
#     uploaded_count = None
#     filtered_companies = None
#
#     if request.method == 'POST':
#         images = request.FILES.getlist('images')
#         company = request.POST.get('solarPlateCompany')
#         wattage = request.POST.get('wattage')
#         comp_name = request.POST.get('comp_name')
#         if comp_name:
#             customer = Customer.objects.get(new_customer_id=comp_name)
#             company_name = customer.Comp_name
#             selected_company_name = company_name  # Set the selected company name
#         product_name = None
#
#         # Determine the product_name based on the template being used
#         if request.path == '/detect_barcodes/serial_barcode/':
#             product_name = 'SolarPanel'
#         elif request.path == '/detect_barcodes/serial_barcode_inverter/':
#             product_name = 'Inverter'
#
#         AssignBy = request.user.id
#
#         AssignTo_id = request.POST.get('new_customer_id')
#
#         detected_count, non_detected_count, duplicate_count, valid_barcodes = process_and_save_barcodes(
#             images, company, wattage, comp_name, product_name, AssignBy, AssignTo_id, company_name
#         )
#
#         # messages.success(request, f"Successfully uploaded {len(images)} images.")
#         # messages.success(request, f"Detected Barcodes: {detected_count}")
#         # messages.success(request, f"Duplicate Barcodes: {duplicate_count}")
#         # messages.warning(request, f"Non-Detected Barcodes: {non_detected_count}")
#         uploaded_count = len(images)
#         detected_count = detected_count
#         duplicate_count = duplicate_count
#         non_detected_count = non_detected_count
#
#         # Determine the product_name based on the template being used
#         for company in companies:
#                 deployed_inverter_count = BarcodeImage.objects.filter(AssignTo_id=company.new_customer_id,
#                                                                       product_name="Inverter").count()
#                 print(deployed_inverter_count)
#                 remaining_inverter_count = company.qunt_inv - deployed_inverter_count
#                 company.remaining_inverter_count = remaining_inverter_count
#
#                 # Filter companies based on remaining_inverter_count
#         filtered_companies = [company for company in companies if company.remaining_inverter_count > 0]
#
#
#
#         print(request.POST)
#         print(request.FILES)
#
#     context = {
#         'detected_count': detected_count,
#         'non_detected_count': non_detected_count,
#         'duplicate_count': duplicate_count,
#         'valid_barcodes': valid_barcodes,
#         'filtered_companies': filtered_companies,
#         'count1': count1,
#         'notification1': notification1,
#         'companies': companies,
#         'selected_company_name': selected_company_name,  # Pass the selected company name to the template
#         'uploaded_count': uploaded_count,
#     }
#     return render(request, 'detect_barcodes/serial_barcode_inverter.html', context)


def upload_and_display_view_inverter(request):
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    detected_count = None
    non_detected_count = None
    duplicate_count = None
    valid_barcodes = None
    companies = Customer.objects.all()
    selected_company_name = None
    uploaded_count = None
    filtered_companies = []  # Initialize with an empty list

    # Determine the product_name based on the template being used
    for company in companies:
        deployed_inverter_count = BarcodeImage.objects.filter(AssignTo_id=company.new_customer_id,
                                                              product_name="Inverter").count()
        print(deployed_inverter_count)
        remaining_inverter_count = company.qunt_inv - deployed_inverter_count
        company.remaining_inverter_count = remaining_inverter_count

    # Filter companies based on remaining_inverter_count
    filtered_companies = [company for company in companies if company.remaining_inverter_count > 0]

    print("Filtered Companies:", filtered_companies)
    # print(request.POST)
    # print(request.FILES)

    if request.method == 'POST':
        images = request.FILES.getlist('images')
        company = request.POST.get('solarPlateCompany')
        wattage = request.POST.get('wattage')
        comp_name = request.POST.get('comp_name')
        if comp_name:
            customer = Customer.objects.get(new_customer_id=comp_name)
            company_name = customer.Comp_name
            selected_company_name = company_name  # Set the selected company name
        product_name = None

        # Determine the product_name based on the template being used
        if request.path == '/detect_barcodes/serial_barcode/':
            product_name = 'SolarPanel'
        elif request.path == '/detect_barcodes/serial_barcode_inverter/':
            product_name = 'Inverter'

        AssignBy = request.user.id
        AssignTo_id = request.POST.get('new_customer_id')

        detected_count, non_detected_count, duplicate_count, valid_barcodes = process_and_save_barcodes(
            images, company, wattage, comp_name, product_name, AssignBy, AssignTo_id, company_name
        )

        uploaded_count = len(images)
        detected_count = detected_count
        duplicate_count = duplicate_count
        non_detected_count = non_detected_count


    context = {
        'detected_count': detected_count,
        'non_detected_count': non_detected_count,
        'duplicate_count': duplicate_count,
        'valid_barcodes': valid_barcodes,
        'filtered_companies': filtered_companies,
        'count1': count1,
        'notification1': notification1,
        'companies': companies,
        'selected_company_name': selected_company_name,  # Pass the selected company name to the template
        'uploaded_count': uploaded_count,
    }
    return render(request, 'detect_barcodes/serial_barcode_inverter.html', context)




def search_barcode(request):
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    barcode_image = None
    customer = None

    if request.method == 'POST':
        barcode_value = request.POST.get('barcode_value', '')
        # Assume barcode_value is the barcode you are searching for
        try:
            barcode_image = BarcodeImage.objects.get(barcode_data=barcode_value)
            customer = Customer.objects.get(new_customer_id=barcode_image.AssignTo)
        except (BarcodeImage.DoesNotExist, Customer.DoesNotExist):
            barcode_image = None
            customer = None

    return render(request, 'detect_barcodes/search_results.html', {'barcode_image': barcode_image, 'customer': customer, 'count1': count1,
        'notification1': notification1})


