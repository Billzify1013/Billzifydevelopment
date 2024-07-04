from django.shortcuts import render, redirect,HttpResponse 
from . models import *
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
import datetime
from datetime import datetime, timedelta
from django.db.models import Max
import requests
from django.conf import settings
import urllib.parse
from django.db.models import Sum


def setting(request):
    try:
        if request.user.is_authenticated:
            user=request.user
            loyltydata = loylty_data.objects.filter(vendor=user)
            taxdata = Taxes.objects.filter(vendor=user)
            category = RoomsCategory.objects.filter(vendor=user)
            return render(request,'settings.html',{'active_page': 'setting','category':category,'loyltydata':loyltydata,'taxdata':taxdata})
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)

def activeloylty(request):
    try:
        if request.user.is_authenticated and request.method=="POST":
            user=request.user
            loyltypersantage = request.POST.get('loyltypersantage')
            loylty_data.objects.create(vendor=user,loylty_rate_prsantage=loyltypersantage,Is_active=True)
            messages.success(request,'Loylty Activated')
            return redirect('setting')
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)

def updateloylty(request):
    try:
        if request.user.is_authenticated and request.method=="POST":
            user=request.user
            loyltypersantage = request.POST.get('loyltypersantage')
            checkbox = request.POST.get('checkbox')
            print(checkbox)
            if checkbox is None:
                loylty_data.objects.filter(vendor=user).update(loylty_rate_prsantage=loyltypersantage,Is_active=False)
                
                
            else:
                loylty_data.objects.filter(vendor=user).update(loylty_rate_prsantage=loyltypersantage,Is_active=True)
            messages.success(request,'Loylty updates Succesfully')
            return redirect('setting')
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)

    
def deletetaxitem(request,id):
    try:
        if request.user.is_authenticated:
            user=request.user
            if Taxes.objects.filter(vendor=user,id=id).exists():
                Taxes.objects.filter(vendor=user,id=id).delete()
                messages.success(request,'Item Delete Succesfully')
            else:
                messages.error(request,'Item note matched')
            return redirect('setting')
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)
    
def deletecategory(request,id):
    try:
        if request.user.is_authenticated:
            user=request.user
            if RoomsCategory.objects.filter(vendor=user,id=id).exists():
                RoomsCategory.objects.filter(vendor=user,id=id).delete()
                messages.success(request,'Category Delete Succesfully')
            else:
                messages.error(request,'Category note matched')
            return redirect('setting')
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)

def websetting(request):
    try:
        if request.user.is_authenticated:
            user=request.user
            amenities = amainities.objects.filter(vendor=user)
            gallary = webgallary.objects.filter(vendor=user)
            reviewsdata = webreview.objects.filter(vendor=user)
            category = RoomsCategory.objects.filter(vendor=user)
            offers = offerwebsitevendor.objects.filter(vendor=user)
            return render(request,'websettings.html',{'active_page': 'websetting','offers':offers,'category':category,'reviewsdata':reviewsdata,'amenities':amenities,'gallary':gallary})
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)
    
def deleteamenities(request,id):
    try:
        if request.user.is_authenticated:
            user=request.user
            if amainities.objects.filter(vendor=user,id=id).exists():
                amainities.objects.filter(vendor=user,id=id).delete()
                messages.success(request,'Amenities Delete Succesfully')
            else:
                messages.error(request,'Amenities note matched')
            return redirect('websetting')
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)

def deleteimages(request,id):
    try:
        if request.user.is_authenticated:
            user=request.user
            if webgallary.objects.filter(vendor=user,id=id).exists():
                webgallary.objects.filter(vendor=user,id=id).delete()
                messages.success(request,'Amainities Delete Succesfully')
            else:
                messages.error(request,'Amainities note matched')
            return redirect('websetting')
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)

























# ajax book date all rooms data
@csrf_exempt
def getloyltydataajax(request):
    try:
        if request.user.is_authenticated and request.method == "POST":
            user = request.user
            Mobile = request.POST['Mobile']
            data = loylty_Guests_Data.objects.filter(Q(vendor=user, guest_contact=Mobile)).all()
            if data.exists():
                return JsonResponse(list(data.values('id', 'guest_name', 'guest_contact', 'loylty_point')), safe=False)
            else:
                return JsonResponse({'error': 'No data found matching the query'}, status=404)
        else:
            return JsonResponse({'error': 'User not authenticated or invalid request method'}, status=400)
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)
         
@csrf_exempt
def deleteloyltyajaxdata(request):
    try:
        if request.method == "POST":
            if request.user.is_authenticated:
                user = request.user
                Mobile = request.POST.get('Mobile')
                try:
                    # Update loyalty points to 0 for the given vendor and guest contact
                    data = loylty_Guests_Data.objects.filter(vendor=user, guest_contact=Mobile).update(loylty_point=0)
                    
                    if data > 0:  # Check if any records were updated
                        updated_data = loylty_Guests_Data.objects.filter(vendor=user, guest_contact=Mobile)
                        return JsonResponse(list(updated_data.values('id', 'guest_name', 'guest_contact', 'loylty_point')), safe=False)
                    else:
                        return JsonResponse({'error': 'No data found matching the query'}, status=404)
                
                except loylty_Guests_Data.DoesNotExist:
                    return JsonResponse({'error': 'No data found matching the query'}, status=404)
                
            else:
                return JsonResponse({'error': 'User not authenticated'}, status=401)
        
        else:
            return JsonResponse({'error': 'Invalid request method'}, status=405)
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)    
    

def creditmanage(request):
    try:
        if request.user.is_authenticated:
            user = request.user
            customerdata = CustomerCredit.objects.filter(vendor=user)
            total_amount = CustomerCredit.objects.filter(vendor=user).aggregate(total=Sum('amount'))['total']
            return render(request,'showcredit.html',{'customerdata':customerdata,'active_page':'creditmanage','total_amount':total_amount})
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)    
    
        
def addcreditcustomer(request):
    try:
        if request.user.is_authenticated and request.method == "POST":
            user = request.user
            name = request.POST.get('name')
            phone = request.POST.get('phone')
            amount = request.POST.get('amount')
            duedate = request.POST.get('duedate')
            if CustomerCredit.objects.filter(vendor=user,customer_name=name,phone=phone,amount=amount,due_date=duedate).exists():
                return redirect('creditmanage')
            else:
                CustomerCredit.objects.create(vendor=user,customer_name=name,phone=phone,amount=amount,due_date=duedate,invoice=None)
                messages.success(request,"Data Added Succesfully!")
                return redirect('creditmanage')
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)    
    
    
    
def saveinvoicetocredit(request,id):
    try:
        if request.user.is_authenticated:
            user = request.user
            dataid = id
            if CustomerCredit.objects.filter(vendor=user,id=dataid).exists():
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

                invcdata = CustomerCredit.objects.get(vendor=user,id=dataid)
                if invcdata.invoice is None:
                    CustomerCredit.objects.filter(vendor=user,id=dataid).delete()
                    messages.success(request,"Credit Sattle done Succesfully!")
                    return redirect('creditmanage')
                else:
                    invoiceid = invcdata.invoice.id
                    if Invoice.objects.filter(vendor=user,id=invoiceid).exists():
                        
                        grandtotalamt = invcdata.invoice.grand_total_amount
                        Invoice.objects.filter(vendor=user,id=invoiceid).update(invoice_number=invoice_number,invoice_status=True,modeofpayment="cash",cash_amount=grandtotalamt,online_amount=0.00)
                        CustomerCredit.objects.filter(vendor=user,id=dataid).delete()
                        messages.success(request,"Invoice Sattle done Succesfully!")
                        return redirect('creditmanage')
            else:
                return redirect('creditmanage')
        else:
            return redirect('loginpage')
    except Exception as e:
            return render(request, '404.html', {'error_message': str(e)}, status=500)    
    
        
def searchcredit(request):
    try:
        if request.user.is_authenticated and request.method == "POST":
            user = request.user
            name = request.POST.get('name', '').strip()
            phone = request.POST.get('phone', '').strip()
            date = request.POST.get('date', '').strip()
            
            if not name and not phone and not date:
                messages.error(request, "Please provide at least one search criterion.")
                return redirect('creditmanage') 

            # Start with all records for the current vendor
            queryset = CustomerCredit.objects.filter(vendor=user)

            # Apply filters if any field is provided
            if name:
                queryset = queryset.filter(customer_name__icontains=name)
            elif phone:
                queryset = queryset.filter(phone__icontains=phone)
            elif date:
                queryset = queryset.filter(due_date=date)
            if not queryset.exists():
                messages.error(request, "No data found matching the criteria.")
                return redirect('creditmanage')  # Replace with your search form view name

            # Return results even if none of the fields were provided (i.e., all records for the vendor)
            return render(request, 'showcredit.html', {'customerdata': queryset,'active_page':'creditmanage'})
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)    
    
            
def Messages(request):
    try:
        if request.user.is_authenticated:
            user = request.user
            profiledata = HotelProfile.objects.get(vendor=user)
            return render(request,'messages.html',{'active_page':'Messages','profiledata':profiledata})
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)    
    
        
def sendwelcomemsg(request):
    try:
        if request.user.is_authenticated and request.method == "POST":
            user = request.user
            name = request.POST.get('name')
            phone = request.POST.get('phone')
            usermsglimit = Messgesinfo.objects.get(vendor=user)
            if usermsglimit.defaultlimit > usermsglimit.changedlimit :
                    addmsg = usermsglimit.changedlimit + 2
                    Messgesinfo.objects.filter(vendor=user).update(changedlimit=addmsg)
                    profilename = HotelProfile.objects.get(vendor=user)
                    mobile_number = phone
                    user_name = "chandan"
                    val = 5
                    message_content = f"Dear {name}, Welcome to {profilename.name}. We are delighted to have you with us and look forward to making your stay enjoyable. Thank you for choosing us. - Billzify"
                        
                    base_url = "http://control.yourbulksms.com/api/sendhttp.php"
                    params = {
                        'authkey': settings.YOURBULKSMS_API_KEY,
                        'mobiles': phone,
                        'sender':  'BILZFY',
                        'route': '2',
                        'country': '0',
                        'DLT_TE_ID': '1707171889808133640'
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
            
            return redirect('Messages')
        
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)    
    
            
    




def sendloyaltymsg(request):
    try:
        if request.user.is_authenticated and request.method == "POST":
            user = request.user
            points = request.POST.get('points')
            phone = request.POST.get('phone')
            usermsglimit = Messgesinfo.objects.get(vendor=user)
            if usermsglimit.defaultlimit > usermsglimit.changedlimit :
                    addmsg = usermsglimit.changedlimit + 2
                    Messgesinfo.objects.filter(vendor=user).update(changedlimit=addmsg)
                    profilename = HotelProfile.objects.get(vendor=user)
                    message_content = f"Dear Guest, you have earned loyalty points worth Rs {points} at {profilename.name}. We look forward to welcoming you back soon. - Billzify"
                        
                    base_url = "http://control.yourbulksms.com/api/sendhttp.php"
                    params = {
                        'authkey': settings.YOURBULKSMS_API_KEY,
                        'mobiles': phone,
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
            
            return redirect('Messages')
        
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)    
    
    