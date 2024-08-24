from django.shortcuts import render, redirect,HttpResponse 
from . models import *
from time import gmtime, strftime
from django.db.models import Sum
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt
from datetime import date
from django.contrib import messages
import datetime
from django.http import JsonResponse
from django.db.models import Q
import json
import requests
import urllib.parse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models.functions import ExtractMonth
import calendar
from django.db.models import Count
from django.shortcuts import redirect, get_object_or_404
# Create your views here.






from decimal import Decimal
import json
from django.core.serializers.json import DjangoJSONEncoder

def custom_404(request, exception):
    return render(request, '404.html',{'error_message': str("Page Not Found")}, status=404)

def index(request):
    try:
        if request.user.is_authenticated:
            user = request.user
            
            # Fetch data for Gueststay model
            subtotalsale = Invoice.objects.filter(vendor=user).aggregate(total_sales=Sum('grand_total_amount'))['total_sales'] or 0
            totaltax = Invoice.objects.filter(vendor=user).aggregate(total_sales=Sum('gst_amount'))['total_sales'] or 0
            subtotalsale = int(subtotalsale)
            totaltax = int(totaltax*2)
            totalsalaryexpance = SalaryManagement.objects.filter(vendor=user).aggregate(total_sales=Sum('basic_salary'))['total_sales'] or 0
            totalsalaryexpance = int(totalsalaryexpance)
            totaltaxandsalary = totalsalaryexpance + totaltax
            totalsalaryexcludedeductions = subtotalsale - totaltaxandsalary
            subtotalsalereal = Invoice.objects.filter(vendor=user).aggregate(total_sales=Sum('subtotal_amount'))['total_sales'] or 0
            # fetch highly hot rooms
            print(subtotalsalereal)
            most_booked_room = Gueststay.objects.filter(vendor=user).values('roomno').annotate(bookings_count=Count('roomno')).order_by('-bookings_count').values_list('roomno', flat=True).first()
            # Fetch monthly sales data for Invoice model
            
            monthly_data = Invoice.objects.filter(vendor=user) \
                                        .annotate(month=ExtractMonth('invoice_date')) \
                                        .values('month') \
                                        .annotate(total_sales=Sum('grand_total_amount')) \
                                        .order_by('month')
            # total amount via cash
            total_cash_amount = Invoice.objects.filter(vendor=user, ).aggregate(total_cash=Sum('cash_amount'))['total_cash'] or 0
            total_online_amount = Invoice.objects.filter(vendor=user,).aggregate(total_cash=Sum('online_amount'))['total_cash'] or 0
            
            # Prepare data for Chart.js
            labels = []
            data = []

            # Prepare a dictionary to hold the sales data for each month
            sales_data = {month: 0 for month in range(1, 13)}
            for entry in monthly_data:
                month = entry['month']
                total_sales = float(entry['total_sales'])  # Convert Decimal to float
                sales_data[month] = total_sales

            # Sort the sales_data dictionary by month and prepare labels and data
            for month, total_sales in sorted(sales_data.items()):
                labels.append(datetime(2024, month, 1).strftime('%b'))
                data.append(total_sales)

            # Simulate the growth percentage
            growth = sum(data) / 12  # Example calculation

            # Convert data to JSON format for Chart.js
            labels_json = json.dumps(labels)
            data_json = json.dumps(data)

            # Calculate total sales for all time
            total_sales_all_time = Invoice.objects.filter(vendor=user) \
                                                .aggregate(total_sales=Sum('grand_total_amount'))['total_sales'] or 0
            
            # Calculate total sales for the last 7 days
            total_sales_last_7_days = Invoice.objects.filter(vendor=user, 
                                                            invoice_date__gte=(datetime.now())-timedelta(days=7)) \
                                                    .aggregate(total_sales=Sum('grand_total_amount'))['total_sales'] or 0
            
            # Calculate sales percentage
            if total_sales_all_time > 0:
                sales_percent = 100 * total_sales_last_7_days / total_sales_all_time
            else:
                sales_percent = 0
            sales_percent = int(sales_percent)
            growth_json = json.dumps(sales_percent)

                    
                        # Get the last Sunday and the upcoming Saturday
            today = datetime.now().date()
            last_sunday = today - timedelta(days=today.weekday() + 1)
            next_saturday = last_sunday + timedelta(days=6)

            # Fetch invoices from last Sunday to next Saturday
            invoices = Invoice.objects.filter(vendor=user, invoice_date__range=[last_sunday, next_saturday])

            # Initialize a list for Sun to Sat with zeros
            weekly_data = [0] * 7

            # Fill the weekly data
            for invoice in invoices:
                day_index = (invoice.invoice_date - last_sunday).days
                weekly_data[day_index] += float(invoice.grand_total_amount)  # Convert Decimal to float

            # Create a dictionary to hold the data
            data_dict = {
                'today': today.isoformat(),
                'last_sunday': last_sunday.isoformat(),
                'next_saturday': next_saturday.isoformat(),
                'weekly_data': weekly_data
            }

            # Convert dictionary to JSON string with custom encoder
            weeklys_data = json.dumps(data_dict, cls=DjangoJSONEncoder)

          
            

            # Pass data to the template
            return render(request, 'index.html', {
                'subtotalsale': subtotalsale,
                'active_page': 'index',
                'labels_json': labels_json,
                'data_json': data_json,
                'growth_json': growth_json,
                'totaltax':totaltax,
                'totalsalaryexpance':totalsalaryexpance,
                'totalsalaryexcludedeductions':totalsalaryexcludedeductions,
                'most_booked_room':most_booked_room,
                'total_cash_amount':total_cash_amount,
                'total_online_amount':total_online_amount,
                 'weeklys_data': weeklys_data,
            })
        else:
            return render(request, 'login.html')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)
    
def guestregform(request,id):
    try:
        if request.user.is_authenticated:
            user = request.user
            if Gueststay.objects.filter(vendor=user,id=id).exists():
                guestdata = Gueststay.objects.filter(vendor=user,id=id)
                hoteldata = HotelProfile.objects.filter(vendor=user)
                return render(request,"guestregform.html",{'guestdata':guestdata,'hoteldata':hoteldata})
            else:
                return render(request,"homepage.html")
        else:
            return render(request, 'login.html')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)


def myprofile(request):
    if not request.user.is_authenticated:
        return render(request, 'login.html')
        
    profiledata = HotelProfile.objects.filter(vendor=request.user)
    return render(request, 'profile.html', {'profiledata': profiledata})



def guesthistory(request):
    try:
        if request.user.is_authenticated:
            user = request.user
            guestshistory = Gueststay.objects.filter(vendor=user).values(
                'checkoutdate', 'checkindate', 'roomno', 'guestname', 'id', 'guestphome', 'guestcity', 'noofrooms'
            ).order_by('-id')
            
            paginator = Paginator(guestshistory, 25)
            page = request.GET.get('page', 1)
            
            try:
                guesthistory = paginator.page(page)
            except PageNotAnInteger:
                guesthistory = paginator.page(1)
            except EmptyPage:
                guesthistory = paginator.page(paginator.num_pages)
            
            return render(request, 'guesthistory.html', {'guesthistory': guesthistory, 'active_page': 'guesthistory'})
        else:
            return render(request, 'login.html')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)

        
    
def guestdetails(request, id):
    try:
        if request.user.is_authenticated:
            user = request.user
            guestdetails = Gueststay.objects.filter(vendor=user, id=id).all()
            moredata = MoreGuestData.objects.filter(vendor=user, mainguest_id=id).all()
            
            return render(request, 'guestdetails.html', {
                'guestdetails': guestdetails,
                'MoreGuestData': moredata,
                'active_page': 'guesthistory'
            })
        else:
            return render(request, 'login.html')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)


def advanceroombookpage(request):
    try:
        if request.user.is_authenticated:
            user = request.user
            br = Rooms.objects.filter(vendor=user)
            channal = onlinechannls.objects.all()
            return render(request, 'roombookpage.html', {
                'br': br,
                'channal': channal,
                'active_page': 'advanceroombookpage'
            })
        else:
            return render(request, 'login.html')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)

def foliobillingpage(request):
    try:
        if request.user.is_authenticated:
            user = request.user
            invoice_data = Invoice.objects.filter(vendor=user, foliostatus=False).order_by('room_no')
            return render(request, 'foliopage.html', {
                'invoice_data': invoice_data,
                'active_page': 'foliobillingpage'
            })
        else:
            return render(request, 'login.html')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)
    
    
def invoicepage(request, id):
    try:
        if request.user.is_authenticated:
            user = request.user
            userid = id
            guestdata = Gueststay.objects.filter(vendor=user, id=userid)
            invoice_data = Invoice.objects.get(vendor=user, customer=userid)
            profiledata = HotelProfile.objects.filter(vendor=user)
            itemid = invoice_data.id
            status = invoice_data.foliostatus

            invoice_data = Invoice.objects.filter(vendor=user, customer=userid)
            invoiceitemdata = InvoiceItem.objects.filter(vendor=user, invoice=itemid)
            loyltydata = loylty_data.objects.filter(vendor=user, Is_active=True)
            
            if status is False:
                for datas in invoice_data:
                    cashamt = datas.cash_amount
                    onlineamt = datas.online_amount
                    grandamt = datas.grand_total_amount
                print(cashamt,onlineamt,grandamt)
                remainamt =  True
                remainamtinrs = 0
                testamt=cashamt + onlineamt
                if testamt == grandamt:
                    remainamt = False
                remainamtinrs = grandamt - testamt
                print(testamt)
                return render(request, 'foliobill.html', {
                    'active_page': 'foliobillingpage',
                    'profiledata': profiledata,
                    'guestdata': guestdata,
                    'invoice_data': invoice_data,
                    'invoiceitemdata': invoiceitemdata,
                    'loyltydata': loyltydata,
                    'remainamt':remainamt,
                    'remainamtinrs':remainamtinrs
                })
            else:
                return render(request, 'invoicepage.html', {
                    'profiledata': profiledata,
                    'guestdata': guestdata,
                    'invoice_data': invoice_data,
                    'invoiceitemdata': invoiceitemdata
                })
        else:
            return render(request, 'login.html')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)

from django.urls import reverse
def editcustomergstnumber(request):
    try:
        if request.user.is_authenticated and request.method == "POST":
            user = request.user
            invcid = request.POST.get('invcid')
            gstnumber = request.POST.get('gstnumber')
            customerphone = request.POST.get('customerphone')
            if Invoice.objects.filter(vendor=user,customer_id=invcid).exists():
                Invoice.objects.filter(vendor=user,customer_id=invcid).update(customer_gst_number=gstnumber)
                Gueststay.objects.filter(vendor=user,id=invcid).update(guestphome=customerphone)
                

            else:
                pass

            url = reverse('invoicepage', args=[invcid])

        
            return redirect(url)
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)



def rooms(request):
    try:
        if request.user.is_authenticated:
            user = request.user
            roomdata = Rooms.objects.filter(vendor=user).order_by('room_name')
            category = RoomsCategory.objects.filter(vendor=user)
            tax = Taxes.objects.filter(vendor=user)
            return render(request, 'rooms.html', {
                'roomdata': roomdata,
                'active_page': 'rooms',
                'category': category,
                'tax': tax
            })
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)





# def homepage(request):
#     try:
#         if request.user.is_authenticated:
#             user = request.user
#             showtimeb = strftime("%Y-%m-%d %H:%M:%S", gmtime())

#             # Filter data
#             category = RoomsCategory.objects.filter(vendor=user).order_by('id')
#             rooms = Rooms.objects.filter(vendor=user).order_by('id')
#             desired_date = datetime.now().date()

#             # Update checkout status for guests
#             Gueststay.objects.filter(Q(vendor=user, checkoutdate__date__lte=desired_date) | Q(vendor=user, checkoutdate__date=desired_date)).update(checkoutstatus=True)

#             # Query sets
#             dats = Gueststay.objects.filter(vendor=user, checkoutdate__date__lte=desired_date, checkoutstatus=True, checkoutdone=False)
#             datsin = Gueststay.objects.filter(vendor=user, checkindate__date=desired_date)
#             tax = Taxes.objects.filter(vendor=user).all()
#             arriwaldata = RoomBookAdvance.objects.filter(
#                   # Include the vendor condition
#                 Q(vendor=user,bookingdate=desired_date,checkinstatus=False) | 
#                 Q(vendor=user,bookingdate__lte=desired_date, checkoutdate__gt=desired_date,checkinstatus=False)
#             )
#             bookedmisseddata = RoomBookAdvance.objects.filter(vendor=user, checkoutdate__lte=desired_date, checkinstatus=False)
#             saveguestallroomcheckout = RoomBookAdvance.objects.filter(vendor=user, checkoutdate=desired_date, checkinstatus=True)
            
#             # Update rooms based on filtered data
#             for i in saveguestallroomcheckout:
#                 Rooms.objects.filter(vendor=user, room_name=i.roomno.room_name).exclude(checkin=6).update(checkin=2)
#             print(saveguestallroomcheckout)
#             for i in dats:
#                 Rooms.objects.filter(vendor=user, room_name=i.roomno).exclude(checkin=6).update(checkin=2)

#             for i in bookedmisseddata:
#                 if i.roomno.checkin == 5 or i.roomno.checkin == 4:
#                     Rooms.objects.filter(vendor=user, id=i.roomno.id).update(checkin=0)

#             for data in arriwaldata:
#                 if data.roomno.checkin not in [1, 2, 5]:
#                     Rooms.objects.filter(vendor=user, id=data.roomno.id).update(checkin=4)

#             # Additional queries
#             checkintimedata = HotelProfile.objects.filter(vendor=user)
#             stayover = Rooms.objects.filter(vendor=user, checkin=1).count()
#             availablerooms = Rooms.objects.filter(vendor=user, checkin=0).count()
#             totalrooms = Rooms.objects.filter(vendor=user).count()
#             checkoutcount = Gueststay.objects.filter(vendor=user, checkoutdate__date=desired_date, checkoutstatus=True, checkoutdone=False).count()
#             checkincountdays = len(datsin)

#             # Create rooms dictionary
#             roomsdict = {}
#             for cat in category:
#                 roomsdict[cat.category_name] = [[room.room_name, room.checkin] for room in rooms.filter(room_type=cat)]

#             return render(request, 'homepage.html', {
#                 'active_page': 'homepage',
#                 'category': category,
#                 'rooms': rooms,
#                 'roomsdict': roomsdict,
#                 'tax': tax,
#                 'checkintimedata': checkintimedata,
#                 'stayover': stayover,
#                 'availablerooms': availablerooms,
#                 'checkincount': checkincountdays,
#                 'checkoutcount': checkoutcount,
#                 'arriwalcount': len(arriwaldata)
#             })
#         else:
#             return redirect('loginpage')
#     except Exception as e:
#         return render(request, '404.html', {'error_message': str(e)}, status=500)
    
# update by me code


def homepage(request):
    try:
        if request.user.is_authenticated:
            user = request.user
            showtimeb = strftime("%Y-%m-%d %H:%M:%S", gmtime())

            # Filter data
            category = RoomsCategory.objects.filter(vendor=user).order_by('id')
            rooms = Rooms.objects.filter(vendor=user).order_by('id')
            desired_date = datetime.now().date()

            # Update checkout status for guests
            Gueststay.objects.filter(Q(vendor=user, checkoutdate__date__lte=desired_date) | Q(vendor=user, checkoutdate__date=desired_date)).update(checkoutstatus=True)

            # Query sets
            dats = Gueststay.objects.filter(vendor=user, checkoutdate__date__lte=desired_date, checkoutstatus=True, checkoutdone=False)
            datsin = Gueststay.objects.filter(vendor=user, checkindate__date=desired_date)
            tax = Taxes.objects.filter(vendor=user).all()
            arriwaldata = RoomBookAdvance.objects.filter(
                  # Include the vendor condition
                Q(vendor=user,bookingdate=desired_date,checkinstatus=False) | 
                Q(vendor=user,bookingdate__lte=desired_date, checkoutdate__gt=desired_date,checkinstatus=False)
            )
            bookedmisseddata = RoomBookAdvance.objects.filter(vendor=user, checkoutdate__lte=desired_date, checkinstatus=False)
            saveguestallroomcheckout = RoomBookAdvance.objects.filter(vendor=user, checkoutdate=desired_date, checkinstatus=True)
            
            # Update rooms based on filtered data
            for i in saveguestallroomcheckout:
                roomnumber = i.roomno.room_name
                invcdata = InvoiceItem.objects.filter(vendor=user,description=roomnumber).last()
                if invcdata:
                    if Invoice.objects.filter(vendor=user,id=invcdata.invoice.id,foliostatus=False,customer__checkoutdate=desired_date):
                        Rooms.objects.filter(vendor=user, room_name=i.roomno.room_name).exclude(checkin=6).update(checkin=2)
                    else:
                        # Rooms.objects.filter(vendor=user, room_name=i.roomno.room_name).exclude(checkin=6).update(checkin=0)
                        pass
                else:
                    pass

            for i in dats:
                Rooms.objects.filter(vendor=user, room_name=i.roomno).exclude(checkin=6).update(checkin=2)

            for i in bookedmisseddata:
                if i.roomno.checkin == 5 or i.roomno.checkin == 4:
                    Rooms.objects.filter(vendor=user, id=i.roomno.id).update(checkin=0)

            for data in arriwaldata:
                if data.roomno.checkin not in [1, 2, 5]:
                    Rooms.objects.filter(vendor=user, id=data.roomno.id).update(checkin=4)

            # Additional queries
            checkintimedata = HotelProfile.objects.filter(vendor=user)
            stayover = Rooms.objects.filter(vendor=user, checkin=1).count()
            availablerooms = Rooms.objects.filter(vendor=user, checkin=0).count()
            totalrooms = Rooms.objects.filter(vendor=user).count()
            checkoutcount = Gueststay.objects.filter(vendor=user, checkoutdate__date=desired_date, checkoutstatus=True, checkoutdone=False).count()
            checkincountdays = len(datsin)

            # Create rooms dictionary
            roomsdict = {}
            for cat in category:
                roomsdict[cat.category_name] = [[room.room_name, room.checkin] for room in rooms.filter(room_type=cat)]

            return render(request, 'homepage.html', {
                'active_page': 'homepage',
                'category': category,
                'rooms': rooms,
                'roomsdict': roomsdict,
                'tax': tax,
                'checkintimedata': checkintimedata,
                'stayover': stayover,
                'availablerooms': availablerooms,
                'checkincount': checkincountdays,
                'checkoutcount': checkoutcount,
                'arriwalcount': len(arriwaldata)
            })
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)

def addtax(request):
    try:
        if request.user.is_authenticated and request.method == "POST":
            user = request.user
            taxname = request.POST.get('taxname')
            taxcode = request.POST.get('taxcode')
            taxrate = request.POST.get('taxrate')

            if Taxes.objects.filter(vendor=user, taxname=taxname, taxrate=taxrate).exists():
                messages.error(request, 'Tax Already Exists!')
            else:
                Taxes.objects.create(vendor=user, taxname=taxname, taxcode=taxcode, taxrate=taxrate)
                messages.success(request, 'Tax Added')

            return redirect('setting')
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)
    

def addcategory(request):
    try:
        if request.user.is_authenticated and request.method == "POST":
            user = request.user
            roomcategory = request.POST.get('catname')
            if RoomsCategory.objects.filter(vendor=user, category_name=roomcategory).exists():
                messages.error(request, 'Category already exists')
            else:
                price = request.POST.get('price')
                taxcategory = request.POST.get('taxcategory')
                hsccode = request.POST.get('hsccode')
                category_img = request.FILES.get('Categoryimg')

                RoomsCategory.objects.create(
                    vendor=user,
                    category_name=roomcategory,
                    catprice=price,
                    category_tax_id=taxcategory,
                    Hsn_sac=hsccode,
                    roomimg=category_img
                )

                messages.success(request, 'Category added successfully')

            return redirect('setting')
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)
    
def updatecategory(request):
    try:
        if request.user.is_authenticated and request.method == "POST":
            user = request.user
            roomcategory = request.POST.get('catname')
            categoryid = request.POST.get('categoryid')
            price = request.POST.get('price')
            taxcategory = request.POST.get('taxcategory')
            hsccode = request.POST.get('hsccode')
            Categoryimg = request.FILES.get('Categoryimg')

            profile = RoomsCategory.objects.get(vendor=user, id=categoryid)
            tax = Taxes.objects.get(vendor=user, id=taxcategory)

            profile.category_name = roomcategory
            profile.catprice = price
            profile.category_tax = tax
            profile.Hsn_sac = hsccode

            if Categoryimg:
                profile.roomimg = Categoryimg  # Update the image only if a new one is provided

            profile.save()

            taxrate = tax.taxrate
            taxamount = int(price) * taxrate // 100

            Rooms.objects.filter(vendor=user, room_type_id=categoryid).update(price=price, tax=tax, tax_amount=taxamount)

            messages.success(request, 'Category update successful')

            return redirect('setting')

        else:
            return redirect('loginpage')
    
    except RoomsCategory.DoesNotExist:
        messages.error(request, 'Category does not exist')
    
    except Taxes.DoesNotExist:
        messages.error(request, 'Tax category does not exist')
    
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')

    return redirect('setting')

 

def addroom(request):
    try:
        if request.user.is_authenticated and request.method == "POST":
            user = request.user
            roomname = request.POST.get('roomname')
            category = request.POST.get('category')
            catdata = RoomsCategory.objects.get(vendor=user, id=category)
            tax_price = catdata.category_tax.taxrate
            roomprice = catdata.catprice
            taxprice = roomprice * tax_price // 100
            tax_type = catdata.category_tax.id
            
            if Rooms.objects.filter(vendor=user, room_name=roomname).exists():
                return redirect('rooms')
            else:
                Rooms.objects.create(
                    vendor=user,
                    room_name=roomname,
                    room_type_id=category,
                    price=roomprice,
                    tax_id=tax_type,
                    tax_amount=taxprice
                )

            category = RoomsCategory.objects.filter(vendor=user)
            roomdata = Rooms.objects.filter(vendor=user).order_by('room_name')
            tax = Taxes.objects.filter(vendor=user)
            
            return render(request, 'rooms.html', {
                'roomdata': roomdata,
                'active_page': 'rooms',
                'category': category,
                'tax': tax,
            })
        
        else:
            return redirect('loginpage')
    
    except RoomsCategory.DoesNotExist:
        messages.error(request, 'Selected category does not exist')
    
    except Taxes.DoesNotExist:
        messages.error(request, 'Tax category does not exist')
    
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
    
    return redirect('rooms')



def updaterooms(request):
    try:
        if request.user.is_authenticated and request.method == "POST":
            user = request.user
            roomname = request.POST.get('roomname')
            category = request.POST.get('category')
            roomid = request.POST.get('roomid')

            catdata = RoomsCategory.objects.get(vendor=user, id=category)
            tax_price = catdata.category_tax.taxrate
            roomprice = catdata.catprice
            taxprice = roomprice * tax_price // 100
            tax_type = catdata.category_tax.id

            if Rooms.objects.filter(vendor=user, id=roomid).exists():
                Rooms.objects.filter(vendor=user, id=roomid).update(
                    room_name=roomname,
                    room_type_id=category,
                    price=roomprice,
                    tax_id=tax_type,
                    tax_amount=taxprice
                )

            category = RoomsCategory.objects.filter(vendor=user)
            roomdata = Rooms.objects.filter(vendor=user).order_by('room_name')
            tax = Taxes.objects.filter(vendor=user)

            return render(request, 'rooms.html', {
                'roomdata': roomdata,
                'active_page': 'rooms',
                'category': category,
                'tax': tax,
            })
        
        else:
            return redirect('loginpage')
    
    except RoomsCategory.DoesNotExist:
        messages.error(request, 'Selected category does not exist')
    
    except Taxes.DoesNotExist:
        messages.error(request, 'Tax category does not exist')
    
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
    
    return redirect('rooms')
    
def deleteroom(request, id):
    try:
        if request.user.is_authenticated:
            user = request.user
            try:
                room = Rooms.objects.get(vendor=user, id=id)
                room.delete()
            except Rooms.DoesNotExist:
                pass  # Room with given ID does not exist, no action needed
            
            return redirect('rooms')
        else:
            return redirect('loginpage')
    
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('rooms')


def openroomclickformpage(request, id):
    try:
        if request.user.is_authenticated:
            user = request.user
            room_data = Rooms.objects.filter(vendor=user, room_name=id)
            roomno = id
            loyltydata = loylty_data.objects.filter(vendor=user, Is_active=True)
            return render(request, 'bookroomclickpage.html', {
                'id': roomno,
                'room_data': room_data,
                'loyltydata': loyltydata
            })
        else:
            return redirect('loginpage')
    
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('homepage')

def roomcheckin(request,id):
    try:
        if request.user.is_authenticated:
            user=request.user
            roomno=id
            print(type)
            realroomnuo=Rooms.objects.get(vendor=user,room_name=roomno)
            Rooms.objects.filter(vendor=user,room_name=roomno).update(checkin=1)
            category = RoomsCategory.objects.filter(vendor=user).all()
            category_count = RoomsCategory.objects.filter(vendor=user).count()
            rooms =Rooms.objects.filter(vendor=user).all()
            roomsdict=dict()
            for i in category:
                newlist=[]
                for j in rooms:
                    roomsdict[i.category_name] =newlist
                    if j.room_type == i:
                        lst=[]
                        lst.append(j.room_name)
                        lst.append(j.checkin)
                        newlist.append(lst)
                    else:
                        continue
            showtimeb = strftime("%Y-%m-%d %H:%M:%S", gmtime())
            print(roomsdict)
            return render(request,'index.html')
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)
    



def addguestdata(request):
    try:
        if request.user.is_authenticated and request.method=="POST":
            user=request.user
            guestname = request.POST.get('guestname')
            guestphome = request.POST.get('guestphone')
            guestemail = request.POST.get('guestemail')
            guestcity = request.POST.get('guestcity')
            guestcountry = request.POST.get('guestcountry')
            guestidimg = request.FILES.get('guestid')
            checkindate = request.POST.get('guestcheckindate')
            checkoutdate = request.POST.get('guestcheckoutdate')
            noofguest = request.POST.get('noofguest')
            adults = request.POST.get('guestadults')
            children = request.POST.get('guestchildren')
            purposeofvisit = request.POST.get('Purpose')
            roomno = request.POST.get('roomno')
            subtotal = request.POST.get('subtotal')
            total = request.POST.get('total')
            tax = request.POST.get('tax')
            paidstatus = request.POST.get('paidstatus')
            state = request.POST.get('STATE')
            paymentstatus = request.POST.get('paymentstatus')
            staydays = float(request.POST.get('staydays'))
            subtotal=int(subtotal)
            total=int(total)
            discount = float(request.POST.get('discount'))
            checkmoredatastatus = request.POST.get('checkmoredatastatus')
            current_date = datetime.now()
            userstatedata = HotelProfile.objects.get(vendor=user)
            userstate = userstatedata.zipcode
            if Rooms.objects.filter(vendor=user,room_name=roomno,checkin=0).exists():
                Rooms.objects.filter(vendor=user,room_name=roomno).update(checkin=1)
                if userstate == state:
                    taxtypes = "GST"
                else:
                    taxtypes = "IGST"
                guestdata = Gueststay.objects.create(vendor=user,guestname=guestname,guestphome=guestphome,guestemail=guestemail,guestcity=guestcity,guestcountry=guestcountry,guestidimg=guestidimg,
                                        checkindate=current_date,checkoutdate=checkoutdate ,noofguest=noofguest,adults=adults,children=children
                                        ,purposeofvisit=purposeofvisit,roomno=roomno,tax=tax,discount=discount,subtotal=subtotal,total=total,noofrooms=1)
                gsid=guestdata.id
                if checkmoredatastatus == 'on':
                    moreguestname = request.POST.get('moreguestname')
                    moreguestphone = request.POST.get('moreguestphone',0)
                    moreguestaddress = request.POST.get('moreguestaddress')
                    if moreguestphone == "":
                        moreguestphone = 0
                    else:
                        pass
                    MoreGuestData.objects.create(vendor=user,mainguest=guestdata,another_guest_name=moreguestname,
                                                another_guest_phone=moreguestphone,another_guest_address=moreguestaddress)
                    print("createsuccessfull chandan")
                roomdata = Rooms.objects.filter(vendor=user,room_name=roomno).all()
                for i in roomdata:
                    roomprice = i.price
                    tax_rate = i.tax.taxrate
                    roomname = i.room_name
                    tax_amount = i.tax_amount
                    roomtype = i.room_type.id
                    room_details = i.room_type.category_name
                divideamt = tax_amount / 2
                tax_rate = tax_rate / 2
                totalitemamount = roomprice * staydays
                subtotalamount = totalitemamount - discount
                gstamount = (subtotalamount * tax_rate) /100
                sgstamount = (subtotalamount * tax_rate) /100
                grandtotal_amount = subtotalamount + gstamount + sgstamount
                cat = RoomsCategory.objects.get(vendor=user,id=roomtype)
                hsnno = cat.Hsn_sac
                print(room_details)
                room_details = roomname
                print(hsnno)
                #  for invoice number
                current_date = datetime.now().date()
                invoice_number = ""
                cashamount = 0.00
                onlineamount = 0.00
                if paidstatus == "Paid":
                    statuspaid = True
                    if paymentstatus == "cash":
                        cashamount = grandtotal_amount
                    elif paymentstatus == "online":
                        onlineamount = grandtotal_amount
                    else:
                        cashamount = float(request.POST.get('cashamount'))
                        onlineamount = float(request.POST.get('onlineamount'))
                else:
                    statuspaid = False
                Invoiceid = Invoice.objects.create(vendor=user,customer=guestdata,customer_gst_number="",
                                                    invoice_number=invoice_number,invoice_date=checkindate,total_item_amount=totalitemamount,discount_amount=discount,
                                                    subtotal_amount=subtotalamount,gst_amount=gstamount,sgst_amount=sgstamount,
                                                    grand_total_amount=grandtotal_amount,modeofpayment=paymentstatus,room_no=roomname,
                                                    taxtype=taxtypes,online_amount=onlineamount ,cash_amount=cashamount,)
                
                invoiceitem = InvoiceItem.objects.create(vendor=user,invoice=Invoiceid,description=room_details,quantity_likedays=staydays,
                                        paidstatus=statuspaid,price=roomprice,cgst_rate=tax_rate,sgst_rate=tax_rate,hsncode=hsnno,total_amount=grandtotal_amount)  
                Rooms.objects.filter(vendor=user,room_name=roomno).update(checkin=1)

            
                
                return redirect('foliobillingpage')
            else:
                return redirect('foliobillingpage')
        else:
            return redirect('loginpage') 
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)
    


def addguestdatafromadvanceroombook(request):
    try:
        if request.user.is_authenticated and request.method=="POST":
            user=request.user
            guestname = request.POST.get('guestname')
            guestphome = request.POST.get('guestphone')
            guestemail = request.POST.get('guestemail')
            guestcity = request.POST.get('guestcity')
            guestcountry = request.POST.get('guestcountry')
            guestidimg = request.FILES.get('guestid')
            checkindate = request.POST.get('guestcheckindate')
            checkoutdate = request.POST.get('guestcheckoutdate')
            noofguest = request.POST.get('noofguest')
            adults = request.POST.get('guestadults')
            children = request.POST.get('guestchildren')
            purposeofvisit = request.POST.get('Purpose')
            roomno = request.POST.get('roomno')
            subtotal = request.POST.get('subtotal')
            total = request.POST.get('total')
            tax = request.POST.get('tax')
            noofrooms = request.POST.get('noofrooms')
            saveguestdata = request.POST.get('saveguestdata')
            SaveAdvanceBookGuestData.objects.filter(vendor=user,id=saveguestdata).update(checkinstatus=True)
            checkmoredatastatus = request.POST.get('checkmoredatastatus')
            roomalldefaultcheckinbutton = request.POST.get('roomalldefaultcheckinbutton')
            discount = request.POST.get('discount')
            state = request.POST['STATE']
            subtotal=int(subtotal)
            paidstatus = request.POST.get('paidstatus')
            paymentstatus = request.POST['paymentstatus']
            total=int(total)
            saveguestdata =  SaveAdvanceBookGuestData.objects.get(vendor=user,id=saveguestdata)
            guestcheckinstatus= Gueststay.objects.filter(vendor=user,guestname=guestname,guestphome=guestphome,checkindate=checkindate,checkoutdate=checkoutdate).exists()
            userstatedata = HotelProfile.objects.get(vendor=user)
            userstate = userstatedata.zipcode
            roomsdatas = RoomBookAdvance.objects.filter(vendor=user,saveguestdata=saveguestdata)
            checkindoornot = True
            for check in roomsdatas:
                if check.roomno.checkin == 1 or check.roomno.checkin == 2:
                    checkindoornot = False
            if checkindoornot == True:
                if userstate == state:
                    taxtypes = "GST"
                else:
                    taxtypes = "IGST"
                if guestcheckinstatus is True:
                    messages.error(request,'recently Check In this Room With Same Data Please Change Address Mobile And Guest Name heckIn CheckOut Date / Room No to CheckIn this Room')
                else:
                    current_date = datetime.now()
                    guestdata=Gueststay.objects.create(vendor=user,guestname=guestname,guestphome=guestphome,guestemail=guestemail,guestcity=guestcity,guestcountry=guestcountry,guestidimg=guestidimg,
                                            checkindate=current_date,checkoutdate=checkoutdate ,noofguest=noofguest,adults=adults,children=children
                                            ,purposeofvisit=purposeofvisit,roomno=roomno,tax=tax,discount=discount,subtotal=subtotal,total=total,noofrooms=noofrooms)
                    Invoiceid = Invoice.objects.create(vendor=user,customer=guestdata,customer_gst_number="",
                                                online_amount=0.00 ,cash_amount=0.00,  invoice_number="",invoice_date=checkindate,total_item_amount=0.0,discount_amount=discount,
                                                    subtotal_amount=0.0,gst_amount=0.0,sgst_amount=0.0,
                                                    grand_total_amount=0.0,modeofpayment=paymentstatus,room_no=0.0,taxtype=taxtypes)
                
                    totalrooms = RoomBookAdvance.objects.filter(vendor=user,saveguestdata_id=saveguestdata).all()
                    print(len(totalrooms))
                    updatediscountamount = int(discount)
                    if len(totalrooms)>1:
                        updatediscountamount = int(discount) / int(len(totalrooms))
                    print(updatediscountamount)
                    staydays = saveguestdata.staydays
                    Invtotal_amount = 0.0
                    Invsub_total = 0.0
                    Invtaxamt = 0.0
                    if paidstatus == "Paid":
                        statuspaid = True
                    else:
                        statuspaid = False
                    for i in totalrooms:
                        rid = i.roomno.id
                        roomdata = Rooms.objects.get(vendor=user,id=rid)
                        
                        roomprice = int(roomdata.price) * int(staydays)
                        roomprice = roomprice - updatediscountamount
            
                        taxrate = roomdata.tax.taxrate
                        hsn = roomdata.room_type.Hsn_sac
                        gstrate = taxrate/2
                        Invtotal_amount = Invtotal_amount  + roomdata.price * staydays
                        Invsub_total = Invsub_total +  roomprice
                        Invtaxamt = Invtaxamt + (roomprice*taxrate/100)
                        incltaxprice = roomprice + (roomprice*taxrate/100)
                        InvoiceItem.objects.create(vendor=user,invoice=Invoiceid,description=roomdata.room_name,hsncode=hsn,
                                        quantity_likedays=staydays,price=roomdata.price,total_amount=incltaxprice,cgst_rate=gstrate,sgst_rate=gstrate,paidstatus=statuspaid)
                        print(taxrate)
                    Invgrandtotal = Invsub_total + Invtaxamt
                    Invtaxamt = Invtaxamt /2

                    # amount split
                    cashamount = 0.00
                    onlineamount = 0.00
                    if paidstatus == "Paid":
                        statuspaid = True
                        if paymentstatus == "cash":
                            cashamount = Invgrandtotal
                        elif paymentstatus == "online":
                            onlineamount = Invgrandtotal
                        else:
                            cashamount = float(request.POST.get('cashamount'))
                            onlineamount = float(request.POST.get('onlineamount'))
                    else:
                        statuspaid = False
                    Invoice.objects.filter(vendor=user,id=Invoiceid.id).update(total_item_amount=Invtotal_amount,discount_amount=discount,subtotal_amount=Invsub_total,
                                    modeofpayment=paymentstatus,online_amount=onlineamount ,cash_amount=cashamount,grand_total_amount=Invgrandtotal,gst_amount=Invtaxamt,sgst_amount=Invtaxamt,room_no=roomno)

            
                #Invoice start here
                
                


                    if checkmoredatastatus == 'on':
                        moreguestname = request.POST.get('moreguestname')
                        moreguestphone = request.POST.get('moreguestphone')
                        if moreguestphone == "":
                            moreguestphone = 0
                        else:
                            pass
                        moreguestaddress = request.POST.get('moreguestaddress')
                        MoreGuestData.objects.create(vendor=user,mainguest=guestdata,another_guest_name=moreguestname,
                                                    another_guest_phone=moreguestphone,another_guest_address=moreguestaddress)
                        print("createsuccessfull chandan")

            
                
                    today = datetime.now().date()
                    roomdata = RoomBookAdvance.objects.filter(vendor=user,saveguestdata_id=saveguestdata).all()
                    #  roomdata = Room_history.objects.filter(vendor=user,checkindate__range=[checkindate,checkoutdate],bookingstatus=True,bookingguestphone=guestphome).all()
                    if roomalldefaultcheckinbutton == 'on':
                        for data in roomdata:
                            print(data.roomno.room_name,data.roomno.checkin)
                            Rooms.objects.filter(vendor=user,id=data.roomno.id).all().update(checkin=5)
                            print(data.roomno.room_name,data.roomno.checkin)
                            RoomBookAdvance.objects.filter(vendor=user,saveguestdata_id=saveguestdata).update(partly_checkin=True)
                        print(roomdata)
                    else:
                        for data in roomdata:
                            print(data.roomno.id)
                            roomid = Rooms.objects.get(vendor=user,id=data.roomno.id)
                            Rooms.objects.filter(vendor=user,id=data.roomno.id).update(checkin=1)
                            print(data.roomno.room_name,data.roomno.checkin)
                            RoomBookAdvance.objects.filter(vendor=user,saveguestdata_id=saveguestdata).update(checkinstatus=True)
                return redirect('todaybookingpage')
            else:
                messages.error(request,"Please check out the room that has not been checked out yet for the same guest before you can check in to a new room.")
                return redirect('todaybookingpage')
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)
   

# checkout button function
from django.db.models import Max
def checkoutroom(request):
    try:
        if request.user.is_authenticated and request.method=="POST":
            user=request.user
            roomno = request.POST.get('roomno')
            invoice_id = request.POST.get('invoice_id')
            loyltycheck = request.POST.get('loyltycheck')
            paymentstatus = request.POST.get('paymentstatus')
            gstnumbercustomer = request.POST.get('gstnumber')
            
            if Invoice.objects.filter(vendor=user,id=invoice_id,foliostatus=False).exists():
                if gstnumbercustomer:
                    Invoice.objects.filter(vendor=user,id=invoice_id).update(customer_gst_number=gstnumbercustomer)
                else:
                    pass
                if Invoice.objects.filter(vendor=user,id=invoice_id).exists():
                    GUESTIDs = Invoice.objects.get(vendor=user,id=invoice_id)
                    GUESTID = GUESTIDs.customer.id
                    invoicegrandtotalpaymentstatus = GUESTIDs.grand_total_amount
                    if paymentstatus == "Partly":
                        cashamount = request.POST.get('cashamount')
                        onlineamount = request.POST.get('onlineamount')
                        Invoice.objects.filter(vendor=user,id=invoice_id).update(cash_amount=cashamount,online_amount=onlineamount,invoice_status=True)
        
                    elif paymentstatus == "cash":
                        Invoice.objects.filter(vendor=user,id=invoice_id).update(cash_amount=invoicegrandtotalpaymentstatus,online_amount=0.00,invoice_status=True)
                    elif paymentstatus =="unpaid":
                        duedate = request.POST.get('duedate')
                        Invoice.objects.filter(vendor=user,id=invoice_id).update(online_amount=invoicegrandtotalpaymentstatus,invoice_status=False,invoice_number="unpaid")
                        CustomerCredit.objects.create(vendor=user,customer_name=GUESTIDs.customer.guestname,amount=invoicegrandtotalpaymentstatus,due_date=duedate,invoice=GUESTIDs,phone=GUESTIDs.customer.guestphome)
                    else:
                        Invoice.objects.filter(vendor=user,id=invoice_id).update(cash_amount=0.00,online_amount=invoicegrandtotalpaymentstatus,invoice_status=True)
                    guestdatas = Gueststay.objects.get(vendor=user,id=GUESTID)
                    current_date = datetime.now()
                    # Get the current date
                    invccurrentdate = datetime.now().date()

                    # Fetch the maximum invoice number for today for the given user
                    max_invoice_today = Invoice.objects.filter(
                        vendor=user,
                        invoice_date=invccurrentdate,
                        foliostatus=True
                    ).aggregate(max_invoice_number=Max('invoice_number'))['max_invoice_number']

                    # Determine the next invoice number
                    if max_invoice_today is not None:
                        # Extract the numeric part of the latest invoice number and increment it
                        try:
                            current_number = int(max_invoice_today.split('-')[-1])
                            next_invoice_number = current_number + 1
                        except (ValueError, IndexError):
                            # Handle the case where the invoice number format is unexpected
                            next_invoice_number = 1
                    else:
                        next_invoice_number = 1
                    # Generate the invoice number
                    invoice_number = f'INV-{invccurrentdate}-{next_invoice_number}'
                    
                    # Check if the generated invoice number already exists
                    while Invoice.objects.filter(vendor=user,invoice_number=invoice_number).exists():
                        next_invoice_number += 1
                        invoice_number = f'INV-{invccurrentdate}-{next_invoice_number}'

                    Invoice.objects.filter(vendor=user,id=invoice_id).update(invoice_date=invccurrentdate)
                    if RoomBookAdvance.objects.filter(vendor=user,roomno__room_name = roomno,bookingguestphone = guestdatas.guestphome,bookingdate__range = [guestdatas.checkindate , guestdatas.checkoutdate]).exists():
                        saveguestid = RoomBookAdvance.objects.get(vendor=user,roomno__room_name = roomno,bookingguestphone = guestdatas.guestphome,bookingdate__range = [guestdatas.checkindate , guestdatas.checkoutdate])
                        print(saveguestid.saveguestdata.id)
                        multipleroomsdata = RoomBookAdvance.objects.filter(vendor=user,saveguestdata_id=saveguestid.saveguestdata.id).all()
                        print(multipleroomsdata,"rooms data")
                        for i in multipleroomsdata:
                            print(i.roomno.id)
                            Rooms.objects.filter(vendor=user,id=i.roomno.id).update(checkin=0)
                        Invoice.objects.filter(vendor=user,id=invoice_id).update(foliostatus=True,invoice_number=invoice_number,modeofpayment=paymentstatus)
                        SaveAdvanceBookGuestData.objects.filter(id=saveguestid.saveguestdata.id).delete()
                        Gueststay.objects.filter(vendor=user,id=GUESTID).update(checkoutdone=True,checkoutstatus=True,checkoutdate=current_date)
                    elif HourlyRoomsdata.objects.filter(vendor=user,rooms__room_name=guestdatas.roomno).exists():
                        HourlyRoomsdata.objects.filter(vendor=user,rooms__room_name=guestdatas.roomno).update(checkinstatus=False)
                        Invoice.objects.filter(vendor=user,id=invoice_id).update(foliostatus=True,invoice_number=invoice_number,modeofpayment=paymentstatus)
                        Gueststay.objects.filter(vendor=user,id=GUESTID).update(checkoutdone=True,checkoutstatus=True,checkoutdate=current_date)
                
                    else:
                        Gueststay.objects.filter(vendor=user,id=GUESTID).update(checkoutdone=True,checkoutstatus=True,checkoutdate=current_date)
                        Invoice.objects.filter(vendor=user,id=invoice_id).update(foliostatus=True,invoice_number=invoice_number,modeofpayment=paymentstatus)
                        Rooms.objects.filter(vendor=user,room_name=roomno).update(checkin=0)

                    if  paymentstatus =="unpaid":
                            Invoice.objects.filter(vendor=user,id=invoice_id).update(invoice_number="unpaid")
                    else:
                        pass
                if loyltycheck == 'on':
                        guestphone = Gueststay.objects.get(vendor=user,id=GUESTID)
                        guestphonenumber = guestphone.guestphome
                        guestnameformsg = guestphone.guestname
                        loyltyrate = loylty_data.objects.get(vendor=user)
                        totalamountinvoice = GUESTIDs.grand_total_amount
                        totalloyltyamount = int(totalamountinvoice)*loyltyrate.loylty_rate_prsantage//100
                        if loylty_Guests_Data.objects.filter(vendor=user,guest_contact=guestphonenumber).exists():
                                    loyltdatas = loylty_Guests_Data.objects.get(vendor=user,guest_contact=guestphonenumber)
                                    existsamount = loyltdatas.loylty_point + totalloyltyamount
                                    loylty_Guests_Data.objects.filter(vendor=user,guest_contact=guestphonenumber).update(loylty_point = existsamount)
                        else:
                                    loylty_Guests_Data.objects.create(vendor=user,guest_name=guestnameformsg,guest_contact=guestphonenumber,loylty_point=totalloyltyamount)
                        # msg content 
                        usermsglimit = Messgesinfo.objects.get(vendor=user)
                        if usermsglimit.defaultlimit > usermsglimit.changedlimit :
                                addmsg = usermsglimit.changedlimit + 2
                                Messgesinfo.objects.filter(vendor=user).update(changedlimit=addmsg)
                                profilename = HotelProfile.objects.get(vendor=user)
                                hotelname = profilename.name
                                mobile_number = guestphonenumber
                                user_name = "chandan"
                                val = 5
                                message_content = f"Dear Guest, you have earned loyalty points worth Rs {totalloyltyamount} at {hotelname}. We look forward to welcoming you back soon. - Billzify"
                                    
                                base_url = "http://control.yourbulksms.com/api/sendhttp.php"
                                params = {
                                    'authkey': settings.YOURBULKSMS_API_KEY,
                                    'mobiles': guestphonenumber,
                                    'sender':  'BILZFY',
                                    'route': '2',
                                    'country': '0',
                                    'DLT_TE_ID': '1707171993560691064'
                                }
                                encoded_message = urllib.parse.urlencode({'message': message_content})
                                url = f"{base_url}?authkey={params['authkey']}&mobiles={params['mobiles']}&sender={params['sender']}&route={params['route']}&country={params['country']}&DLT_TE_ID={params['DLT_TE_ID']}&{encoded_message}"
                                
                                try:
                                    response = requests.get(url)
                                    if response.status_code == 200:
                                        try:
                                            response_data = response.json()
                                            if response_data.get('Status') == 'success':
                                                messages.success(request, 'SMS sent successfully.')
                                            else:
                                                messages.success(request, response_data.get('Description', 'Failed to send SMS'))
                                        except ValueError:
                                            messages.success(request, 'Failed to parse JSON response')
                                    else:
                                        messages.success(request, f'Failed to send SMS. Status code: {response.status_code}')
                                except requests.RequestException as e:
                                    messages.success(request, f'Error: {str(e)}')
                        else:
                            messages.error(request,'Ooooops! Looks like your message balance is depleted. Please recharge to keep sending SMS notifications to your guests.CLICK HERE TO RECHARGE!')
                                
                else:
                    pass
                return redirect('invoicepage', id=GUESTID)
            else:
                return redirect('invoicepage', id=GUESTID)
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)
    


def cancelroom(request):
    try:
        if request.user.is_authenticated and request.method=="POST":
            user=request.user
            roomno = request.POST.get('roomno')
            invoice_id = request.POST.get('invoice_id')
            guest_id = request.POST.get('guest_id')
            guestdatas = Gueststay.objects.get(vendor=user,id=guest_id)
            if Gueststay.objects.filter(vendor=user,id=guest_id).exists():
                if RoomBookAdvance.objects.filter(vendor=user,roomno__room_name = roomno,bookingguestphone = guestdatas.guestphome,bookingdate__range = [guestdatas.checkindate , guestdatas.checkoutdate]).exists():
                    print("haan bhai booking hai")
                    saveguestid = RoomBookAdvance.objects.filter(vendor=user,roomno__room_name = roomno,bookingguestphone = guestdatas.guestphome,bookingdate__range = [guestdatas.checkindate , guestdatas.checkoutdate])
                    for i in saveguestid:
                        saveguestidfilter = i.saveguestdata.id
                    multipleroomsdata = RoomBookAdvance.objects.filter(vendor=user,saveguestdata_id=saveguestidfilter).all()
                    print(multipleroomsdata,"rooms data")
                    for i in multipleroomsdata:
                            print(i.roomno.id)
                            Rooms.objects.filter(vendor=user,id=i.roomno.id).update(checkin=0)
                    SaveAdvanceBookGuestData.objects.filter(id=saveguestidfilter).delete()
                    Gueststay.objects.filter(vendor=user,id=guest_id).delete()
                elif HourlyRoomsdata.objects.filter(vendor=user,rooms__room_name=guestdatas.roomno).exists():
                    HourlyRoomsdata.objects.filter(vendor=user,rooms__room_name=guestdatas.roomno).update(checkinstatus=False)
                    Gueststay.objects.filter(vendor=user,id=guest_id).delete()
                else:
                    Gueststay.objects.filter(vendor=user,id=guest_id).delete()
                    Rooms.objects.filter(vendor=user,room_name=roomno).update(checkin=0)
                    
            else:
                pass
            return redirect('homepage')
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)
    



def gotofoliobyhome(request,id):
    try:
        if request.user.is_authenticated:
            user=request.user
            roomno = id
            if Gueststay.objects.filter(vendor=user,roomno=roomno,checkoutdone=False).exists():
                custid = Gueststay.objects.filter(vendor=user,roomno=roomno,checkoutdone=False).last()
                customerid = custid.id
                if Invoice.objects.filter(vendor=user,customer_id=customerid).exists():
                    invcid = Invoice.objects.get(vendor=user,customer_id=customerid)
                    urlid = custid.id
                    # invoicepage
                    return redirect('invoicepage', id=urlid)
                else:
                    Rooms.objects.filter(vendor=user,room_name=roomno).update(checkin=0)
                    return redirect('homepage')
            else:
                current_date = datetime.now().date()
                invcitemid = InvoiceItem.objects.filter(vendor=user,description=roomno,invoice__foliostatus=False)
                for i in invcitemid:
                    invceid = i.invoice.id
                if len(invcitemid) > 0:
                    if Invoice.objects.filter(vendor=user,id=invceid).exists():
                        invoicedata = Invoice.objects.get(vendor=user,id=invceid)
                        customerid = invoicedata.customer.id
                        return redirect('invoicepage', id=customerid)
                    else:
                        Rooms.objects.filter(vendor=user,room_name=roomno).update(checkin=0)
                        return redirect('homepage')
                else:
                    Rooms.objects.filter(vendor=user,room_name=roomno).update(checkin=0)
                    return redirect('homepage')
                
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)
    


#login authencatation and subscription


def signuppage(request):
    try:
        form = UserCreationForm()
        return render(request, 'signup.html', {'form': form})
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)
    

    
def loginpage(request):
    try:
        form = UserCreationForm()
        return render(request, 'login.html', {'form': form}) 
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)
    

@csrf_exempt
def signup(request):
    try:
        if request.method == 'POST':
            form = UserCreationForm(request.POST)
            if form.is_valid():
                form.save()
                username = form.cleaned_data.get('username')
                raw_password = form.cleaned_data.get('password1')
                user = authenticate(username=username, password=raw_password)
                login(request, user)
                form = UserCreationForm()
                messages.success(request,'Registerd Succesfully!   ')
                return render(request, 'login.html', {'form': form}) 
        else:
            form = UserCreationForm()
        return render(request, 'signup.html', {'form': form})
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('signuppage')

from django.contrib.sessions.models import Session
from django.utils import timezone

@csrf_exempt
def login_view(request):
    try:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # Invalidate any existing sessions for this user
                current_session_key = request.session.session_key
                user_sessions = Session.objects.filter(expire_date__gte=timezone.now())
                for session in user_sessions:
                    session_data = session.get_decoded()
                    if session_data.get('_auth_user_id') == str(user.id) and session.session_key != current_session_key:
                        session.delete()

                # Log the user in
                login(request, user)

                # Ensure the session is correctly set
                request.session.save()

                # Check subscription status
                user_subscription = Subscription.objects.filter(user=user).last()
                if user_subscription and user_subscription.end_date >= date.today():
                    messages.success(request, 'Successfully logged in!')
                    return redirect('homepage')
                else:
                    messages.error(request, 'Your plan is over. Please recharge to enjoy Billzify services.')
                    return render(request, 'subscriptionplanpage.html', {'username': username})
            else:
                messages.error(request, 'Invalid username and password!')
                return render(request, 'login.html')
        return render(request, 'login.html')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('login')
    

def subscribe(request):
    plans = SubscriptionPlan.objects.all()
    if request.method == 'POST':
        # Handle subscription creation here
        pass
    return render(request, 'subscribe.html', {'plans': plans})



def subscriptionplanpage(request):
    return render(request,'subscriptionplanpage.html')


# its a tempraory not real
def createsubscription(request,id):
    username = id
    user=User.objects.get(username=username)
    sid=SubscriptionPlan.objects.get(id=1)
    b=datetime.now().date()
    enddate=datetime.now().date()
    delta = timedelta(days=28)
    # startdate = enddate + datetime.timedelta(days=30)
    startdate = enddate + delta
    if Messgesinfo.objects.filter(vendor=user).exists():
        data = Messgesinfo.objects.get(vendor=user)
        msg = data.defaultlimit + 250
        Messgesinfo.objects.filter(vendor=user).update(defaultlimit=msg)
    else:
        Messgesinfo.objects.create(vendor=user,defaultlimit=250)
    Subscription.objects.create(user=user,plan=sid,start_date=b,end_date=startdate)
    return render(request, 'login.html')



# ajax book date all rooms data
@csrf_exempt
def addbrnahc(request):
    if request.user.is_authenticated and request.method=="POST":
        user=request.user
        bokingdate=request.POST['date']
        data=Rooms.objects.filter(Q(vendor=user,checkin=0) | Q(vendor=user,checkin=2)).all()
        print(data)
        return JsonResponse(list(data.values('id', 'room_name','room_type','price' ,'tax')),safe=False)
    else:
        return redirect('loginpage')
    

# booking date search function
def bookingdate(request):
    try:
        if request.user.is_authenticated and request.method == "POST":
            user = request.user
            startdate = request.POST['startdate']
            enddate = request.POST.get('enddate')

            bookingdate = datetime.strptime(startdate, '%Y-%m-%d').date()
            checkoutdate = datetime.strptime(enddate, '%Y-%m-%d').date()
            newbookdateminus = bookingdate + timedelta(days=1)

            if checkoutdate == bookingdate:
                messages.error(request, 'Same-Day Checkout Booking Are Not Allowed Here Book To Hourly Room Booking')
                return redirect('advanceroombookpage')
            else:

                # Fetching guest stays with checkoutstatus=False within the specified date range
                guestroomsdata = Gueststay.objects.filter(
                    Q(vendor=user, checkoutstatus=False) &
                    Q(checkindate__lte=checkoutdate) & 
                    Q(checkoutdate__gte=newbookdateminus)
                )

                # Fetching booked rooms within the specified date range
                bookedroomsdata = RoomBookAdvance.objects.filter(
                    Q(vendor=user) &
                    (Q(bookingdate__lte=checkoutdate) & Q(checkoutdate__gte=newbookdateminus))
                )

                # Collecting room numbers from guest stays
                occupied_rooms = set(guest.roomno for guest in guestroomsdata)
                
                # Collecting room numbers from booked rooms, except those starting from enddate
                booked_rooms = set(
                    booking.roomno for booking in bookedroomsdata
                    if booking.bookingdate != checkoutdate
                )
                
                # Fetching all room data excluding rooms with checkin=6
                roomdata = Rooms.objects.filter(vendor=user).exclude(checkin=6).order_by('room_name')

                # Filtering available rooms
                availableroomdata = [
                    room for room in roomdata
                    if room.room_name not in occupied_rooms and room not in booked_rooms
                ]

                channal = onlinechannls.objects.all()
                lenoflist = len(availableroomdata)
                emptymessage = "No Rooms Available On This Day!" if lenoflist == 0 else ""

                return render(request, 'roombookpage.html', {
                    'active_page': 'advanceroombookpage',
                    'availableroomdata': availableroomdata,
                    'emptymessage': emptymessage,
                    'startdate': startdate,
                    'enddate': enddate,
                    'channal': channal,
                    'bookedroomsdata': bookedroomsdata,
                    'guestroomsdata': guestroomsdata
                })
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)
    
    
# booking date search function
# def bookingdate(request):
#     if request.user.is_authenticated and request.method=="POST":
#         user=request.user
#         startdate = request.POST['startdate']
#         enddate = request.POST.get('enddate')
#         bookingdate = datetime.strptime(startdate, '%Y-%m-%d').date()
#         checkoutdate = datetime.strptime(enddate, '%Y-%m-%d').date()
#         # bookingdataset = Room_history.objects.filter(vendor=user,checkindate__range=[bookingdate, enddate],bookingstatus=True).exists()
#         # checkoutdate -= timedelta(days=1)
#         newbookdateminus = datetime.strptime(startdate, '%Y-%m-%d').date()
#         newbookdateminus += timedelta(days=1)
#         b=datetime.now().date()
#         if checkoutdate == bookingdate:
#             messages.success(request,'Same-Day Checkout  Booking Are Not Not Allowed Here Book TO Hourly Room Booking')
#             channal = onlinechannls.objects.all()
#             return redirect('advanceroombookpage')
#         else:
#             guestroomsdata = []

#             total_guests_stayed = Gueststay.objects.filter(Q(vendor = user,checkindate__lte=checkoutdate,checkoutstatus=False) & Q(vendor = user,checkoutdate__gte=newbookdateminus,checkoutstatus=False))
#             chekinroomsdata = []
#             for j in total_guests_stayed:
#                 # roomid = Rooms.objects.get(vendor=user,room_name=j.roomno)
#                 roomid = j.roomno
#                 chekinroomsdata.append(roomid)
#                 guestroomsdata.append(j)
#             # print(chekinroomsdata)
            
#             roomdata = Rooms.objects.filter(vendor=user).exclude(checkin=6).order_by('room_name')
#             availableroomdata = []
#             bookedroomsdata = RoomBookAdvance.objects.filter(Q(vendor=user,bookingdate__lte=checkoutdate) & Q(vendor = user,checkoutdate__gte=newbookdateminus))
#             for i in roomdata:
#                 if not  RoomBookAdvance.objects.filter(Q(vendor=user,roomno = i,bookingdate__lte=checkoutdate) & Q(vendor = user,checkoutdate__gte=newbookdateminus)).exists():
#                         availableroomdata.append(i) 
#                 else:
#                         pass    
#             # print(availableroomdata)    
#             # print(chekinroomsdata)
#             channal = onlinechannls.objects.all()
#             lenoflist=len(availableroomdata)
#             emptymessage=""
#             if lenoflist == 0:
#                     emptymessage="No Rooms Available In This Day !"
#             else:
#                     emptymessage=""
                
#             for data in chekinroomsdata:
#                 for checkdata in availableroomdata:
#                     if data == checkdata :
#                         # print(data)
#                         availableroomdata.remove(data)
#             # current_datetime = datetime.now()

#             # # Format the datetime object as a string
#             # formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')
#             # print(formatted_datetime)
#             # user = request.user
#             # startsdate = request.POST['startdate']
#             # endsdate = request.POST['enddate']
#             # startdate = datetime.strptime(startsdate, '%Y-%m-%d').date()
#             # enddate = datetime.strptime(endsdate, '%Y-%m-%d').date()
#             # checkoutdate = enddate - timedelta(days=1)
#             # newbookdateminus = startdate + timedelta(days=1)
            
#             # bookingdataset = Room_history.objects.filter(vendor=user, checkindate__range=[startdate, enddate], bookingstatus=True).exists()

#             # total_guests_stayed = Gueststay.objects.filter(Q(checkindate__lte=checkoutdate) & Q(checkoutdate__gte=newbookdateminus))
#             # chekinroomsdata = [Rooms.objects.get(vendor=user, room_name=guest.roomno) for guest in total_guests_stayed]

#             # roomdata = Rooms.objects.filter(vendor=user)
#             # availableroomdata = [room for room in roomdata if not Room_history.objects.filter(vendor=user, room_no=room, checkindate__range=[startdate, checkoutdate], bookingstatus=True).exists()]

#             # channal = onlinechannls.objects.all()
#             # lenoflist = len(availableroomdata)
#             # emptymessage = "No Rooms Available In This Day !" if lenoflist == 0 else ""

#             # availableroomdata = [room for room in availableroomdata if room not in chekinroomsdata]
#             # # currents_datetime = datetime.now()
#             # # formatted_datetime = currents_datetime.strftime('%Y-%m-%d %H:%M:%S.%f')
#             # # print(formatted_datetime)
#             # # print(startdate)
#             # # print(enddate)
#             return render(request,'roombookpage.html',{'active_page': 'advanceroombookpage','availableroomdata':availableroomdata,'emptymessage':emptymessage,'startdate':startdate,'enddate':enddate,'channal':channal,'bookedroomsdata':bookedroomsdata,'guestroomsdata':guestroomsdata})
            
        # # delta = timedelta(days=1)
        # # while bookingdate <= checkoutdate:
        # #         print(bookingdate)
        # #         bookingdate += delta
        # roomdata = Rooms.objects.filter(vendor=user).all()
        # availableroomdata = []
        # for i in roomdata:
        #     if not  Room_history.objects.filter(vendor=user,room_no = i,checkindate__range=[bookingdate, enddate]).exists():
        #         availableroomdata.append(i)  
        #     else:
        #         pass          
        # channal = onlinechannls.objects.all()
        # return render(request,'roombookpage.html',{'availableroomdata':availableroomdata,'startdate':startdate,'enddate':enddate,'channal':channal})


from datetime import datetime, timedelta

def addadvancebooking(request):
    try:
        if request.user.is_authenticated and request.method=="POST":
            user=request.user
            bookingdate = request.POST.get('bookingdate')
            guestname = request.POST.get('guestname')
            totalstaydays = request.POST.get('totalstaydays')
            phone = request.POST.get('phone',0)
            channal = request.POST.get('channal')
            bookenddate = request.POST.get('bookenddate')
            totalamount = float(request.POST.get('totalamount'))
            advanceamount = request.POST.get('advanceamount')
            discountamount = float(request.POST.get('discountamount'))
            reaminingamount = request.POST.get('reaminingamount',0)
            serialized_array = request.POST['news']
            channal=onlinechannls.objects.get(id=channal)
            my_array = json.loads(serialized_array)
            noofrooms = len(my_array)
            bookenddate = str(bookenddate)
            # bookenddate = datetime.strptime(bookenddate, '%Y-%m-%d').date()
            bookingdate = datetime.strptime(bookingdate, '%Y-%m-%d').date()
            checkoutdate = datetime.strptime(bookenddate, '%Y-%m-%d').date()
            checkoutdate -= timedelta(days=1)
            # bookingdate -= timedelta(days=1)
            print(bookingdate)
            
            # delta = timedelta(days=1)
            # while bookingdate <= checkoutdate:
            #         print(bookingdate,"working")
            #         bookingdate += delta
            Saveadvancebookdata = SaveAdvanceBookGuestData.objects.create(vendor=user,bookingdate=bookingdate,noofrooms=noofrooms,bookingguest=guestname,
                bookingguestphone=phone,staydays=totalstaydays,
                                                advance_amount=advanceamount,reamaining_amount=reaminingamount,discount=discountamount,
                                                total_amount=totalamount,channal=channal,checkoutdate=bookenddate )
            for i in my_array:
                    roomid = i['id']
                    roomid = Rooms.objects.get(id=roomid)
                    RoomBookAdvance.objects.create(vendor=user,saveguestdata=Saveadvancebookdata,bookingdate=bookingdate,roomno=roomid,
                                                    bookingguest=guestname,bookingguestphone=phone
                                                ,checkoutdate=bookenddate,bookingstatus=True,channal=channal)
            if Saveadvancebookdata:
                usermsglimit = Messgesinfo.objects.get(vendor=user)
                if channal.channalname== "self" :
                    if usermsglimit.defaultlimit > usermsglimit.changedlimit :
                        addmsg = usermsglimit.changedlimit + 2
                        Messgesinfo.objects.filter(vendor=user).update(changedlimit=addmsg)
                        profilename = HotelProfile.objects.get(vendor=user)
                        mobile_number = phone
                        user_name = "chandan"
                        val = 5
                        message_content = f"Dear guest, Your booking at {profilename.name} is confirmed. Advance payment of Rs.{advanceamount} received. Check-in date: {bookingdate}. We're thrilled to host you and make your stay unforgettable. For assistance, contact us at {profilename.contact}. -BILLZIFY"
                            
                        base_url = "http://control.yourbulksms.com/api/sendhttp.php"
                        params = {
                            'authkey': settings.YOURBULKSMS_API_KEY,
                            'mobiles': mobile_number,
                            'sender':  'BILZFY',
                            'route': '2',
                            'country': '0',
                            'DLT_TE_ID': '1707171861809414803'
                        }
                        encoded_message = urllib.parse.urlencode({'message': message_content})
                        url = f"{base_url}?authkey={params['authkey']}&mobiles={params['mobiles']}&sender={params['sender']}&route={params['route']}&country={params['country']}&DLT_TE_ID={params['DLT_TE_ID']}&{encoded_message}"
                        
                        try:
                            response = requests.get(url)
                            if response.status_code == 200:
                                try:
                                    response_data = response.json()
                                    if response_data.get('Status') == 'success':
                                        messages.success(request, 'SMS sent successfully.')
                                    else:
                                        messages.success(request, response_data.get('Description', 'Failed to send SMS'))
                                except ValueError:
                                    messages.success(request, 'Failed to parse JSON response')
                            else:
                                messages.success(request, f'Failed to send SMS. Status code: {response.status_code}')
                        except requests.RequestException as e:
                            messages.success(request, f'Error: {str(e)}')
                    else:
                        messages.error(request,'Ooooops! Looks like your message balance is depleted. Please recharge to keep sending SMS notifications to your guests.CLICK HERE TO RECHARGE!')
            else:
                messages.success(request, 'No data found matching the query')
            
        

            messages.success(request,"Booking Done")
            return redirect('advanceroombookpage')
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)
    


def todaybookingpage(request):
    try:
        if request.user.is_authenticated:
            user=request.user
            # today=datetime.date.today() 
            today = datetime.now().date()
            checkoutdate = datetime.now().date()
            changeddate = today - timedelta(days=1)
            roomdata = RoomBookAdvance.objects.filter(vendor=user,bookingdate=today,bookingstatus=True).all()
            # advancebookdata = RoomBookAdvance.objects.filter(vendor=user,bookingdate=today)
            advancebookcheckoutdata = RoomBookAdvance.objects.filter(vendor=user,checkoutdate=checkoutdate)
            
            print(changeddate)
            for i in advancebookcheckoutdata:
                if i.roomno.checkin == 4 :
                    if  i.roomno.checkin == 5:
                        pass
                    else: 
                        roomid = i.roomno.id
                        print(i.roomno.room_name,i.roomno.checkin)
                        Rooms.objects.filter(vendor=user,id=i.roomno.id).update(checkin=0) 
                else:
                    pass
            allbookdata = RoomBookAdvance.objects.filter(vendor=user,bookingdate__lte=today, checkoutdate__gt=today,checkinstatus=False)
            print(allbookdata)
            return render(request,'todayarrivalsrom.html',{'active_page':'todaybookingpage','roomdata':roomdata,'advancebookdata':allbookdata})
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)
    


def openroomclickformtodayarriwalspage(request,id):
    try:
        if request.user.is_authenticated:
            user=request.user
            room_data = Rooms.objects.filter(vendor=user,room_name=id)
            roomno=id
            roomguestdata = RoomBookAdvance.objects.filter(vendor=user,id=id).all()
            loyltydata = loylty_data.objects.filter(vendor=user,Is_active=True)
            today=datetime.now().date()
            saveguestdata = 0
            guestphone = 0
            for i in roomguestdata:
                guestphone=i.bookingguestphone
                saveguestdata = i.saveguestdata.id
            paymentdatauserfromsaveadvancedata = SaveAdvanceBookGuestData.objects.filter(vendor=user,id=saveguestdata).all()
            roomnumberdata = RoomBookAdvance.objects.filter(vendor=user,saveguestdata_id=saveguestdata)
            countrooms = len(roomnumberdata)
            # return render(request,'advanceroomclickpage.html',{'id':roomno,'countrooms':countrooms,'roomnumberdata':roomnumberdata,'room_data':room_data,'roomguestdata':roomguestdata})
            return render(request,'advanceroomclickpage.html',{'loyltydata':loyltydata,'id':roomno,'countrooms':countrooms,'roomnumberdata':roomnumberdata,'room_data':room_data,'roomguestdata':roomguestdata,'paymentdatauserfromsaveadvancedata':paymentdatauserfromsaveadvancedata})
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)
    

    
# one by one chekcin function
def chekinonebyoneguestdata(request):
    try:
        if request.user.is_authenticated and request.method=="POST":
            user=request.user
            roombookadvanceiddata = request.POST.get('roombookadvanceiddata')
            roomnodata = request.POST.get('roomnodata')
            name = request.POST.get('name')
            phone = request.POST.get('phone')
            address = request.POST.get('address')
            roombookingdata = RoomBookAdvance.objects.get(vendor=user,id=roombookadvanceiddata)
            if roombookingdata and Gueststay.objects.filter(vendor=user,guestphome=roombookingdata.bookingguestphone,checkindate__date=roombookingdata.bookingdate,checkoutdate__date=roombookingdata.checkoutdate).exists():
                guestdata = Gueststay.objects.filter(vendor=user,guestphome=roombookingdata.bookingguestphone,checkindate__date=roombookingdata.bookingdate,checkoutdate__date=roombookingdata.checkoutdate).last()
            RoomBookAdvance.objects.filter(vendor=user,id=roombookadvanceiddata).update(checkinstatus=True)
            MoreGuestData.objects.create(vendor=user,mainguest=guestdata,another_guest_name=name,another_guest_phone=phone,another_guest_address=address)
            print(roombookingdata.roomno.id)
            Rooms.objects.filter(vendor=user,id=roombookingdata.roomno.id).update(checkin=1)
            return  redirect('todaybookingpage')
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)
    



def opencheckinforadvanebooking(request,pk):
    try:
        if request.user.is_authenticated:
            user=request.user
            return render(request,'index.html')
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)
    



# advancebook page function
def advanceroomhistory(request):
    try:
        if request.user.is_authenticated:
            user=request.user

            # Get today's date
            today = timezone.now().date()

            # Define the date range
            # Example: Get dates within the next 7 days from today
            start_date = today
            end_date = today + timedelta(days=7)

            # Query to filter records within the date range and order by bookingdate
            filtered_orders = SaveAdvanceBookGuestData.objects.filter(
                vendor=user,
                bookingdate__range=(start_date, end_date)
                    ).order_by('bookingdate')
            # advanceroomdata = RoomBookAdvance.objects.filter(vendor=user).all().order_by('bookingdate')
            advanceroomsdata = SaveAdvanceBookGuestData.objects.filter(vendor=user).all().order_by('-id')
            page = request.GET.get('page', 1) 
            paginator = Paginator(advanceroomsdata, 25) 
            try: 
                advanceroomdata = paginator.page(page) 
            except PageNotAnInteger: 
                advanceroomdata = paginator.page(1) 
            except EmptyPage: 
                advanceroomdata = paginator.page(paginator.num_pages) 

            return render(request,'advancebookinghistory.html',{'filtered_orders':filtered_orders,'advanceroomdata':advanceroomdata,'active_page': 'advancebookhistory'})
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)
    



# advance details function
def advancebookingdetails(request,id):
    try:
        if request.user.is_authenticated:
            user=request.user
            guestdata = SaveAdvanceBookGuestData.objects.filter(vendor=user,id=id)
            roomdata = RoomBookAdvance.objects.filter(vendor=user,saveguestdata=id).all()
            return render(request,'advancebookingdetailspage.html',{'roomdata':roomdata,'guestdata':guestdata,'active_page': 'advancebookhistory'})
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)
    

# advance booking delete function
def advancebookingdelete(request,id):
    try:
        if request.user.is_authenticated:
            user=request.user
            saveguestid=id
            roomdata = RoomBookAdvance.objects.filter(vendor=user,saveguestdata=saveguestid,partly_checkin=False,checkinstatus=False).all()
            if roomdata: 
                for data in roomdata:
                    Rooms.objects.filter(vendor=user,id=data.roomno.id).update(checkin=0)
                # roomid = roomdata.roomno.id
                SaveAdvanceBookGuestData.objects.filter(vendor=user,id=saveguestid).delete()
                # roomchekinstatus = Rooms.objects.filter(vendor=user,id=roomid,checkin__range=[4,5]).exists()
                # if roomchekinstatus is True:
                #     Rooms.objects.filter(vendor=user,id=roomid).update(checkin=0)
                # RoomBookAdvance.objects.filter(vendor=user,id=id).delete()
                # Room_history.objects.filter(vendor=user,room_no=roomid).delete()
                # advanceroomdata = RoomBookAdvance.objects.filter(vendor=user).all()
                messages.success(request,'booking delete succesfully')
            else:
                messages.error(request,'Guest Is Stayed If You Want To Delete So cancel the folio room.')
            advanceroomdata = SaveAdvanceBookGuestData.objects.filter(vendor=user).all()
            return render(request,'advancebookinghistory.html',{'advanceroomdata':advanceroomdata,'active_page': 'advancebookhistory'})
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)
    

# add profile hotels
def addprofile(request):
    try:
        if request.user.is_authenticated and request.method=="POST":
            user=request.user
            if HotelProfile.objects.filter(vendor=user).exists():
                profiledata =  HotelProfile.objects.filter(vendor=user)
                return render(request,'profile.html',{'profiledata':profiledata})
            else:
                hotelame = request.POST.get('hotelame')
                email = request.POST.get('email')
                phoneNumber = request.POST.get('phoneNumber',0)
                address = request.POST.get('address')
                ziCode = request.POST.get('zipCode')
                country = request.POST.get('country')
                checkintime = request.POST.get('checkintime')
                checkouttime = request.POST.get('checkouttime')
                logoimg = request.FILES['logoimg']
                gstnumber = request.POST.get('gstnumber')
                HotelProfile.objects.create(vendor=user,name=hotelame,email=email,contact=phoneNumber,address=address,
                        zipcode=ziCode,gstin= gstnumber, profile_image=logoimg,counrty=country,
                        checkintimes=checkintime,checkouttimes=checkouttime)
                profiledata =  HotelProfile.objects.filter(vendor=user)
                return render(request,'profile.html',{'profiledata':profiledata})
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)
    



def updateprofile(request):
    try:
        if request.user.is_authenticated and request.method == "POST":
            user = request.user
            hotelame = request.POST.get('hotelame')
            email = request.POST.get('email')
            phoneNumber = request.POST.get('phoneNumber', 0)
            address = request.POST.get('address')
            zipCode = request.POST.get('zipCode')
            country = request.POST.get('country')
            logoimg = request.FILES.get('logonewimg')  # Use get to avoid KeyError if file is not uploaded
            gstnumber = request.POST.get('gstnumber')
            checkintime = request.POST.get('checkintime')
            checkouttime = request.POST.get('checkouttime')

            try:
                profile = HotelProfile.objects.get(vendor=user)
                profile.name = hotelame
                profile.email = email
                profile.contact = phoneNumber
                profile.address = address
                profile.zipcode = zipCode
                profile.counrty = country
                profile.gstin = gstnumber
                profile.checkintimes = checkintime
                profile.checkouttimes = checkouttime
                print(country)
                if logoimg:
                    profile.profile_image = logoimg  # Update the image only if a new one is provided
                profile.save()
            except HotelProfile.DoesNotExist:
                messages.error(request, 'Profile does not exist')

            profiledata = HotelProfile.objects.filter(vendor=user)
            return render(request, 'profile.html', {'profiledata': profiledata})

        else:
            return redirect('loginpage')  # Redirect to login if not authenticated or not a POST request
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)
    




def IGfKg(request):
    try:
        return render(request,'IGfKg.html')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)
    


import qrcode
from django.http import HttpResponse, HttpResponseNotFound
from django.conf import settings
from PIL import Image
import os
from io import BytesIO
from django.core.files.base import ContentFile

def generate_qr(request, url):
    # Generate the QR code
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # Use high error correction to allow for logo
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        qr_image = qr.make_image(fill_color="black", back_color="white").convert('RGB')

        # Get the logo image path from the static files
        logo_path = os.path.join(settings.BASE_DIR, 'app', 'static', 'img', 'newshadowlogo.png')
        print(f"Logo path: {logo_path}")  # Debug statement to print the logo path

        if not os.path.exists(logo_path):
            print(f"Logo file not found at: {logo_path}")
            return HttpResponseNotFound("Logo image not found.")
        
        try:
            # Open the logo image
            logo = Image.open(logo_path)
            print("Logo image opened successfully.")  # Debug statement to confirm the image is opened
            
            # Ensure the logo image has an alpha channel
            logo = logo.convert("RGBA")

            # Calculate logo size and position
            qr_width, qr_height = qr_image.size
            logo_size = qr_width // 5
            logo = logo.resize((logo_size, logo_size), Image.ANTIALIAS)

            # Calculate logo position to center it on the QR code
            logo_position = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)

            # Paste the logo onto the QR code
            qr_image.paste(logo, logo_position, logo)

        except Exception as e:
            print(f"Error opening/logo image: {e}")
            return HttpResponse("Error opening/logo image.", status=500)

        user=request.user
        # Create an HTTP response with the QR code image
        # Save the QR code image to an in-memory file
        buffer = BytesIO()
        qr_image.save(buffer, format="PNG")
        buffer.seek(0)

        # Create a Django file from the in-memory file
        file_name = f'user_{user.id}_qr.png'
        file_content = ContentFile(buffer.read(), name=file_name)

        # Save the file to the model's qr_code field
        # reviewQr.qrimage.save(file_name, file_content, save=True)
        # reviewQr.objects.create(vendor=user,qrimage=file_content)
        response = HttpResponse(content_type="image/png")
        qr_image.save(response, "PNG")
        return response
    
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)
    


# views.py
from django.shortcuts import render

def qr_code(request):
    url = "https://www.billzify.com/IGfKg/120"  # Replace this with your desired URL
    return render(request, 'qr_code.html', {'url': url})
# isko chalane ke liye url map krni hogi empty us din jase 


# from django.shortcuts import render

# def subscription_expired(request):
#     return render(request, 'login.html')

# def no_subscription(request):
#     return render(request, 'login.html')


def password_reset_request(request):
    try:
        if request.method == 'POST':
            username = request.POST['username']
            new_password = request.POST['new_password']
            try:
                user = User.objects.get(username=username)
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password reset successfully!')
                return render(request, 'password_reset_form.html')
            except User.DoesNotExist:
                messages.error(request, 'Invalid username')
        return render(request, 'password_reset_form.html')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)
    

from django.contrib.auth import logout as auth_logout

def logout_view(request):
    auth_logout(request)  # Log out the user
    response = redirect('loginpage')  # Redirect to the login page or any other page
    # Clear all cookies
    for cookie in request.COOKIES:
        response.delete_cookie(cookie)
    return response



from django.core.exceptions import ValidationError
def deleteitemstofolio(request):
    try:
        if request.user.is_authenticated and request.method == "POST":
            user = request.user
            invoiceid = request.POST.get('invoiceid')
            invoiceitemsid = request.POST.get('invoiceitemsid')
            if Invoice.objects.filter(vendor=user,id=invoiceid).exists():
                if InvoiceItem.objects.filter(vendor=user,id=invoiceitemsid,invoice_id=invoiceid).exists():
                    invoiceitemdata = InvoiceItem.objects.get(vendor=user,id=invoiceitemsid,invoice_id=invoiceid)
                    print(invoiceitemdata.invoice.customer,invoiceitemdata.description,invoiceitemdata.total_amount,invoiceitemdata.cgst_rate)
                    try:
                        int_value = int(invoiceitemdata.description)
                        # If successful, filter using Q objects to handle both int and str queries
                        if  Rooms.objects.filter(vendor=user,room_name=int_value,price=invoiceitemdata.price).exists():
                            pass
                    except (ValueError, TypeError, ValidationError):
                        if invoiceitemdata.cgst_rate == 0.00:
                            invoiceamt = invoiceitemdata.total_amount
                            invoicedata = Invoice.objects.get(vendor=user,id=invoiceid)
                            totalamt = invoicedata.total_item_amount - invoiceamt
                            subtotalamt = invoicedata.subtotal_amount - invoiceamt
                            grandtotalamt = invoicedata.grand_total_amount - invoiceamt
                            Invoice.objects.filter(vendor=user,id=invoiceid).update(total_item_amount=totalamt,subtotal_amount=subtotalamt,grand_total_amount=grandtotalamt)
                            InvoiceItem.objects.filter(vendor=user,id=invoiceitemsid,invoice_id=invoiceid).delete()
                            
                        else:
                            invoiceamt = invoiceitemdata.total_amount
                            qtys = invoiceitemdata.quantity_likedays
                            priceproduct = invoiceitemdata.price
                            print("acutal price=",priceproduct*qtys,"taxprice =",invoiceamt-priceproduct*qtys)
                            invoicedata = Invoice.objects.get(vendor=user,id=invoiceid)
                            totalamt = invoicedata.total_item_amount - priceproduct*qtys
                            subtotalamt = invoicedata.subtotal_amount - priceproduct*qtys
                            cgstamt = invoicedata.sgst_amount - (invoiceamt-priceproduct*qtys)/2
                            gstamt = invoicedata.gst_amount - (invoiceamt-priceproduct*qtys)/2
                            grandtotalamt = invoicedata.grand_total_amount - invoiceamt
                            Invoice.objects.filter(vendor=user,id=invoiceid).update(gst_amount=gstamt,sgst_amount=cgstamt,total_item_amount=totalamt,subtotal_amount=subtotalamt,grand_total_amount=grandtotalamt)
                            InvoiceItem.objects.filter(vendor=user,id=invoiceitemsid,invoice_id=invoiceid).delete()
                            
                    
                else:
                    messages.error(request, 'Invoice item not exists')
            else:
                messages.error(request, 'Invoice does not exist')
            ckinvcdata = Invoice.objects.get(vendor=user,id=invoiceid)
            cstmrid = ckinvcdata.customer.id
            return redirect('invoicepage', id=cstmrid)
        
        else:
            return redirect('loginpage')
        
    except Exception as e:
            return render(request, '404.html', {'error_message': str(e)}, status=500)    


    