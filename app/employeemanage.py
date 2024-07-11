from django.shortcuts import render, redirect
from . models import *
import datetime
from datetime import  timedelta
from django.contrib import messages
from datetime import datetime, timedelta
from django.db.models import Q
from django.db.models import OuterRef, Subquery
from django.db.models import Avg, F, ExpressionWrapper, DurationField
from django.shortcuts import render, get_object_or_404
import json
import requests
from django.conf import settings
import urllib.parse
from django.db.models import F, ExpressionWrapper, DurationField, Avg, Case, When, Value, DateTimeField, OuterRef, Subquery
from django.db.models import Count


def employee(request):
    try:
        if request.user.is_authenticated:
            user=request.user
            empdata = Employee.objects.filter(vendor=user).all()
            return render(request,'employeepage.html',{'active_page': 'employee','empdata':empdata})
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)    
    
         
def addemployee(request):
    try:
        if request.user.is_authenticated and request.method=="POST":
            user=request.user
            firstname = request.POST.get('firstname')
            lastname = request.POST.get('lastname')
            dob = request.POST.get('dob')
            joindate = request.POST.get('joindate')
            Position = request.POST.get('Position')
            Department = request.POST.get('Department')
            phone = request.POST.get('phone')
            salarybyday = request.POST.get('salarybyday')
            workinghour = request.POST.get('workinghour')
            Employee.objects.create(vendor=user,first_name=firstname,last_name=lastname,date_of_birth=dob,
                    date_of_joining=joindate,position=Position,department=Department,employee_contact=phone,salarybyday=salarybyday
                    ,working_hours=workinghour)
            empdata = Employee.objects.filter(vendor=user).all()
            return render(request,'employeepage.html',{'active_page': 'employee','empdata':empdata})
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)    
    
         
def deleteemployee(request,id):
    try:
        if request.user.is_authenticated:
            user=request.user
            if Employee.objects.filter(vendor=user,id=id).exists():
                Employee.objects.filter(vendor=user,id=id).delete()
                empdata = Employee.objects.filter(vendor=user).all()
                return render(request,'employeepage.html',{'active_page': 'employee','empdata':empdata})
            else:
                empdata = Employee.objects.filter(vendor=user).all()
                return render(request,'employeepage.html',{'active_page': 'employee','empdata':empdata})
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)    
    
             
def updateemployee(request,id):
    try:
        if request.user.is_authenticated:
            user=request.user
            # Employee.objects.filter(vendor=user,id=id).update()
            empdata = Employee.objects.filter(vendor=user).all()
            return render(request,'employeepage.html',{'active_page': 'employee','empdata':empdata})
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)    
    
         
    

def dailyattendance(request):
    try:
        if request.user.is_authenticated:
            user=request.user
            current_date = datetime.now().date()
            current_time = datetime.now().time()  # Get current time
            # subtracted_time = (datetime.combine(datetime.now(), current_time) - timedelta(hours=24)).time()
            oneminuscurrent_date = current_date - timedelta(days=1)
            current_datetime = datetime.now()
            subtracted_time = current_datetime - timedelta(hours=24)
            # Find the most recent date that has data
            most_recent_date = Employee.objects.filter(
                vendor=user
            ).aggregate(
                max_date=Max('dailymanagement__date')
            )['max_date']
            
            
            current_time = datetime.now().time()
            twenty_four_hours_ago = (datetime.combine(datetime.today(), current_time) - timedelta(hours=24)).time()
            
            # new chat gpt code jo chal raha hai
            current_datetime = datetime.now()
            subtracted_time = current_datetime - timedelta(hours=24)
            lastday = current_datetime - timedelta(days=1)

            

            if most_recent_date:
                employees_not_checked_out = Employee.objects.filter(
                    Q(vendor=user) &
                    Q(dailymanagement__check_out_time=None) &
                    Q( Q(Q(dailymanagement__date=lastday) & Q(dailymanagement__check_out_time=None))) &
                    Q(dailymanagement__check_in_time__gte=subtracted_time)
                ).distinct()
            else:
                employees_not_checked_out = Employee.objects.none()  # No data found

            employees_current_date_not_checked_out = Employee.objects.filter(
                    Q(vendor=user) &
                    Q(dailymanagement__check_out_time=None) &
                    Q( dailymanagement__date=current_date ) 
                ).distinct()
            employees_not_checked_out = employees_not_checked_out | employees_current_date_not_checked_out
            employees_not_checked_in = Employee.objects.filter(
                vendor=user
            ).exclude(id__in=employees_not_checked_out.values('id'))
            return render(request,'dailyattendance.html',{'active_page': 'dailyattendance',
                        'employees_not_checked_in':employees_not_checked_in,'employees_not_checked_out':employees_not_checked_out,})
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)    
    
     



    
def employeecheckin(request,dsd):
    try:
        if request.user.is_authenticated:
            user=request.user
            current_date = datetime.now().date()
            current_time = datetime.now().time()
            if DailyManagement.objects.filter(vendor=user,employee_id=dsd,date=current_date).exists():
                messages.error(request,"Employees completed their jobs today and will check in again tomorrow.")
                return redirect('dailyattendance')
            else:
                DailyManagement.objects.create(vendor=user,employee_id=dsd,date=current_date,check_in_time=current_time)
                messages.success(request,"Employees successfully checked in.")
                return redirect('dailyattendance')
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)    
    
         
def employeecheckout(request,dsd):
    try:
        if request.user.is_authenticated:
            user=request.user
            current_date = datetime.now().date()
            current_time = datetime.now().time()
            lastday = current_date - timedelta(days=1)
            if DailyManagement.objects.filter(vendor=user,employee_id=dsd,date=current_date).exists():
                DailyManagement.objects.filter(vendor=user,employee_id=dsd,date=current_date).update(check_out_time=current_time)
                messages.success(request,"Employees successfully checked Out.")
                return redirect('dailyattendance')
            
            elif DailyManagement.objects.filter(vendor=user,employee_id=dsd,date=lastday).exists() and  not DailyManagement.objects.filter(vendor=user,employee_id=dsd,date=current_date).exists():
                DailyManagement.objects.filter(vendor=user,employee_id=dsd,date=lastday).update(check_out_time=current_time)
                messages.success(request,"Employees successfully checked Out.")
                return redirect('dailyattendance')
            else:
                return redirect('dailyattendance')
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)    
    
         
def employeehalfday(request,dsd):
    try:
        if request.user.is_authenticated:
            user=request.user
            current_date = datetime.now().date()
            current_time = datetime.now().time()
            if DailyManagement.objects.filter(vendor=user,employee_id=dsd,date=current_date).exists():
                DailyManagement.objects.filter(vendor=user,employee_id=dsd,date=current_date).update(halfday=True,check_out_time=current_time)
                messages.success(request,"Employees successfully checked Out in Halfday.")
                return redirect('dailyattendance')
            else:
                return redirect('dailyattendance')
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)    
    
     

def attendancepage(request):
    try:
        if request.user.is_authenticated:
            user=request.user
            current_date = datetime.now().date()
            empsdata = DailyManagement.objects.filter(vendor=user).all()
            datas = Employee.objects.annotate(attendance_count=Count('dailymanagement')).filter(vendor=user,dailymanagement__date__lt=current_date).values()
            return render(request,'attencancepage.html',{'empdata':datas,'active_page': 'attendancepage',})
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)    
    
     
def employeereport(request,eid):
    try:
        if request.user.is_authenticated:
            user=request.user
            empattendancedata = DailyManagement.objects.filter(vendor=user,employee_id=eid).order_by('date')
            start_date = DailyManagement.objects.filter(vendor=user,employee_id=eid).earliest('date').date
            last_date = DailyManagement.objects.filter(vendor=user,employee_id=eid).latest('date').date
            
            s=str(start_date)
            e=str(last_date)
            start_date =  datetime.strptime(s, '%Y-%m-%d').date()
            end_date = datetime.strptime(e, '%Y-%m-%d').date()
            # Calculate the difference in days and add 1
            dayscount = (end_date - start_date).days + 1
            
            all_dates = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]
            present_dates = DailyManagement.objects.filter(vendor=user,employee_id=eid,date__range=[start_date, end_date]).values_list('date', flat=True)
        
            present_dates_set = set(present_dates)
            lost_days = [d for d in all_dates if d not in present_dates_set]
            leavsday = len(lost_days)
            
            comeday = dayscount - leavsday
            halfdaycount = DailyManagement.objects.filter(vendor=user,employee_id=eid,halfday=True).count()
            fulldaycount = DailyManagement.objects.filter(vendor=user,employee_id=eid,halfday=False).count()
            # create salary function start
            employe = Employee.objects.get(vendor=user,id=eid)
            salary = employe.salarybyday
            halfdaysalcount = halfdaycount/2
            totalsalaryday = comeday - halfdaysalcount
            totalsalary = totalsalaryday * salary
            
        

            # Get the specific employee
            employee = get_object_or_404(Employee, id=eid)
            

            # Fetch all DailyManagement entries for this employee
            daily_management_entries = DailyManagement.objects.filter(vendor=user, employee=employee)

            # Initialize variables for calculating total working time
            total_working_seconds = 0
            valid_entries_count = 0

            for entry in daily_management_entries:
                check_in_datetime = datetime.combine(entry.date, entry.check_in_time)

                if entry.check_out_time:
                    # Determine the checkout date (same date or next day)
                    check_out_date = entry.date if entry.check_out_time >= entry.check_in_time else entry.date + timedelta(days=1)
                    check_out_datetime = datetime.combine(check_out_date, entry.check_out_time)

                    # Calculate working duration
                    working_duration = check_out_datetime - check_in_datetime
                    total_working_seconds += working_duration.total_seconds()
                    valid_entries_count += 1

            if valid_entries_count > 0:
                avg_working_seconds = total_working_seconds / valid_entries_count
                avg_working_hours = avg_working_seconds / 3600
                avg_working_time_in_hours = round(avg_working_hours, 2)
            else:
                avg_working_time_in_hours = 0
            return render(request,'attendancereportpage.html',{'empattendancedata':empattendancedata,'active_page': 'attendancepage','start_date':s,'last_date':e,'dayscount':dayscount,'leavsday':leavsday,'comeday':comeday
                                                            ,'avg_working_time_in_hours':avg_working_time_in_hours,'fulldaycount':fulldaycount,'salary':salary,'halfdaycount':halfdaycount,'totalsalaryday':totalsalaryday,'totalsalary':totalsalary})
        
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)    
    
     
def addsalary(request):
    try:
        if request.user.is_authenticated and request.method=="POST":
            user=request.user
            employeeid = request.POST.get('employeeid')
            startdate = request.POST.get('startdate')
            enddate = request.POST.get('enddate')
            salarytotalday = request.POST.get('salarytotalday')
            salary = request.POST.get('salary')
            bonus = request.POST.get('bonus')
            descount = request.POST.get('descount')
            start_date_obj = datetime.strptime(startdate, '%Y-%m-%d').date()
            end_date_obj = datetime.strptime(enddate, '%Y-%m-%d').date()
            today = datetime.now().date()
            
            SalaryManagement.objects.create(vendor=user,employee_id=employeeid,salary_date=today,start_date=start_date_obj,
                                end_date=end_date_obj,salary_days=salarytotalday,basic_salary=salary,bonus=bonus,deductions=descount)
            
            if DailyManagement.objects.filter(vendor=user,employee_id=employeeid).exists():
                DailyManagement.objects.filter(vendor=user,employee_id=employeeid).delete()
                usermsglimit = Messgesinfo.objects.get(vendor=user)
                empdata = Employee.objects.get(vendor=user,id=employeeid)
                empphone = empdata.employee_contact
                empname = empdata.first_name
                hoteldata = HotelProfile.objects.get(vendor=user)
                hotelname = hoteldata.name
                if usermsglimit.defaultlimit > usermsglimit.changedlimit :
                        addmsg = usermsglimit.changedlimit + 2
                        Messgesinfo.objects.filter(vendor=user).update(changedlimit=addmsg)
                        profilename = HotelProfile.objects.get(vendor=user)
                        mobile_number = empphone
                        user_name = empname
                        val = 5
                        message_content = f"Hello {empname}, your salary for {salary} has been successfully credited. We value your ongoing efforts and contributions. Best regards, {hotelname} - Billzify"
                            
                        base_url = "http://control.yourbulksms.com/api/sendhttp.php"
                        params = {
                            'authkey': settings.YOURBULKSMS_API_KEY,
                            'mobiles': empphone,
                            'sender':  'BILZFY',
                            'route': '2',
                            'country': '0',
                            'DLT_TE_ID': '1707171992237495364'
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
                
                return redirect('attendancepage')
            else:
                return redirect('attendancepage')
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)    
    
         
def payslippage(request):
    try:
        if request.user.is_authenticated:
            user=request.user
            empdata = SalaryManagement.objects.filter(vendor=user)
            return render(request,'payslippage.html',{'empdata':empdata,'active_page': 'payslippage',})
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)    
    
     
def showpayslip(request,eid):
    try:
        if request.user.is_authenticated:
            user=request.user
            empdata = SalaryManagement.objects.filter(vendor=user)
            employeedata = SalaryManagement.objects.filter(vendor=user,id=eid)
            return render(request,'payslippage.html',{'empdata':empdata,'employeedata':employeedata,'active_page': 'payslippage',})
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)    
    
     
def eventpackage(request):
    try:
        if request.user.is_authenticated:
            user=request.user
            eventdata = Events.objects.filter(vendor=user)
            tax = Taxes.objects.filter(vendor=user).all()
            return render(request,'eventpackagepage.html',{'active_page': 'eventpackage','tax':tax,'eventdata':eventdata})
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)    
    
         
def createevent(request):
    try:
        if request.user.is_authenticated and request.method=="POST":
            user=request.user
            eventname = request.POST.get('eventname')
            price = request.POST.get('price')
            taxcategory = request.POST.get('taxcategory')
            description = request.POST.get('description')
            termscondition = request.POST.get('termscondition')
            hsncode = request.POST.get('hsncode')
            Events.objects.create(vendor=user,eventname=eventname,eventprice=price,eventax_id=taxcategory,description=description,termscondition=termscondition,Hsn_sac=hsncode)
            eventdata = Events.objects.filter(vendor=user)
            tax = Taxes.objects.filter(vendor=user).all()
            return render(request,'eventpackagepage.html',{'active_page': 'eventpackage','tax':tax,'eventdata':eventdata})
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)    
    
     
def searchdateevent(request):
    try:
        if request.user.is_authenticated and request.method=="POST":
            user=request.user
            startdate = request.POST.get('startdate')
            enddate = request.POST.get('enddate')
            dataid = request.POST.get('dataid')
            start_date = datetime.strptime(startdate, '%Y-%m-%d').date()
            end_date=datetime.strptime(enddate, '%Y-%m-%d').date()
            eventdata = Events.objects.filter(vendor=user,id=dataid)
            if EventBookGuest.objects.filter(vendor=user,event_id=dataid,start_date__lte=end_date,end_date__gte=start_date).exists():
                errordata = EventBookGuest.objects.filter(vendor=user,event_id=dataid,start_date__lte=end_date,end_date__gte=start_date)
                for i in errordata:
                    stdate = i.start_date
                    edate = i.end_date

                messages.error(request,f'This Event Booked For this date    STARTDATE:{stdate}  TO   ENDDATE:{edate}')
                return redirect('eventpackage')
            else:
                return render(request,'bookeventpage.html',{'eventdata':eventdata,'active_page': 'eventpackage','startdate':startdate,'enddate':enddate})
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)    
    
        

def billingplanpage(request):
    try:
        if request.user.is_authenticated:
            user = request.user

            # Get the latest subscription for the user
            subscription = Subscription.objects.filter(user=user).order_by('-id').first()
        
            if subscription:
                startdate = subscription.start_date
                enddate = subscription.end_date

                # Calculate the necessary date ranges
                bookingdate = startdate
                checkoutdate = enddate
                today = datetime.now().date()
                totalday = (checkoutdate - bookingdate).days
                completed_days = (today - bookingdate).days

                dayswidth = (completed_days / totalday) * 100 if totalday != 0 else 0

                # Calculate the remaining days until checkout
                remaining_days = (checkoutdate - today).days

                # Get message info for the user, or set default values
                msgdata = Messgesinfo.objects.filter(vendor=user).first()
                if msgdata:
                    totalmsg = msgdata.defaultlimit
                    usemsg = msgdata.changedlimit
                else:
                    totalmsg = 1
                    usemsg = 0

                remainmsg = totalmsg - usemsg
                totalwidthmsg = (usemsg / totalmsg) * 100 if totalmsg != 0 else 0

                fiftyper = 50
                planname = subscription.plan.name
                planenddate = subscription.end_date
                return render(request, 'billingplanpage.html', {
                    'planname':planname,
                    'planenddate':planenddate,
                    'totalday': totalday,
                    'completedays': completed_days,
                    'dayswidth': dayswidth,
                    'fiftyper': fiftyper,
                    'reaminday': remaining_days,
                    'totalmsg': totalmsg,
                    'usemsg': usemsg,
                    'remainmsg': remainmsg,
                    'totalwidthmsg': totalwidthmsg
                })
            else:
                return render(request, 'index.html')

        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)    
    
     

def createeventbooking(request):
    try:
        if request.user.is_authenticated and request.method=="POST":
            user=request.user
            customername = request.POST.get('customername')
            customeremail = request.POST.get('customeremail')
            customerphone = request.POST.get('customerphone')
            customeraddress = request.POST.get('customeraddress')
            customergstin = request.POST.get('customergstin')
            totalamount = request.POST.get('totalamount')
            discountamount = request.POST.get('discountamount')
            subtotal = request.POST.get('subtotal')
            taxamount = request.POST.get('taxamount')
            advanceamount = request.POST.get('advanceamount')
            reamainingamount = request.POST.get('reamainingamount')
            eventid = request.POST.get('eventid')
            startdate = request.POST.get('startdate')
            enddate = request.POST.get('enddate')
            state = request.POST.get('STATE')
            userstatedata = HotelProfile.objects.get(vendor=user)
            userstate = userstatedata.zipcode
            if userstate == state:
                taxtypes = "GST"
            else:
                taxtypes = "IGST"
            grandstotal = float(subtotal) + float(taxamount)
            EventBookGuest.objects.create(vendor=user,customername=customername,guestemail=customeremail,customer_contact=customerphone,
                        customeraddress=customeraddress,customergst=customergstin,total=totalamount,discount=discountamount,
                            subtotal=subtotal,taxamount=taxamount,advanceamount=advanceamount,reamainingamount=reamainingamount,event_id=eventid,
                            start_date=startdate,end_date=enddate,taxtype=taxtypes,Grand_total_amount= grandstotal)
            return render(request,'upcomingevents.html')
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)    
    
         
def upcomingevent(request):
    try:
        if request.user.is_authenticated:
            user=request.user
            eventdata = EventBookGuest.objects.filter(vendor=user)
            return render(request,'upcomingevents.html',{'active_page': 'upcomingevent','eventdata':eventdata})
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)    
    
         
def deleteupcomingevent(request,id):
    try:
        if request.user.is_authenticated:
            user=request.user
            eventdata = EventBookGuest.objects.filter(vendor=user)
            if EventBookGuest.objects.filter(vendor=user,id=id).exists():
                EventBookGuest.objects.filter(vendor=user,id=id).delete()
                return render(request,'upcomingevents.html',{'active_page': 'upcomingevent','eventdata':eventdata})
            else:
                return render(request,'upcomingevents.html',{'active_page': 'upcomingevent','eventdata':eventdata})
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)    
    
         
def showeventinvoice(request,id):
    try:
        if request.user.is_authenticated:
            user=request.user
            if EventBookGuest.objects.filter(vendor=user,id=id).exists():
                eventdata = EventBookGuest.objects.filter(vendor=user,id=id).all()
                events = Events.objects.filter(vendor=user)
                profiledata = HotelProfile.objects.filter(vendor=user).all()
                return render(request,'eventinvoice.html',{'profiledata':profiledata,'eventdata': eventdata,'events':events,})
            else:
                eventdata = EventBookGuest.objects.filter(vendor=user)
                return render(request,'upcomingevents.html',{'active_page': 'upcomingevent','eventdata':eventdata})
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)    
    
         
from django.db.models import Max
def createeventinvoice(request,id):
    try:
        if request.user.is_authenticated:
            user=request.user
            if EventBookGuest.objects.filter(vendor=user,id=id,status=False):
                current_date = datetime.now().date()
                # Get the current date
                invccurrentdate = datetime.now().date()

                # Update the EventBookGuest object with status and invoice date
                event_obj = EventBookGuest.objects.filter(vendor=user, id=id).first()
                if event_obj:
                    event_obj.status = True
                    event_obj.invoice_date = invccurrentdate
                    event_obj.reamainingamount = 0
                    event_obj.save()

                # Fetch the maximum invoice number for today for the given user
                max_invoice_today = EventBookGuest.objects.filter(
                    vendor=user,
                    invoice_date=invccurrentdate
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
                invoice_number = f"EVENT-INV-{invccurrentdate}-{next_invoice_number}"
                
                # Check if the generated invoice number already exists
                while EventBookGuest.objects.filter(vendor=user,invoice_number=invoice_number).exists():
                    next_invoice_number += 1
                    invoice_number = f"EVENT-INV-{invccurrentdate}-{next_invoice_number}"

                EventBookGuest.objects.filter(vendor=user,id=id).update(invoice_number=invoice_number)
                previous_url = request.META.get('HTTP_REFERER', 'showeventinvoice')
                # Redirect to the previous page
                return redirect(previous_url)
            else:
                previous_url = request.META.get('HTTP_REFERER', 'showeventinvoice')
                # Redirect to the previous page
                return redirect(previous_url)
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)    
    
         
def roomclean(request):
    try:
        if request.user.is_authenticated:
            user = request.user
            today = datetime.now().date()
            lastday = datetime.now().date()
            # lastday += timedelta(days=1)
            lastday -= timedelta(days=1)
            # today += timedelta(days=1)
            RoomCleaning.objects.filter(vendor=user,current_date__lte =lastday ).all().delete()
            # Subquery to get all room IDs that are cleaned by the current vendor today
            cleaned_rooms_subquery = RoomCleaning.objects.filter(
                vendor=user,
                current_date=today,
                status=True,
                rooms=OuterRef('pk')
            ).values('rooms')

            # Query to get all rooms for the current vendor that are not in the RoomCleaning model today
            uncleandroom = Rooms.objects.filter(vendor=user).exclude(
                id__in=Subquery(cleaned_rooms_subquery)
            )

            roomdata = Rooms.objects.filter(vendor=user).order_by('room_name')
            cleanrooms = RoomCleaning.objects.filter(vendor=user, current_date=today, status=True)

            return render(request, 'roomclean.html', {
                'active_page': 'roomclean',
                'rooms': roomdata,
                'cleanrooms': cleanrooms,
                'uncleandroom': uncleandroom
            })
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)    
    
         
def cleanroom(request):
    try:
        if request.user.is_authenticated and request.method=="POST":
            user=request.user
            roomid = request.POST.get('roomno')
            today = datetime.now().date()
            # today += timedelta(days=1)
            if RoomCleaning.objects.filter(vendor=user,rooms_id=roomid,current_date=today,status=True).exists():
                return redirect('roomclean')
            else:
                RoomCleaning.objects.create(vendor=user,rooms_id=roomid,current_date=today,status=True)
                return redirect('roomclean')
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)    
    
         
def mobileview(request,user):
    try:
        user = user
        if HotelProfile.objects.filter(vendor__username=user).exists():
            profile = HotelProfile.objects.get(vendor__username=user)
            rooms = RoomsCategory.objects.filter(vendor__username=user)
            offers = offerwebsitevendor.objects.filter(vendor__username=user)
            service = amainities.objects.filter(vendor__username=user)
            gallary = webgallary.objects.filter(vendor__username=user)
            about  = webreview.objects.filter(vendor__username=user)
            return render(request,'website.html',{'profile':profile,'rooms':rooms,'offers':offers,'service':service,'gallary':gallary,'about':about,})
        else:
            return render(request, '404.html', {'error_message': "Profile Not Created!"}, status=300)  
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)    
    
     
def addcoupnoffers(request):
    try:
        if request.user.is_authenticated and request.method=="POST":
            user=request.user
            codename = request.POST.get('codename')
            amountintext = request.POST.get('amountintext')
            category = request.POST.get('category')
            if offerwebsitevendor.objects.filter(vendor=user,category_id=category).exists():
                offerwebsitevendor.objects.filter(vendor=user,category_id=category).update(code=codename,amount=amountintext)
                messages.success(request,'voucher update succesfully')
                return redirect('websetting')
            else:
                offerwebsitevendor.objects.create(vendor=user,category_id=category,code=codename,amount=amountintext)
                messages.success(request,'voucher added succesfully')
                return redirect('websetting')
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)    
    
         
def addserviceshow(request):
    try:
        if request.user.is_authenticated and request.method=="POST":
            user=request.user
            servicename = request.POST.get('servicename')
            if amainities.objects.filter(vendor=user,service_name=servicename).exists():
                messages.error(request,'service already exists.')
                return redirect('websetting')
            else:
                amainities.objects.create(vendor=user,service_name=servicename)
                messages.success(request,'service added succesfully')
                return redirect('websetting')
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)    
    
             
def gallryimgwebsite(request):
    try:
        if request.user.is_authenticated and request.method=="POST":
            user=request.user
            galaryimg = request.FILES.get('galaryimg')
            webgallary.objects.create(vendor=user,gallary_img=galaryimg)
            messages.success(request,'image added succesfully')
            return redirect('websetting')
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)    
    
         
def reviewscount(request):
    try:
        if request.user.is_authenticated and request.method=="POST":
            user=request.user
            years = request.POST.get('years')
            reviewscount = request.POST.get('reviewscount')
            clientcount = request.POST.get('clientcount')
            if webreview.objects.filter(vendor=user).exists():
                webreview.objects.filter(vendor=user).update(years=years,clientscount=clientcount,reviewscount=reviewscount)
                messages.success(request,'data update succesfully')
                return redirect('websetting')
            else:
                webreview.objects.create(vendor=user,years=years,clientscount=clientcount,reviewscount=reviewscount)
                messages.success(request,'data added succesfully')
                return redirect('websetting')
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)    
    
     
def pos(request):
    try:
        if request.user.is_authenticated:
            user = request.user
            # room = Rooms.objects.filter(vendor=user)
            # for i in room:
            #     Rooms.objects.filter(vendor=user,id=i.id).update(checkin=0)
            tax = Taxes.objects.filter(vendor=user)
            folio = Invoice.objects.filter(vendor=user,foliostatus=False)
            iteams = Items.objects.filter(vendor=user)
            laundry = LaundryServices.objects.filter(vendor=user)
            return render(request,'pospage.html',{'active_page': 'pos','tax':tax,'folio':folio,'iteams':iteams,'laundry':laundry})
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)    
    
         
def Product(request):
    try:
        if request.user.is_authenticated:
            user = request.user
            tax = Taxes.objects.filter(vendor=user)
            folio = Invoice.objects.filter(vendor=user,foliostatus=False)
            iteams = Items.objects.filter(vendor=user)
            laundry = LaundryServices.objects.filter(vendor=user)
            return render(request,'product.html',{'active_page': 'Product','tax':tax,'folio':folio,'iteams':iteams,'laundry':laundry})
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)    
    
         
def deleteproduct(request,id):
    try:
        if request.user.is_authenticated:
            user = request.user
            if Items.objects.filter(vendor=user,id=id).exists():
                Items.objects.filter(vendor=user,id=id).delete()
            else:
                pass
            return redirect('Product')
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)    
    
     
def additems(request):
    try:
        if request.user.is_authenticated and request.method=="POST":
            user=request.user
            description = request.POST.get('description')
            category_tax = request.POST.get('category_tax')
            hsncode = request.POST.get('hsncode')
            price = request.POST.get('price')
            if Items.objects.filter(vendor=user,description=description).exists():
                messages.error(request,'ITEMS already exists.')
                return redirect('Product')
            else:
                Items.objects.create(vendor=user,description=description,category_tax_id=category_tax,hsncode=hsncode,price=price)
                messages.success(request,'ITEMS added succesfully')
                return redirect('Product')
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)    
    
         
def updateitems(request):
    try:
        if request.user.is_authenticated and request.method=="POST":
            user=request.user
            itemid = request.POST.get('itemid')
            description = request.POST.get('description')
            category_tax = request.POST.get('category_tax')
            hsncode = request.POST.get('hsncode')
            price = request.POST.get('price')
            if Items.objects.filter(vendor=user,id=itemid).exists():
                Items.objects.filter(vendor=user,id=itemid).update(description=description,category_tax_id=category_tax,hsncode=hsncode,price=price)
                messages.success(request,'ITEMS Update succesfuly')
                return redirect('Product')
            else:
                messages.success(request,'Wrong Data Enter')
                return redirect('Product')
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)    
    
         
# add items to pos 
def additemstofolio(request):
    try:
        if request.user.is_authenticated and request.method=="POST":
            user=request.user
            foliocustomer = request.POST.get('foliocustomer')
            qty = request.POST.get('qty')
            itemid = request.POST.get('iteamid')
            if Invoice.objects.filter(vendor=user,id=foliocustomer).exists():
                if qty==0:
                    qty = 1
                else:
                    pass
                iteams = Items.objects.get(vendor=user,id=itemid)
                print(iteams)
                taxes = iteams.category_tax
                price = iteams.price
                total = price * int(qty)
                if taxes is not None:
                    taxrate = iteams.category_tax.taxrate
                    taxamt = total * taxrate /100
                    totalamt = taxamt + total
                    hsccode = iteams.hsncode
                    individualtax = taxrate / 2
                    inditaxamt = taxamt/2
                    print(totalamt)
                    InvoiceItem.objects.create(vendor=user,invoice_id=foliocustomer,description=iteams.description,price=iteams.price,
                                        quantity_likedays=qty,cgst_rate=individualtax,sgst_rate=individualtax,
                                        hsncode=hsccode,total_amount=totalamt)
                    invc = Invoice.objects.get(vendor=user,id=foliocustomer)
                    totalamtinvc = invc.total_item_amount + total
                    subtotalinvc = total + invc.subtotal_amount
                    grandtotal = float(invc.grand_total_amount) + totalamt 
                    sgsttotal = float(invc.sgst_amount) + inditaxamt
                    gsttotal = float(invc.gst_amount) + inditaxamt
                    Invoice.objects.filter(vendor=user,id=foliocustomer).update(total_item_amount=totalamtinvc,subtotal_amount=subtotalinvc,grand_total_amount =grandtotal,sgst_amount=sgsttotal,gst_amount=gsttotal)
                    messages.success(request,'Invoice Item added succesfully')
                    return redirect('pos')
                else:
                    InvoiceItem.objects.create(vendor=user,invoice_id=foliocustomer,description=iteams.description,price=iteams.price,
                                        quantity_likedays=qty,total_amount=total,cgst_rate=0.0,sgst_rate=0.0)
                    invc = Invoice.objects.get(vendor=user,id=foliocustomer)
                    totalamtinvc = invc.total_item_amount + total
                    subtotalinvc = total + invc.subtotal_amount
                    grandtotal = invc.grand_total_amount + total
                    Invoice.objects.filter(vendor=user,id=foliocustomer).update(total_item_amount=totalamtinvc,subtotal_amount=subtotalinvc,grand_total_amount =grandtotal)
                    messages.success(request,'Invoice Item added succesfully')
                    return redirect('pos')
            else:
                return redirect('pos')
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)    
    
            
def addlaundryitems(request):
    try:
        if request.user.is_authenticated and request.method=="POST":
            user=request.user
            foliocustomer = request.POST.get('foliocustomer')
            qty = request.POST.get('qty')
            itemid = request.POST.get('iteamid')
            if Invoice.objects.filter(vendor=user,id=foliocustomer).exists():
                if qty==0:
                    qty = 1
                else:
                    pass
                laundry = LaundryServices.objects.get(vendor=user,id=itemid)
                price = laundry.price
                name = laundry.gencategory + " " + laundry.name +" "+ laundry.sercategory
                total = price * int(qty)
                print(name)
                print(total)
                InvoiceItem.objects.create(vendor=user,invoice_id=foliocustomer,description=name,price=price,
                                        quantity_likedays=qty,total_amount=total,cgst_rate=0.0,sgst_rate=0.0)
                invc = Invoice.objects.get(vendor=user,id=foliocustomer)
                totalamtinvc = invc.total_item_amount + total
                subtotalinvc = total + invc.subtotal_amount
                grandtotal = invc.grand_total_amount + total
                Invoice.objects.filter(vendor=user,id=foliocustomer).update(total_item_amount=totalamtinvc,subtotal_amount=subtotalinvc,grand_total_amount =grandtotal)
                messages.success(request,'Invoice Item added succesfully')
                return redirect('pos')
            else:
                return redirect('pos')
            
        else:
            return redirect('loginpage')
    except Exception as e:
        return render(request, '404.html', {'error_message': str(e)}, status=500)    
    
     

