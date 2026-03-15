

import time
from datetime import datetime
from urllib import response

import barcode
from dateutil.relativedelta import relativedelta
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

from customer.models import Customer, Meters, GenerationMeter, GenerationCT, MSEB, SolarPump
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
        # print('Ajax request received')
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




def detect_barcode(request):
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')

    if request.method == 'POST':
        barcode_option = request.POST.get('barcodeOption')  # Get the selected barcode option
        # print("barcodeOption", barcode_option)
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

                            # Update the Customer table's solar_name field
                            customer.solar_comp = company
                            customer.save()

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
            # print("barcodeOption", barcode_option)
            # serial_numbers = request.POST.get('serial')
            # serial_numbers = json.loads(serial_numbers_str) if serial_numbers_str else []
            serial_numbers_str = request.POST.get('serialNumbers')
            serial_numbers = json.loads(serial_numbers_str) if serial_numbers_str else []

            detected_barcodes = []
            # print("serial_numbers", serial_numbers)
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

                # Update the Customer table's solar_name field
                customer.solar_comp = company
                customer.save()

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

                        # Update the Customer table's solar_name field
                        customer.UPSC = company
                        customer.save()

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



@login_required(login_url='user-login')
def get_customer_details(request):
    if request.method == 'GET':
        new_customer_id = request.GET.get('new_customer_id')
        if new_customer_id:
            customer = Customer.objects.filter(new_customer=new_customer_id).first()
            # print(new_customer_id)
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



@login_required(login_url='user-login')
def search_view(request):
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    # companies = BarcodeImage.objects.values_list('company', flat=True).distinct()
    companies = BarcodeImage.objects.values_list('company', flat=True).distinct().order_by('company')
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



from PIL import Image



@login_required(login_url='user-login')
def GeneratePDF(request):
        selected_company = request.POST.get('selected_company')
        selected_product = request.POST.get('selected_product')
        # selected_company = request.POST.get('selectedCompanySpan')
        # selected_product = request.POST.get('selectedProduct')
        invoice_number = request.POST.get('invoice_number')
        # print("Selected Company:", selected_company)  # Print the value for debugging
        # print("selected_product:", selected_product)  # Print the value for debugging
        selected_no = request.POST.get('selected_no')  # Get the selected radio button value
        # print("selected_no:", selected_no)

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



        # Get the Profile object associated with the selected company
        customer = Customer.objects.filter(Comp_name=selected_company).first()

        user = items.first().AssignTo_id  # Assuming AssignTo is a ForeignKey to User model
        profile = Profile.objects.get(customer_id=user)
        date = datetime.now()
        # date1 = datetime.today().strftime("%d /%m /%Y")
        date1 = datetime.today().strftime("%d %b %Y")
        # image_url = request.build_absolute_uri(settings.MEDIA_URL + 'static/images/dblogo2001.png')
        context = {
            # 'image_url': image_url,
            'date': date,
            'date1': date1,
            'profile': profile,
            'customer': customer,
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



from django.shortcuts import render, redirect
from django.db.models import Count
from .models import BarcodeImage  # Import your BarcodeImage model


@login_required(login_url='user-login')
def editbarcode(request):
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    # companies = BarcodeImage.objects.values_list('company', flat=True).distinct()
    companies = BarcodeImage.objects.values_list('company', flat=True).distinct().order_by('company')
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
                        # print(f'Company Name updated: {barcode_image.company_name} -> {company_name}')
                        barcode_image.company_name = company_name
                    if barcode_image.wattage != wattage:
                        # print(f'Wattage updated: {barcode_image.wattage} -> {wattage}')
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


from django.shortcuts import render, get_object_or_404
from .models import Customer
from django.db.models import F, ExpressionWrapper, DurationField
from datetime import datetime, timedelta

@login_required(login_url='user-login')
def displayproduct(request):
    # global remaining_days_inv_warranty
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    # companies = BarcodeImage.objects.values_list('company', flat=True).distinct()
    companies = BarcodeImage.objects.values_list('company', flat=True).distinct().order_by('company')
    product_names = BarcodeImage.objects.values_list('product_name', flat=True).distinct()
    items1 = BarcodeImage.objects.all()
    progress_warranty = {}
    # solar Panel ,Inverter, Replace Code
    # Inside the view function
    current_date = datetime.now().date()
    remaining_days_inv_warranty = None  # Initialize with None
    remaining_days_sol_warranty = None
    remaining_days_com_warranty = None
    installation_date1 = None  # Initialize with None

    items = []
    solar_items = []
    inverter_items = []
    replace_items = []
    solar_panel_total_quantity = 0
    solar_panel_quantity_by_wattage = []
    waterpump_panel_total_quantity = 0
    waterpump_panel_quantity_by_wattage = []
    unique_wattages = []
    inverter_wattages = []
    inverter_panel_quantity_by_wattage = []
    inverter_panel_total_quantity = 0
    replace_wattages = []
    replace_panel_quantity_by_wattage = []
    replace_panel_total_quantity = 0
    user_record = Customer.objects.get(new_customer_id=request.user.id)
    # selected_company = user_record.Comp_name
    # items = BarcodeImage.objects.filter(company=selected_company)
    selected_company = user_record.new_customer
    items = BarcodeImage.objects.filter(AssignTo=selected_company)
    items_pump = SolarPump.objects.filter(AssignTo=selected_company)
    solar_items = items.filter(product_name='SolarPanel')
    inverter_items = items.filter(product_name='Inverter')
    replace_items = items.filter(product_name='Replace')
    waterpump_items = items_pump.filter(item_type='Water Pump')
    solar_panel_total_quantity = solar_items.count()
    solar_panel_quantity_by_wattage = solar_items.values('wattage').annotate(total_quantity=Count('id'))
    inverter_panel_total_quantity = inverter_items.count()
    inverter_panel_quantity_by_wattage = inverter_items.values('wattage').annotate(total_quantity=Count('id'))
    replace_panel_total_quantity = replace_items.count()
    replace_panel_quantity_by_wattage = replace_items.values('wattage').annotate(total_quantity=Count('id'))
    waterpump_panel_total_quantity = waterpump_items.count()
    waterpump_panel_quantity_by_wattage = waterpump_items.values('pump_hp').annotate(total_quantity=Count('id'))

    unique_wattages = {item['wattage'] for item in solar_panel_quantity_by_wattage}
    inverter_wattages = {item['wattage'] for item in inverter_panel_quantity_by_wattage}
    replace_wattages = {item['wattage'] for item in replace_panel_quantity_by_wattage}
    waterpump_wattages = {item['pump_hp'] for item in waterpump_panel_quantity_by_wattage}

    # Generation Meter Details
    user_record = Customer.objects.get(new_customer_id=request.user.id)
    selected_comp_name = user_record.Comp_name
    # print(selected_comp_name)

    meters_records = Meters.objects.filter(comp_name=selected_comp_name)
    generation_meter_records = GenerationMeter.objects.filter(comp_name=selected_comp_name)
    generation_ct_records = GenerationCT.objects.filter(comp_name=selected_comp_name)

    # CODE FOr MSEB Status
    customer = get_object_or_404(Customer, new_customer_id=request.user.id)
    # customer = Customer.objects.filter(new_customer_id=request.user.id)
    mseb_data = MSEB.objects.filter(customer=customer).first()
    records = MSEB.objects.filter(customer=customer).first()
    progress_data = None
    # CODE FOR MSEB Status
    customer = get_object_or_404(Customer, new_customer_id=request.user.id)
    mseb_data = MSEB.objects.filter(customer=customer).first()



    # installation_date1 = mseb_data.installation_date  # Assuming installation_date is the field name
    # print(installation_date1)
    if mseb_data is not None:
        installation_date1 = mseb_data.installation_date  # Assuming installation_date is the field name
        records = mseb_data
        progress_data = {}
        current_load = int(customer.current_load)  # Parse to integer
        loadsancution = int(customer.loadsancution)  # Parse to integer


        # Check if both values are equal
        if current_load == loadsancution:
            field_mapping = {
                'net_meter': 'Net Metering',
                'flexibility': 'Technical Feasibility',
                'approval': 'Approval',
                'meter_testing': 'Meter Testing',
                'agreement': 'NetMeter Agreement.',
                'release': 'Meter Release',
                'installation_date': 'Meter Installation Date',
            }
        else:
            field_mapping = {
                'load_extension': 'Load Extension',
                'flisibility': 'Off-Line Feasibility',
                'quotation': 'Firm Quotation Gen.',
                'sent_to_bill': 'Sent to Bill',
                'net_meter': 'Net Metering',
                'flexibility': 'Technical Feasibility',
                'approval': 'Approval',
                'meter_testing': 'Meter Testing',
                'agreement': 'NetMeter Agreement.',
                'release': 'Meter Release',
                'installation_date': 'Meter Installation Date',
            }

        # Constructing progress data with display names
        for field, value in mseb_data.__dict__.items():
            if field in field_mapping:
                progress_data[field_mapping[field]] = {
                    'value': value,
                    'date': getattr(mseb_data, f"{field}_date") if f"{field}_date" in mseb_data.__dict__ else None
                }
                # Calculate warranty end dates
                installation_date = mseb_data.installation_date_date
                if installation_date:
                    inv_warranty_years = customer.inv_warranty
                    sol_warranty_years = customer.sol_warranty
                    com_warranty_years = customer.com_warranty
                    waterpump_warranty_years = customer.pump_warranty

                    # if inv_warranty_years:
                    #     inv_warranty_end_date = installation_date + timedelta(
                    #         days=365 * inv_warranty_years) - timedelta(days=1)
                    #     progress_warranty['Inverter Warranty'] = {
                    #         'value': True,
                    #         'date': inv_warranty_end_date
                    #     }
                    if sol_warranty_years:
                        installation_date_date = mseb_data.installation_date_date.date()  # Convert to datetime.date
                        sol_warranty_end_date = installation_date_date + timedelta(
                            days=365 * sol_warranty_years) - timedelta(days=1)
                        remaining_days_sol_warranty = (sol_warranty_end_date - current_date).days + 1
                        progress_warranty['Solar Module Warranty'] = {
                            'value': True,
                            'date': sol_warranty_end_date,
                            'remaining_days': remaining_days_sol_warranty
                        }



                    if inv_warranty_years:
                        installation_date_date = mseb_data.installation_date_date.date()  # Convert to datetime.date
                        inv_warranty_end_date = installation_date_date + timedelta(
                            days=365 * inv_warranty_years) - timedelta(days=1)
                        remaining_days_inv_warranty = (inv_warranty_end_date - current_date).days + 1
                        progress_warranty['Inverter Warranty'] = {
                            'value': True,
                            'date': inv_warranty_end_date,
                            'remaining_days': remaining_days_inv_warranty
                        }


                    if waterpump_warranty_years:
                        installation_date_date = mseb_data.installation_date_date.date()  # Convert to datetime.date
                        waterpump_warranty_end_date = installation_date_date + timedelta(
                            days=365 * waterpump_warranty_years) - timedelta(days=1)
                        remaining_days_waterpump_warranty = (waterpump_warranty_end_date - current_date).days + 1
                        progress_warranty['Solar Water Pump Warranty'] = {
                            'value': True,
                            'date': waterpump_warranty_end_date,
                            'remaining_days': remaining_days_waterpump_warranty
                        }


                    # if sol_warranty_years:
                    #     sol_warranty_end_date = installation_date + timedelta(
                    #         days=365 * sol_warranty_years) - timedelta(days=1)
                    #     progress_warranty['Solar Warranty'] = {
                    #         'value': True,
                    #         'date': sol_warranty_end_date
                    #     }
                    #
                    # if com_warranty_years:
                    #     com_warranty_end_date = installation_date + timedelta(
                    #         days=365 * com_warranty_years) - timedelta(days=1)
                    #     progress_warranty['O & M Warranty'] = {
                    #         'value': True,
                    #         'date': com_warranty_end_date
                    #     }


                    if com_warranty_years:
                        installation_date_date = mseb_data.installation_date_date.date()  # Convert to datetime.date
                        com_warranty_end_date = installation_date_date + timedelta(
                            days=365 * com_warranty_years) - timedelta(days=1)

                        remaining_days_com_warranty = (com_warranty_end_date - current_date).days + 1
                        progress_warranty['O & M Warranty'] = {
                            'value': True,
                            'date': com_warranty_end_date,
                            'remaining_days': remaining_days_com_warranty
                        }

    else:
        records = None
        progress_data = {}


    return render(request, 'detect_barcodes/display_product.html',
                  {'companies': companies, 'product_names': product_names, 'items': items,
                   'solar_items': solar_items, 'inverter_items': inverter_items, 'replace_items': replace_items,
                   'waterpump_items': waterpump_items,
                   'solar_panel_total_quantity': solar_panel_total_quantity,
                   'solar_panel_quantity_by_wattage': solar_panel_quantity_by_wattage,
                   'unique_wattages': unique_wattages, 'inverter_wattages': inverter_wattages,
                   'inverter_panel_total_quantity': inverter_panel_total_quantity,
                   'inverter_panel_quantity_by_wattage': inverter_panel_quantity_by_wattage, 'items1': items1,
                   'replace_panel_total_quantity': replace_panel_total_quantity,
                   'replace_panel_quantity_by_wattage': replace_panel_quantity_by_wattage,
                   'replace_wattages': replace_wattages,
                   'waterpump_panel_total_quantity': waterpump_panel_total_quantity,
                   'waterpump_panel_quantity_by_wattage': waterpump_panel_quantity_by_wattage,
                   'waterpump_wattages': waterpump_wattages,
                   'notification1': notification1,
                   'count1': count1,
                   'user_record': user_record,
                   'meters_records': meters_records,
                   'generation_meter_records': generation_meter_records,
                   'generation_ct_records': generation_ct_records,
                   'selected_comp_name': selected_comp_name,
                   'customer': customer, 'progress_data': progress_data, 'records': records,
                   'progress_warranty': progress_warranty,
                   'mseb_installation_date': installation_date1,
                   'remaining_days_inv_warranty': remaining_days_inv_warranty,

                   })



@login_required(login_url='user-login')
def displaywarranty(request):
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')

    current_date = datetime.now().date()
    progress_warranty = {}

    # Retrieve all Customer objects
    customers = Customer.objects.all()

    for customer in customers:
        # Retrieve corresponding MSEB data for each customer
        mseb_data = MSEB.objects.filter(customer=customer).first()
        if mseb_data:
            installation_date = mseb_data.installation_date_date
            if installation_date:
                com_warranty_years = customer.com_warranty
                inv_warranty_years = customer.inv_warranty
                sol_warranty_years = customer.sol_warranty
                if com_warranty_years:
                    installation_date_date = installation_date.date()
                    com_warranty_end_date = installation_date_date + timedelta(days=365 * com_warranty_years) - timedelta(days=1)
                    remaining_days_com_warranty = (com_warranty_end_date - current_date).days + 1

                    inv_warranty_end_date = installation_date_date + timedelta(days=365 * inv_warranty_years) - timedelta(days=1)
                    remaining_days_inv_warranty = (inv_warranty_end_date - current_date).days + 1

                    sol_warranty_end_date = installation_date_date + timedelta(days=365 * sol_warranty_years) - timedelta(days=1)
                    remaining_days_sol_warranty = (sol_warranty_end_date - current_date).days + 1

                    # Add warranty details to the progress_warranty dictionary with company name as key
                    progress_warranty[mseb_data.comp_name] = {
                        'comp_name': mseb_data.comp_name,
                        'phone': mseb_data.customer.phone,
                        'City': mseb_data.customer.City,
                        'Plant_Capacity': mseb_data.customer.Plant_Capacity,
                        'date_com': com_warranty_end_date,
                        'date_inv': inv_warranty_end_date,
                        'date_sol': sol_warranty_end_date,
                        'remaining_days_com': remaining_days_com_warranty,
                        'remaining_days_inv': remaining_days_inv_warranty,
                        'remaining_days_sol': remaining_days_sol_warranty,
                    }

    # Filter the MSEB data based on different warranty criteria
    all_warranty = {comp_name: data for comp_name, data in progress_warranty.items()}
    remaining_30_days = {comp_name: data for comp_name, data in progress_warranty.items() if data['remaining_days_com'] <= 30 and data['remaining_days_com'] > 0}
    remaining_15_days = {comp_name: data for comp_name, data in progress_warranty.items() if data['remaining_days_com'] <= 15 and data['remaining_days_com'] > 0}
    expired_warranty = {comp_name: data for comp_name, data in progress_warranty.items() if data['remaining_days_com'] <= 0}

    # Count the total number of warranty details and companies in each category
    total_warranty_count = len(all_warranty)
    remaining_30_days_count = len(remaining_30_days)
    remaining_15_days_count = len(remaining_15_days)
    expired_warranty_count = len(expired_warranty)

    return render(request, 'detect_barcodes/display_warranty.html', {
        'all_warranty': all_warranty,
        'remaining_30_days': remaining_30_days,
        'remaining_15_days': remaining_15_days,
        'expired_warranty': expired_warranty,
        'total_warranty_count': total_warranty_count,
        'remaining_30_days_count': remaining_30_days_count,
        'remaining_15_days_count': remaining_15_days_count,
        'expired_warranty_count': expired_warranty_count,
        'notification1': notification1,
        'count1': count1,
    })


from django.shortcuts import render, redirect
from django.db.models import Count
from .models import BarcodeImage  # Import your BarcodeImage model

from django.shortcuts import render, redirect
from django.db.models import Count
from .models import BarcodeImage  # Import your BarcodeImage model


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



def deletebarcode(request):
    count1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).count()
    notification1 = staff_Notification.objects.filter(staff_id=request.user.id, status=False).order_by('-created_at')
    # companies = BarcodeImage.objects.values_list('company', flat=True).distinct()
    companies = BarcodeImage.objects.values_list('company', flat=True).distinct().order_by('company')
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


    if request.method == 'POST':
        selected_company = request.POST.get('company')
        selected_product = request.POST.get('product')

        if 'selected_items' in request.POST:
            selected_item_ids = request.POST.getlist('selected_items')
            selected_items = BarcodeImage.objects.filter(pk__in=selected_item_ids)
            return render(request, 'detect_barcodes/selected_records.html', {'selected_items': selected_items})

    if 'confirm_delete' in request.POST:
        selected_item_ids = request.POST.getlist('selected_item_ids')  # Note the change here
        selected_items = BarcodeImage.objects.filter(pk__in=selected_item_ids)

        for item in selected_items:
            # Construct the path to the image file
            image_path = os.path.join(settings.MEDIA_ROOT, item.image.name) if item.image else None

            # Check if the file exists and delete it
            if image_path and os.path.exists(image_path):
                os.remove(image_path)
                # print(f"Image file exist at {image_path}")
            elif image_path:
                print(f"Image file does not exist at {image_path}")

            # Check if barcode_path is not None and not an empty string
            barcode_path = item.barcode_path.path if item.barcode_path else None
            if barcode_path and os.path.exists(barcode_path):
                os.remove(barcode_path)
                # print(f"Barcode file exist at {barcode_path}")
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
    # print("Received image data:", image_data)
    decoded_data = decode_image(image_data)
    # print("Decoded data:", decoded_data)
    return JsonResponse({'barcode_value': decoded_data})

def decode_image(image_data):
    image_bytes = base64.b64decode(image_data.split(',')[1])
    img = Image.open(BytesIO(image_bytes))
    decoded_data = decode(img)
    if decoded_data:
        return decoded_data[0].data.decode('utf-8')
    else:
        return None


# views.py
from django.shortcuts import render
from .models import BarcodeImage
from PIL import Image
import pytesseract
import re

# Set the Tesseract executable path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# Set the Tesseract executable path for PythonAnywhere
# pytesseract.pytesseract.tesseract_cmd = 'tesseract'

def barcode_exists(barcode):
    return BarcodeImage.objects.filter(barcode_data=barcode).exists()


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
                                # print(f"Saved Barcode: {cleaned_barcode} for Company: {company}")

                                # Update the Customer table based on product_name
                                customer = Customer.objects.get(new_customer_id=AssignTo_id)
                                if product_name == 'SolarPanel':
                                    customer.solar_comp = company
                                elif product_name == 'Inverter':
                                    customer.UPSC = company
                                customer.save()

                            else:
                                duplicate_count += 1
                                valid_barcodes.append(
                                    (cleaned_barcode, 'Duplicate', None, None, None, None))
                                # print(f"Duplicate Barcode: {cleaned_barcode}")
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
                            # print(f"Saved Barcode: {cleaned_barcode} for Company: {company}")

                            # Update the Customer table based on product_name
                            customer = Customer.objects.get(new_customer_id=AssignTo_id)
                            if product_name == 'SolarPanel':
                                customer.solar_comp = company
                            elif product_name == 'Inverter':
                                customer.UPSC = company
                            customer.save()
                        else:
                            duplicate_count += 1
                            valid_barcodes.append(
                                (cleaned_barcode, 'Duplicate', None, None, None, None))
                            # print(f"Duplicate Barcode: {cleaned_barcode}")
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
    # print(request.POST)
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


def get_project_type(request, customer_id):
    try:
        customer = Customer.objects.get(new_customer=customer_id)
        return JsonResponse({"project_type": customer.project_type})
    except Customer.DoesNotExist:
        return JsonResponse({"error": "Customer not found"}, status=404)

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
        # print(f"Saved Barcode: {barcode_serial_number} for Company: {company}")

        # Update the Customer table based on product_name
        customer = Customer.objects.get(new_customer_id=AssignTo_id)
        if product_name == 'SolarPanel':
            customer.solar_comp = company
        elif product_name == 'Inverter':
            customer.UPSC = company
        customer.save()

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

# Set the Tesseract executable path for PythonAnywhere
# pytesseract.pytesseract.tesseract_cmd = 'tesseract'

def barcode_exists(barcode):
    return BarcodeImage.objects.filter(barcode_data=barcode).exists()



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
                                # print(f"Saved Barcode: {cleaned_barcode} for Company: {company}")

                                # Update the Customer table based on product_name
                                customer = Customer.objects.get(new_customer_id=AssignTo_id)
                                if product_name == 'SolarPanel':
                                    customer.solar_comp = company
                                elif product_name == 'Inverter':
                                    customer.UPSC = company
                                customer.save()


                            else:
                                duplicate_count += 1
                                valid_barcodes.append(
                                    (cleaned_barcode, 'Duplicate', None, None, None, None))
                                # print(f"Duplicate Barcode: {cleaned_barcode}")
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

                            valid_barcodes.append(
                                (cleaned_barcode, 'Detect', barcode_image, file_saved_at, company, wattage))
                            # print(f"Saved Barcode: {cleaned_barcode} for Company: {company}")

                            # Update the Customer table based on product_name
                            customer = Customer.objects.get(new_customer_id=AssignTo_id)
                            if product_name == 'SolarPanel':
                                customer.solar_comp = company
                            elif product_name == 'Inverter':
                                customer.UPSC = company
                            customer.save()

                        else:
                            duplicate_count += 1
                            valid_barcodes.append(
                                (cleaned_barcode, 'Duplicate', None, None, None, None))
                            # print(f"Duplicate Barcode: {cleaned_barcode}")
                    else:
                        non_detected_count += 1

        except (pytesseract.TesseractError, Exception) as e:
            print(str(e))

    return detected_count, non_detected_count, duplicate_count, valid_barcodes


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
        # print(deployed_inverter_count)
        remaining_inverter_count = company.qunt_inv - deployed_inverter_count
        company.remaining_inverter_count = remaining_inverter_count

    # Filter companies based on remaining_inverter_count
    filtered_companies = [company for company in companies if company.remaining_inverter_count > 0]

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



from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef, Q


@login_required

def promote_view(request):

    """
    Promote view:
    - Show only customers who still need Solar Panel or Inverter.
    - Dynamically list subcategories and stocks that still have available (unassigned) serial numbers.
    """

    available_customer_ids = []
    available_customer_subcat_map = {}

    # STEP 1 — Build eligible customers & available subcategories dynamically
    for cust in Customer.objects.all():
        assigned_solar = BarcodeImage.objects.filter(
            AssignTo=cust.new_customer, product_name="SolarPanel"
        ).count()
        assigned_inv = BarcodeImage.objects.filter(
            AssignTo=cust.new_customer, product_name="Inverter"
        ).count()

        required_solar = cust.qunt_solar or 0
        required_inv = cust.qunt_inv or 0

        # Skip if fully satisfied
        if assigned_solar >= required_solar and assigned_inv >= required_inv:
            continue

        # Sale items for this customer
        salebills = SaleBill.objects.filter(Cust_id=cust)
        saleitems = SaleItem.objects.filter(billno__in=salebills)
        sold_stock_ids = list(saleitems.values_list("stock_id", flat=True))

        if not sold_stock_ids:
            continue

        used_serials = list(
            BarcodeImage.objects.filter(AssignTo=cust.new_customer)
            .values_list("barcode_data", flat=True)
        )

        # Find available serials sold to this customer
        available_serials_qs = PurchaseSerial.objects.filter(
            stock_id__in=sold_stock_ids,
            sales_billno__Cust_id=cust,
            serialNo__isnull=False,
            return_bill_id__isnull=True,
        ).exclude(serialNo__in=used_serials)

        if not available_serials_qs.exists():
            continue

        # Collect available stock IDs
        available_stock_ids = list(
            available_serials_qs.values_list("stock_id", flat=True).distinct()
        )

        pending_subcat_ids = set()

        # Check Solar Panels
        if required_solar > assigned_solar:
            solar_stocks_qs = Stock.objects.filter(
                id__in=available_stock_ids, subcategory__name="Solar Module Panels"
            )
            if PurchaseSerial.objects.filter(
                stock__in=solar_stocks_qs,
                sales_billno__Cust_id=cust,
                serialNo__isnull=False,
                return_bill_id__isnull=True,
            ).exclude(serialNo__in=used_serials).exists():
                pending_subcat_ids.update(
                    solar_stocks_qs.values_list("subcategory_id", flat=True)
                )

        # Check Inverter
        if required_inv > assigned_inv:
            inverter_stocks_qs = Stock.objects.filter(
                id__in=available_stock_ids, subcategory__name="Inverter"
            )
            if PurchaseSerial.objects.filter(
                stock__in=inverter_stocks_qs,
                sales_billno__Cust_id=cust,
                serialNo__isnull=False,
                return_bill_id__isnull=True,
            ).exclude(serialNo__in=used_serials).exists():
                pending_subcat_ids.update(
                    inverter_stocks_qs.values_list("subcategory_id", flat=True)
                )

        # If any valid subcategory found
        if pending_subcat_ids:
            available_customer_ids.append(cust.Cust_id)
            available_customer_subcat_map[cust.Cust_id] = list(pending_subcat_ids)

    # Customers for dropdown
    customers = Customer.objects.filter(Cust_id__in=available_customer_ids)

    # -------------------- Handle GET parameters --------------------
    selected_customer_id = request.GET.get("customer")
    selected_subcategory = request.GET.get("subcategory")
    selected_stock_ids = request.GET.getlist("stocks")

    try:
        selected_stock_ids_int = [int(x) for x in selected_stock_ids if x.isdigit()]
    except Exception:
        selected_stock_ids_int = []

    try:
        sel_cust_id_int = int(selected_customer_id) if selected_customer_id else None
        if sel_cust_id_int not in available_customer_ids:
            selected_customer_id = None
            sel_cust_id_int = None
    except Exception:
        selected_customer_id = None
        sel_cust_id_int = None

    # -------------------- Initialize template vars --------------------
    customer = None
    subcategories = SubCategory.objects.none()
    stocks = Stock.objects.none()
    serials = PurchaseSerial.objects.none()
    serials_with_checkboxes = []
    existing_serials = BarcodeImage.objects.none()
    summary_product = None
    summary_count = 0
    summary_required = 0
    summary_pending = 0
    show_serial_tables = False
    valid_subcategory = False

    # -------------------- Customer selected --------------------
    if sel_cust_id_int:
        try:
            customer = Customer.objects.get(Cust_id=sel_cust_id_int)
            assigned_to_user = customer.new_customer

            qunt_solar = customer.qunt_solar or 0
            qunt_inv = customer.qunt_inv or 0

            existing_solar = BarcodeImage.objects.filter(
                AssignTo=assigned_to_user, product_name="SolarPanel"
            ).count()
            existing_inv = BarcodeImage.objects.filter(
                AssignTo=assigned_to_user, product_name="Inverter"
            ).count()

            # Possible subcategories
            possible_subcat_ids = available_customer_subcat_map.get(customer.Cust_id, [])
            used_serials_for_customer = list(
                BarcodeImage.objects.filter(AssignTo=assigned_to_user)
                .values_list("barcode_data", flat=True)
            )

            # Re-validate subcategories dynamically (fresh)
            valid_subcat_ids = []
            for sub_id in possible_subcat_ids:
                if PurchaseSerial.objects.filter(
                    stock__subcategory_id=sub_id,
                    sales_billno__Cust_id=customer,
                    serialNo__isnull=False,
                    return_bill_id__isnull=True,
                ).exclude(serialNo__in=used_serials_for_customer).exists():
                    valid_subcat_ids.append(sub_id)

            subcategories = SubCategory.objects.filter(id__in=valid_subcat_ids)

            # Subcategory selected?
            if selected_subcategory:
                try:
                    selected_subcategory_id = int(selected_subcategory)
                except Exception:
                    selected_subcategory_id = None

                valid_subcategory = (
                    subcategories.filter(id=selected_subcategory_id).exists()
                    if selected_subcategory_id
                    else False
                )

                if valid_subcategory:
                    # All sold stocks for this customer
                    salebills = SaleBill.objects.filter(Cust_id=customer)
                    saleitems = SaleItem.objects.filter(billno__in=salebills)
                    sold_stock_ids = list(
                        saleitems.values_list("stock_id", flat=True)
                    )

                    # Stocks for selected subcategory
                    stocks_qs = Stock.objects.filter(
                        id__in=sold_stock_ids, subcategory_id=selected_subcategory_id
                    )

                    # ✅ FIXED: Only keep stocks with *remaining* unassigned serials
                    available_serials_subquery = PurchaseSerial.objects.filter(
                        stock=OuterRef("pk"),
                        sales_billno__Cust_id=customer,
                        serialNo__isnull=False,
                        return_bill_id__isnull=True,
                    ).exclude(serialNo__in=used_serials_for_customer)

                    stocks_with_available_serials = stocks_qs.annotate(
                        has_available_serial=Exists(available_serials_subquery)
                    ).filter(has_available_serial=True)

                    stocks = stocks_with_available_serials

                    # Hide stocks if fully assigned
                    selected_subcat_obj = SubCategory.objects.get(
                        id=selected_subcategory_id
                    )
                    subcat_name = selected_subcat_obj.name.strip()

                    if subcat_name == "Solar Module Panels" and existing_solar >= qunt_solar:
                        stocks = Stock.objects.none()
                    elif subcat_name == "Inverter" and existing_inv >= qunt_inv:
                        stocks = Stock.objects.none()

                    if stocks.exists():
                        map_prod = {
                            "Solar Module Panels": "SolarPanel",
                            "Inverter": "Inverter",
                        }
                        summary_product = map_prod.get(subcat_name, subcat_name)

                        if summary_product == "SolarPanel":
                            summary_required = qunt_solar
                            summary_count = existing_solar
                        elif summary_product == "Inverter":
                            summary_required = qunt_inv
                            summary_count = existing_inv

                        summary_pending = max(0, summary_required - summary_count)

                        existing_serials = BarcodeImage.objects.filter(
                            AssignTo=assigned_to_user, product_name=summary_product
                        )

                        # Selected stocks → show available serials
                        if selected_stock_ids_int:
                            serials = PurchaseSerial.objects.filter(
                                stock_id__in=selected_stock_ids_int,
                                stock__subcategory_id=selected_subcategory_id,
                                sales_billno__Cust_id=customer,
                                serialNo__isnull=False,
                                return_bill_id__isnull=True,
                            ).exclude(serialNo__in=used_serials_for_customer)

                            serials_with_checkboxes = [
                                {"id": s.id, "serialNo": s.serialNo, "checked": False}
                                for s in serials
                            ]

                        show_serial_tables = True

        except Customer.DoesNotExist:
            customer = None
            selected_customer_id = None

    # Attach available subcategories per customer
    for cust in customers:
        subcat_ids = available_customer_subcat_map.get(cust.Cust_id, [])
        cust.available_subcategories = SubCategory.objects.filter(id__in=subcat_ids)

    # -------------------- Render --------------------
    context = {
        "customers": customers,
        "selected_customer_id": selected_customer_id,
        "subcategories": subcategories,
        "selected_subcategories": [selected_subcategory] if selected_subcategory and valid_subcategory else [],
        "stocks": stocks,
        "selected_stock_ids": selected_stock_ids,
        "serials": serials,
        "serials_with_checkboxes": serials_with_checkboxes,
        "existing_serials": existing_serials,
        "summary_product": summary_product,
        "summary_count": summary_count,
        "summary_required": summary_required,
        "summary_pending": summary_pending,
        "show_serial_tables": show_serial_tables,
    }

    return render(request, "detect_barcodes/promote.html", context)




@login_required
def save_selected_serials(request):
    if request.method == 'POST':
        serial_ids = request.POST.getlist('serial_ids[]')

        # If serial_ids list contains a single string with commas, split it
        if len(serial_ids) == 1 and ',' in serial_ids[0]:
            serial_ids = serial_ids[0].split(',')

        customer_id = request.POST.get('customer_id')
        subcategory_ids = request.POST.getlist('subcategory[]')
        company_name = request.POST.get('company_name', '')
        wattage = request.POST.get('wattage', '')

        try:
            customer = Customer.objects.get(Cust_id=customer_id)
        except Customer.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Customer not found'})

        assign_by = request.user.id
        assign_to_user = customer.new_customer

        count = 0
        for sid in serial_ids:
            try:
                sid = sid.strip()
                serial_obj = PurchaseSerial.objects.get(id=int(sid))
                stock = serial_obj.stock
                subcat = stock.subcategory.name.strip() if stock.subcategory else ""

                if subcat == 'Solar Module Panels':
                    product_name = 'SolarPanel'
                elif subcat == 'Inverter':
                    product_name = 'Inverter'
                else:
                    product_name = subcat

                tz = pytz.timezone('Asia/Kolkata')
                file_saved_at = timezone.now().astimezone(tz)

                BarcodeImage.objects.create(
                    barcode_data=serial_obj.serialNo,
                    file_saved_at=file_saved_at,
                    company=customer.Comp_name,
                    AssignTo=assign_to_user,
                    AssignBy=assign_by,
                    product_name=product_name,
                    company_name=company_name,
                    wattage=wattage
                )

                count += 1

            except Exception as e:
                print(f"Error processing serial id {sid}: {e}")
                continue

        # ----------------------------------------------------------------------
        # ✅ After serials are saved, check strict equality for Solar + Inverter
        # ----------------------------------------------------------------------
        try:
            from customer.models import Result  # adjust import to match your project

            # ----- Count assigned products -----
            assigned_solar = BarcodeImage.objects.filter(
                AssignTo=assign_to_user,
                product_name="SolarPanel"
            ).count()
            required_solar = customer.qunt_solar or 0

            assigned_inverter = BarcodeImage.objects.filter(
                AssignTo=assign_to_user,
                product_name="Inverter"
            ).count()
            required_inverter = customer.qunt_inv or 0

            # ----- Get or create Result row -----
            result_obj, created = Result.objects.get_or_create(
                consumer_id_id=customer.Cust_id,
                defaults={
                    "consumer": customer.Comp_name,
                    "AssignTo_id": assign_to_user.id,
                    "solar_panel": False,
                    "inverter": False,
                    "net_meter": False,
                    "mseb": False,
                    "solar_pump": False,
                    "inspection_report": False,
                    "controller": False,
                },
            )

            # ----- Update solar_panel flag only if assigned == required -----
            if required_solar > 0 and assigned_solar == required_solar:
                result_obj.solar_panel = True

            # ----- Update inverter flag only if assigned == required -----
            if required_inverter > 0 and assigned_inverter == required_inverter:
                result_obj.inverter = True

            # Save only if any change was made
            if result_obj.solar_panel or result_obj.inverter:
                result_obj.save()

        except Exception as e:
            print(f"⚠️ Error updating Result table for customer {customer_id}: {e}")

        return JsonResponse({'success': True, 'saved_count': count})


