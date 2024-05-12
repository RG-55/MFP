from django.shortcuts import render, redirect, get_object_or_404
from .models import Employee, Payslip
from django.contrib import messages

# ============================ EMPLOYEE STUFF ============================
def employees(request):
    employee_objects = Employee.objects.all()
    return render(request, 'MyInventoryApp/employees.html', {'Employees':employee_objects})


def add_employee(request):
    if request.method == "POST":
        try:
            dname = request.POST.get('name').strip()
            did_number = request.POST.get('id_number').strip() 
            drate = request.POST.get('rate').strip()
            dallowance = request.POST.get('allowance').strip()
        except AttributeError:
            messages.warning(request, 'Error: Missing Input')
            return redirect('add_employee')

        
        # If all have a value (False) [meaning one value is 0] reverse to (True) to slam it into the redirect
        if not all((dname,did_number,drate)):
            messages.warning(request, 'Error: Missing Input')
            return redirect('add_employee')
        
        # Check if the sku already exists (assumption that skus are unique)
        if Employee.objects.filter(id_number=did_number).exists():
            messages.warning(request, 'ID Numbers already exists')
            return redirect('add_employee')
        
        Employee.objects.create(name=dname,id_number=did_number,rate=float(drate),allowance=float(dallowance),overtime_pay = 0)
        messages.success(request, 'Employee created successfully') 
        return redirect('employees')
    else:
        return render(request,'MyInventoryApp/add_employee.html')
    
def update_employee(request, pk):
    empobj = get_object_or_404(Employee,pk=pk)
    if request.method == "POST":
        try:
            dname = request.POST.get('name').strip()
            did_number = request.POST.get('id_number').strip() 
            drate = request.POST.get('rate').strip()
            dallowance = request.POST.get('allowance').strip()
        except AttributeError:
            messages.warning(request, 'Error: Missing Input')
            return redirect('add_employee')
        
        # If all have a value (False) [meaning one value is 0] reverse to (True) to slam it into the redirect
        if not all((dname,did_number,drate)):
            messages.warning(request, 'Error: Missing Input')
            return redirect('update_employee',pk)
        
        # Check if the id already exists (assumption that skus are unique)
        if Employee.objects.filter(id_number=did_number).exists() and  empobj.getID() != did_number:
            messages.warning(request, 'ID Numbers already exists')
            return redirect('update_employee', pk)
        
        Employee.objects.filter(pk=pk).update(name=dname,id_number=did_number,rate=drate,allowance=dallowance)
    
        messages.success(request, 'Employee has been modified') 
        return redirect('employees')
    else:
        return render(request,'MyInventoryApp/update_employee.html', {'empobj': empobj})
    
def delete_employee(request, pk):
    employee_object = get_object_or_404(Employee, pk=pk)
    employee_object.delete()

    messages.success(request, 'Account deleted successfully. You have been logged out.')
    return redirect('employees')

def add_overtime(request, pk):
    if request.method == "POST":
        employee_object = get_object_or_404(Employee, pk=pk)
        dovertime_hours = request.POST.get('overtime_hours')
        dovertime = employee_object.getRate()/160 * 1.5 *int(dovertime_hours)
        dovertime += employee_object.getOvertime()
        Employee.objects.filter(pk=pk).update(overtime_pay=dovertime)
        return redirect('employees')
    else:
        return redirect('payslips')
    

# ============================ PAYSLIP STUFF ============================

def payslips(request):
    #Note, get_object_or_404 creates a copy of the original. To change, call a [.save()] at the variable name

    employee_objects = Employee.objects.all()
    payslip_objects = Payslip.objects.all()

    if request.method == "POST":
        try:
            dname_or_id = request.POST.get('name_or_id').strip()
            dmonth = request.POST.get('month').strip() 
            dyear = request.POST.get('year').strip()
            dpay_cycle = request.POST.get('cycle').strip()
        except AttributeError:
            messages.warning(request, 'Error: Missing Input')
            return redirect('payslips')
        
        # If all have a value (False) [meaning one value is 0] reverse to (True) to slam it into the redirect
        if not all((dname_or_id,dmonth,dyear,dpay_cycle)):
            messages.warning(request, 'Error: Missing Input')
            return redirect('payslips')
        
        # Checks if the input is a name or id
        if not Employee.objects.filter(name=dname_or_id):
            empobj = get_object_or_404(Employee, id_number=dname_or_id)
        else:
            empobj = get_object_or_404(Employee, name=dname_or_id)
        
        print(payslip_objects.filter(id_number=empobj,month=dmonth,year=dyear))
        if not payslip_objects.filter(id_number=empobj,month=dmonth,year=dyear):
            #Pagibig
            if dpay_cycle == "1":
                dtax = ((empobj.getRate()/2) + empobj.getAllowance() + empobj.getOvertime() - 100)*0.2
                dtotal_pay = ((empobj.getRate()/2) + empobj.getAllowance() + empobj.getOvertime() - 100) - dtax
                Payslip.objects.create(id_number=empobj,
                                       month=dmonth,
                                       year=dyear,
                                       pay_cycle=int(dpay_cycle),
                                       rate=empobj.getRate(),
                                       earnings_allowance=empobj.getAllowance(), 
                                       deductions_tax=dtax, 
                                       pag_ibig= 100,
                                       deductions_health = 0,
                                       sss=0, 
                                       overtime=empobj.getOvertime(), 
                                       total_pay=dtotal_pay, date_range=0)
            #Philhealth and SSS
            else: 
                ddeductions_health = (empobj.getRate()*0.04) 
                dsss = (empobj.getRate()*0.045)
                dtax = ((empobj.getRate()/2) + empobj.getAllowance() + empobj.getOvertime() - ddeductions_health - dsss)*0.2
                dtotal_pay = ((empobj.getRate()/2) + empobj.getAllowance() + empobj.getOvertime() - ddeductions_health - dsss) - dtax
                Payslip.objects.create(id_number=empobj,
                                       month=dmonth,
                                       year=dyear,
                                       pay_cycle=dpay_cycle,
                                       rate=empobj.getRate(),
                                       earnings_allowance=empobj.getAllowance(), 
                                       deductions_tax=dtax, 
                                       deductions_health = ddeductions_health,
                                       sss=dsss, 
                                       overtime=empobj.getOvertime(), 
                                       total_pay=dtotal_pay,
                                       pag_ibig=0, date_range=0)
            messages.success(request, 'Payslip created successfully')
            empobj.resetOvertime()
            empobj.save()
            return redirect('payslips')

        else: 
            messages.warning(request, 'ID already has a payslip for specified time period')
            return redirect('payslips')
        
    else:
        return render(request,'MyInventoryApp/payslips.html', {'Employees':employee_objects,'Payslips':payslip_objects})

def view_payslip(request,pk):
    payslipobj=get_object_or_404(Payslip,pk=pk)
    empobj=payslipobj.getID()
    grosspay=empobj.getRate() + payslipobj.getOvertime()+ payslipobj.getEarnings_allowance()
    totaldeductions = payslipobj.getPag_ibig() + payslipobj.getSSS() + payslipobj.getDeductions_health() + payslipobj.getDeductions_tax()
    return render(request,'MyInventoryApp/view_payslip.html', {'empobj':empobj,'payslipobj':payslipobj,'grosspay':grosspay,'totaldeductions':totaldeductions})