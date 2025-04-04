from typing_extensions import Concatenate
from django import template
from django.db.models.query import QuerySet
from django.http import HttpResponse, Http404, HttpResponseRedirect, FileResponse
from django.template import loader
from wwdb.filters import CastFilter
from .models import *
from django.views.generic import *
from django.urls import reverse_lazy
from django.urls import reverse
from bootstrap_datepicker_plus import *
from .forms import *
from django.shortcuts import render, get_object_or_404, redirect
import pandas as pd
from django.db.models import Count, Q
import pyodbc 
from django.db.models import Avg, Count, Min, Sum, Max
import logging
from .filters import *
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
import io
from datetime import datetime, timedelta
from django.contrib.auth import logout
import json
import subprocess


logger = logging.getLogger(__name__)

def get_data_from_external_db(start_date, end_date, winch):
    print("Fetching data from external DB...")  # Added context to the print statement

    try:
        conn = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='b1uz00!!2SQ',
            database='winch_data'
        )

        query = f"""
            SELECT date_time, tension_load_cell, payout
            FROM {winch}
            WHERE date_time BETWEEN '{start_date}' AND '{end_date}'
        """

        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()

        cursor.close()
        conn.close()  # Close connection properly

        if len(rows) > 1000:
            print("Data rows fetched:", rows)
            binned_data = {}
            for row in rows:
                dt = row[0]
                if dt not in binned_data:
                    binned_data[dt] = {'max_tension': row[1], 'max_payout': row[2]}
                else:
                    binned_data[dt]['max_tension'] = max(binned_data[dt]['max_tension'], row[1])
                    binned_data[dt]['max_payout'] = max(binned_data[dt]['max_payout'], row[2])
            return sorted(binned_data.items())
        else:
            print("Data rows fetched (less than 1000):", rows)
            return [(row[0], {'max_tension': row[1], 'max_payout': row[2]}) for row in rows]
    
    except Exception as e:
        print(f"Error fetching data: {e}")  # Print error for debugging
        return []

def charts(request):
    # Default values for filtering
    start_date = request.GET.get('start_date')
    print(start_date)
    end_date = request.GET.get('end_date')
    print(end_date)
    winch_id = request.GET.get('winch')
    print(winch_id)

    # Initialize empty data lists
    data_tension = []
    data_payout = []

    # Validate and parse the dates and winch
    if start_date and end_date and winch_id:
        print('attempting to parse:', start_date, end_date, winch_id)
        try:
            # Convert the string dates to date objects
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date() + timedelta(days=1)
            winch = Winch.objects.get(id=winch_id)  # Fetch the winch object
        except (ValueError, Winch.DoesNotExist):
            # Handle parsing errors or winch not found
            start_date = end_date = None
            winch = None
    else:
        # Set default values if parameters are missing
        end_date = datetime.utcnow().date() + timedelta(days=1)
        start_date = end_date - timedelta(days=1)
        winch = Winch.objects.last()  # Default to the last winch if none provided

    # Fetch data using the retrieved parameters
    data_points = get_data_from_external_db(start_date, end_date, winch)

    # Process the data points
    if data_points:
        for dt, values in data_points:
            data_tension.append({'date': dt.strftime('%Y-%m-%d %H:%M:%S'), 'value': values['max_tension']})
            data_payout.append({'date': dt.strftime('%Y-%m-%d %H:%M:%S'), 'value': values['max_payout']})

    # Serialize the data to JSON
    data_json_tension = json.dumps(data_tension)
    data_json_payout = json.dumps(data_payout)

    # Create an instance of the form with the initial values for rendering
    form = DataFilterForm(initial={
        'start_date': start_date,
        'end_date': end_date - timedelta(days=1) if end_date else None,
        'winch': winch,
    })

    return render(request, 'wwdb/reports/charts.html', {
        'form': form,
        'data_json_tension': data_json_tension,
        'data_json_payout': data_json_payout
    })


def custom_logout(request):
    logout(request)  # Logs out the user
    return redirect('home')  # Redirects to the homepage

def home(request):
    template = loader.get_template('wwdb/home.html')
    context = {
        'template_name': 'home.html'
        }
    return HttpResponse(template.render(context, request))

"""
CASTS
Classes related to create, update, delete, view Cast model
"""

def caststart(request):
    context ={}
    form = StartCastForm(request.POST or None)
    if request.method == "POST":
        form = StartCastForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            cast=Cast.objects.last()
            cast.refresh_from_db()
            cast.get_active_wire()
            if cast.startdate == None:
                cast.startcast_get_datetime()
            cast.save()
            return HttpResponseRedirect("%i/castend" % cast.pk)
    else:
        form = StartCastForm 
        if 'submitted' in request.GET:
            submitted = True
            return render(request, 'wwdb/casts/caststart.html', {'form':form, 'submitted':submitted, 'id':id})

    template_name = 'caststart.html'

    context = {
        'form':form,
        'template_name':template_name}

    return render(request, "wwdb/casts/caststart.html", context)

def caststartend(request):
    form = StartEndCastForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            cast = form.save()
            cast.refresh_from_db()
            cast.get_active_wire()
            cast.endcastcal()
            cast.get_active_length()
            cast.get_active_safeworkingtension()
            cast.get_active_factorofsafety()
            cast.save()
            cast.refresh_from_db()
            cast.get_cast_duration()
            cast.save()
            return HttpResponseRedirect('/wwdb/reports/castreport')  # This should redirect to the cast report
        else:
            print(form.errors)

    # No need to redefine form if it's already defined
    submitted = 'submitted' in request.GET

    context = {
        'form': form,
        'submitted': submitted,
    }

    return render(request, "wwdb/casts/caststartend.html", context)

def castlist(request):
    cast_complete = Cast.objects.filter(maxpayout__isnull=False, maxtension__isnull=False) 
    cast_flag = Cast.objects.filter((Q(flagforreview=True) | Q(maxpayout__isnull=True) | Q(maxtension__isnull=True)))
    
    castfilter = CastFilter(request.GET, queryset=cast_complete)
    cast_complete= castfilter.qs

    context = {
        'cast_complete': cast_complete,
        'cast_flag': cast_flag,
       }

    return render(request, 'wwdb/reports/castlist.html', context=context)

def cast_end(request):
    last = Cast.objects.latest('pk')
    return redirect('castend', id=last.pk)
	
def castend(request, id):
    context ={}
    obj = Cast.objects.get(id=id)
    form = EndCastForm(request.POST or None, instance = obj)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            if obj.enddate == None:
                obj.endcast_get_datetime()
            obj.save()
            obj.refresh_from_db()
            obj.get_active_wire()
            obj.endcastcal()
            obj.get_cast_duration()
            obj.get_active_length()
            obj.get_active_safeworkingtension()
            obj.get_active_factorofsafety()
            obj.save()

            return HttpResponseRedirect("/wwdb/casts/%i/castenddetail" % obj.pk)
    context["form"] = form

    template_name = 'castend.html'

    context = {
        'form':form,
        'template_name':template_name}

    return render(request, "wwdb/casts/castend.html", context)

def castedit(request, id):
    context ={}
    obj = Cast.objects.get(id=id)
    if request.method == 'POST':
        form = EditCastForm(request.POST, instance = obj)
        if form.is_valid():
            form.save()
            obj.get_active_wire()
            obj.endcastcal()
            obj.get_cast_duration()
            obj.save()
            return HttpResponseRedirect('/wwdb/reports/castreport')
    else:
        form = EditCastForm(instance = obj)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/wwdb/casts/%i/edit' % cast.pk)

    context["form"] = form
    return render(request, "wwdb/casts/castedit.html", context)

def castmanualenter(request):
    context ={}
    form = ManualCastForm(request.POST or None)
    if request.method == "POST":
        form = ManualCastForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            cast=Cast.objects.last()
            return HttpResponseRedirect("/wwdb/casts/%i/castenddetail" % cast.pk)
    else:
        form = ManualCastForm
        if 'submitted' in request.GET:
            submitted = True
            return render(request, 'wwdb/casts/castmanualenter.html', {'form':form, 'submitted':submitted, 'id':id})

    context['form']= form

    return render(request, "wwdb/casts/castmanualenter.html", context)

def castmanualedit(request, id):
    context ={}
    obj = Cast.objects.get(id=id)
    if request.method == 'POST':
        form = ManualCastForm(request.POST, instance = obj)
        if form.is_valid():
            form.save()
            obj.save()
            return HttpResponseRedirect('/wwdb/reports/castreport')
    else:
        form = ManualCastForm(instance = obj)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/wwdb/casts/%i/manualedit' % cast.pk)

    context["form"] = form
    return render(request, "wwdb/casts/castmanualedit.html", context)


def castdetail(request, id):
    context ={}
    context["cast"] = Cast.objects.get(id = id)     
    return render(request, "wwdb/casts/castdetail.html", context)

class CastDelete(DeleteView):
    model = Cast
    template_name="wwdb/casts/castdelete.html"
    success_url= reverse_lazy('castreport')

def castenddetail(request, id):
    context ={}
    context["cast"] = Cast.objects.get(id = id)
    return render(request, "wwdb/casts/castenddetail.html", context)

"""
PRECRUISE CONFIGURATION
Classes related to starting a cruise including updating WinchOperators and DeploymentType models
"""

def cruiseconfigurehome(request):
    operators = WinchOperator.objects.all()
    deployments = DeploymentType.objects.all()
    active_wire = Wire.objects.filter(status=True)
    winches = Winch.objects.all()
    cruises = Cruise.objects.all()

    context = {
        'operators': operators,
        'deployments': deployments,
        'active_wire': active_wire,
        'winches': winches,
        'cruises' : cruises,
       }

    return render(request, 'wwdb/configuration/cruiseconfiguration.html', context=context)

def wireeditfactorofsafety(request, id):
    context ={}
    obj = get_object_or_404(Wire, id = id)

    if request.method == 'POST':
        form = EditFactorofSafetyForm(request.POST, instance = obj)
        if form.is_valid():
            form.save()
            wireid=Wire.objects.get(id=id)
            return HttpResponseRedirect("/wwdb/configuration/cruiseconfiguration")
    else:
        form = EditFactorofSafetyForm(instance = obj)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/wwdb/inventories/wire/%i/editfactorofsafety" % wireid.pk)

    context["form"] = form
    return render(request, "wwdb/inventories/wireeditfactorofsafety.html", context)


"""
WINCH WIRE REPORTING
Classes related to winch and wire reporting 
"""

def wirereport(request, pk):
    wire=Wire.objects.filter(id=pk)
    wire_object=wire.last()
    cutback_retermination=CutbackRetermination.objects.filter(wire=pk)
    break_test=Breaktest.objects.filter(wire=pk)
    lubrication=Lubrication.objects.filter(wire=pk)

    context ={
        'wire':wire,
        'wire_object':wire_object,
        'cutback_retermination':cutback_retermination,
        'break_test':break_test,
        'lubrication':lubrication,
        }

    return render(request, "wwdb/reports/wirereport.html", context)

def cruiselist(request):
    cruises = Cruise.objects.order_by('-startdate')

    context = {
        'cruises': cruises,
       }

    return render(request, 'wwdb/reports/cruiselist.html', context=context)

def castreport(request):
    # Initialize form with data from GET request (if any)
    form = CastFilterForm(request.GET)
    casts = Cast.objects.all()
    cast_complete = Cast.objects.filter(flagforreview=False, maxpayout__isnull=False, maxtension__isnull=False) 
    cast_flag = Cast.objects.filter((Q(flagforreview=True) | Q(maxpayout__isnull=True) | Q(maxtension__isnull=True)))

    # Handle form submission and filtering
    if form.is_valid():
        casts = Cast.objects.all()
        deploymenttype = form.cleaned_data.get('deploymenttype')
        winch = form.cleaned_data.get('winch')
        startdate = form.cleaned_data.get('startdate')
        enddate = form.cleaned_data.get('enddate')
        wire = form.cleaned_data.get('wire')
        operator = form.cleaned_data.get('operator')
        if deploymenttype:
            casts = casts.filter(deploymenttype=deploymenttype)
        if winch:
            casts = casts.filter(winch=winch)
        if startdate:    
            casts = casts.filter(startdate__gte=startdate)
        if enddate:
            casts = casts.filter(enddate__lte=enddate)
        if wire:
            casts = casts.filter(wire=wire)
        if operator:
            casts = casts.filter(Q(startoperator=operator) | Q(endoperator=operator))

    context = {
        'cast_complete': cast_complete,
        'cast_flag': cast_flag,
        'casts': casts,
        'form': form,
       }
    # Render the template with form and filtered products
    return render(request, 'wwdb/reports/castreport.html', context)

"""
def is_valid_queryparam(param):
    return param != '' and param is not None


def cast_table_filter(request):
    
    qs = Cast.objects.all()
    wire = request.GET.get('wire_nsfid')
    winch = request.GET.get('winch_id')
    deployment = request.GET.get('deployment_id')
    date_min = request.GET.get('date_min')
    date_max = request.GET.get('date_max')

    if is_valid_queryparam(date_min):
        qs=qs.filter(startdate__gte=date_min)

    if is_valid_queryparam(date_max):
        qs=qs.filter(enddate__lt=date_max)

    if is_valid_queryparam(wire):
        if wire!='Wire':
            wire_obj=Wire.objects.filter(nsfid=wire).last()
            qs=qs.filter(wire=wire_obj)

    if is_valid_queryparam(winch):
        if winch!='Winch':
            winch_obj=Winch.objects.filter(name=winch).last()
            qs=qs.filter(winch=winch_obj)

    if is_valid_queryparam(deployment):
        if deployment!='Deployment':
            deployment_obj=DeploymentType.objects.filter(name=deployment).last()
            qs=qs.filter(deploymenttype=deployment_obj)

    return qs

def castreport(request):
    wire=Wire.objects.all()
    winch=Winch.objects.all()
    deployment=DeploymentType.objects.all()
    qs = cast_table_filter(request)



    context = {
        'qs':qs,
        'wire':wire,
        'winch':winch,
        'deployment':deployment,
        }

    return render(request, "wwdb/reports/castreport.html", context)
"""

def cast_table_csv(request):
    cast = cast_table_filter(request)

    response = HttpResponse(content_type="text/plain")
    response['Content-Disposition']='attachement; filename=cast_table.csv'
    
    lines = []

    date_min=cast.order_by('startdate').first()
    date_max=cast.order_by('enddate').last()

    lines.append('\n#Start date:' + str(date_min))
    lines.append('\n#End Date:' + str(date_max))
    lines.append('\n#\n#')
    lines.append('\n#\nstarttime, endtime, winch, wire, deploymenttype, startoperator, endoperator, maxtension, maxpayout, payoutmaxtension, metermaxtension, timemaxtension, wetendtag, dryendtag, notes')

    for c in cast:
            lines.append('\n' + str(c.startdate) + ',' 
            +  str(c.enddate) + ',' 
            +  str(c.active_winch) + ',' 
            +  str(c.wire) + ','
            +  str(c.deploymenttype) + ',' 
            +  str(c.startoperator) + ',' 
            +  str(c.endoperator) + ',' 
            +  str(c.maxtension) + ',' 
            +  str(c.maxpayout) + ',' 
            +  str(c.payoutmaxtension) + ',' 
            +  str(c.metermaxtension) + ',' 
            +  str(c.timemaxtension) + ','
            +  str(c.wetendtag) + ',' 
            +  str(c.dryendtag) + ',' 
            +  str(c.notes) + ',' )


    response.writelines(lines)


    return response




def cruisereport(request, pk):
    
    #cruise object and casts by cruise daterange
    cruise=Cruise.objects.filter(id=pk)
    cruise_object=cruise.last()
    startdate=cruise_object.startdate
    enddate=cruise_object.enddate
    cast = Cast.objects.filter(startdate__range=[startdate, enddate])

    #create dictionary of active winch keys and cast object list values
    cast_by_winch = {}
    for c in cast:
        if c.active_winch not in cast_by_winch:
            cast_by_winch[c.active_winch] = []

        cast_by_winch[c.active_winch].append(c)
        
    #create dictionary of active winch keys and integer value of casts completed values
    cast_by_winch_count = {}
    for c in cast_by_winch:
        cast_by_winch_count[c]=len(cast_by_winch[c])

    #create dictionary of active winch keys and maxtension list values of casts completed
    tension_by_winch = {}
    for c in cast:
        if c.active_winch not in tension_by_winch:
            tension_by_winch[c.active_winch] = []
        tension_by_winch[c.active_winch].append(c.maxtension)

    # filter none values from key value lists
    for t in tension_by_winch:
        tension_by_winch[t]=list(filter(lambda item: item is not None,tension_by_winch[t]))

    #Create dictionary of active winch keys and max tension per winch values
    maxtension_by_winch={}
    for t in tension_by_winch:
        if tension_by_winch[t]:
            maxtension_by_winch[t]=max(tension_by_winch[t])
        else:
            maxtension_by_winch[t]='None'

    #create dictionary of active winch keys and max payout list values of casts completed
    payout_by_winch = {}
    for c in cast:
        if c.active_winch not in payout_by_winch:
            payout_by_winch[c.active_winch] = []
        payout_by_winch[c.active_winch].append(c.maxpayout)

    #Create dictionary of active winch keys and max payout per winch values
    for t in payout_by_winch:
        payout_by_winch[t]=list(filter(lambda item: item is not None,payout_by_winch[t]))

    #Create dictionary of active winch keys and max payout per winch values
    maxpayout_by_winch={}
    for t in payout_by_winch:
        if payout_by_winch[t]:
            maxpayout_by_winch[t]=max(payout_by_winch[t])
        else:
            maxpayout_by_winch[t]='None'

    context = {
        "cruise": cruise,
        "cast": cast,
        "cast_by_winch_count": cast_by_winch_count,
        "maxtension_by_winch":maxtension_by_winch,
        "maxpayout_by_winch":maxpayout_by_winch,
    }

    return render(request, "wwdb/reports/cruisereport.html", context)

def cruise_report_file(request, pk):

    #cruise object and casts by cruise daterange
    cruise=Cruise.objects.filter(id=pk)
    cruise_object=cruise.last()
    startdate=cruise_object.startdate
    enddate=cruise_object.enddate
    cast = Cast.objects.filter(startdate__range=[startdate, enddate])
    cruisenumber=cruise_object.number

    response = HttpResponse(content_type="text/plain")
    response['Content-Disposition']='attachement; filename=cruise_report_' + str(cruisenumber) + '.txt'

    #cruise object and casts by cruise daterange
    cruise=Cruise.objects.filter(id=pk)
    cruise_object=cruise.last()
    startdate=cruise_object.startdate
    enddate=cruise_object.enddate
    cast = Cast.objects.filter(startdate__range=[startdate, enddate])

    #create dictionary of active winch keys and cast object list values
    cast_by_winch = {}
    for c in cast:
        if c.active_winch not in cast_by_winch:
            cast_by_winch[c.active_winch] = []

        cast_by_winch[c.active_winch].append(c)
        
    #create dictionary of active winch keys and integer value of casts completed values
    cast_by_winch_count = {}
    for c in cast_by_winch:
        cast_by_winch_count[c]=len(cast_by_winch[c])

    #create dictionary of active winch keys and maxtension list values of casts completed
    tension_by_winch = {}
    for c in cast:
        if c.active_winch not in tension_by_winch:
            tension_by_winch[c.active_winch] = []
        tension_by_winch[c.active_winch].append(c.maxtension)

    # filter none values from key value lists
    for t in tension_by_winch:
        tension_by_winch[t]=list(filter(lambda item: item is not None,tension_by_winch[t]))

    #Create dictionary of active winch keys and max tension per winch values
    maxtension_by_winch={}
    for t in tension_by_winch:
        if tension_by_winch[t]:
            maxtension_by_winch[t]=max(tension_by_winch[t])
        else:
            maxtension_by_winch[t]='None'

    #create dictionary of active winch keys and max payout list values of casts completed
    payout_by_winch = {}
    for c in cast:
        if c.active_winch not in payout_by_winch:
            payout_by_winch[c.active_winch] = []
        payout_by_winch[c.active_winch].append(c.maxpayout)

    #Create dictionary of active winch keys and max payout per winch values
    for t in payout_by_winch:
        payout_by_winch[t]=list(filter(lambda item: item is not None,payout_by_winch[t]))

    #Create dictionary of active winch keys and max payout per winch values
    maxpayout_by_winch={}
    for t in payout_by_winch:
        if payout_by_winch[t]:
            maxpayout_by_winch[t]=max(payout_by_winch[t])
        else:
            maxpayout_by_winch[t]='None'

    #append data to list, write to file
    lines = []
    lines.append('#' + cruise_object.number)

    lines.append('\n#Start date:' + str(startdate))
    lines.append('\n#End Date:' + str(enddate))

    lines.append('\n#\n#')

    for t in maxtension_by_winch:
        lines.append('\n#' + str(t) + ' Max tension: ' + str(maxtension_by_winch[t]))

    lines.append('\n#\n#')

    for t in maxpayout_by_winch:
        lines.append('\n#' + str(t) + ' Max payout: ' + str(maxpayout_by_winch[t]))

    lines.append('\n#\nstarttime, endtime, winch, deploymenttype, startoperator, endoperator, maxtension, maxpayout, payoutmaxtension, metermaxtension, timemaxtension, wetendtag, dryendtag, notes')

    for c in cast:
            lines.append('\n' + str(c.startdate) + ',' 
            +  str(c.enddate) + ',' 
            +  str(c.active_winch) + ',' 
            +  str(c.deploymenttype) + ',' 
            +  str(c.startoperator) + ',' 
            +  str(c.endoperator) + ',' 
            +  str(c.maxtension) + ',' 
            +  str(c.maxpayout) + ',' 
            +  str(c.payoutmaxtension) + ',' 
            +  str(c.metermaxtension) + ',' 
            +  str(c.timemaxtension) + ','
            +  str(c.wetendtag) + ',' 
            +  str(c.dryendtag) + ',' 
            +  str(c.notes) + ',' )


    response.writelines(lines)

    return response

def castplot(request, pk):

    obj = get_object_or_404(Cast, id=pk)

    conn = pyodbc.connect('Driver={SQL Server};'
                            'Server=192.168.1.90, 1433;'
                            'Database=WinchDb;'
                            'Trusted_Connection=no;'
			        'UID=remoteadmin;'
			        'PWD=eris.2003;')

    winch=(obj.winch.name)
    startcal=str(obj.startdate)
    endcal=str(obj.enddate)

    df=pd.read_sql_query("SELECT * FROM " + winch + " WHERE DateTime BETWEEN '" + startcal + "' AND '" + endcal + "'", conn)

    df_tension_datetime=df.loc[:,['DateTime','Tension','Payout']]
    df_json=df_tension_datetime.to_json(orient='records')

    return render(request, 'wwdb/reports/castplot.html', {'df_json': df_json})


"""
Postings
"""

def safeworkingtensions(request):
    wires = Wire.objects.all()
    # Filter in Python based on the active_winch property
    wires_with_active_winch = [wire for wire in wires if wire.active_winch is not None]
    
    context = {
        'wires': wires_with_active_winch
    }
    
    return render(request, 'wwdb/reports/safeworkingtensions.html', context)

def safeworkingtensions_file(request):

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer)

    #Set canvas as landscape A4
    c.setPageSize(landscape(A4))

    #Draw title
    c.setFont("Helvetica", 36, leading=None)
    c.drawString(1*inch,7*inch,"Safe Working Tensions")

    #Create formatted datetime object 
    now=datetime.now()
    date_time=now.strftime('%m/%d/%Y')
    date_time_filename=now.strftime('%Y%m%d')

    #draw date posted on canvas
    c.setFont("Helvetica", 12, leading=None)
    c.drawString(1*inch,1*inch,"date posted: " + date_time)

    #create empty lines list object
    lines = []
    
    #wire objects where status=True, ordered by winch name in ascending order
    active_wire = [wire for wire in wires if wire.active_winch is not None]
    
    #Define stylesheet for headers
    stylesheet=getSampleStyleSheet()
    HeaderStyle=ParagraphStyle('yourtitle',
                           fontName="Helvetica-Bold",
                           fontSize=16,
                           parent=stylesheet['Heading2'],
                           alignment=TA_LEFT,
                           spaceAfter=14)


    #Define header objects
    header1=Paragraph('Winch',HeaderStyle)
    header2=Paragraph('Wire ID',HeaderStyle)
    header3=Paragraph('Length',HeaderStyle)
    header4=Paragraph('Factor of Safety',HeaderStyle)
    header5=Paragraph('Safe Working Tension',HeaderStyle)

    #append headers to lines list
    lines.append((header1,header2,header3,header4,header5))
    
    #append wire data to lines list
    for wire in active_wire:
        lines.append((wire.active_winch.name, 
                      wire.nsfid, 
                      wire.active_length, 
                      wire.factorofsafety, 
                      wire.safe_working_tension))
    
    #Define table settings and styles, add lines list to table
    table = Table(lines,
                  colWidths=[150,175,80,120,120],
                  rowHeights=[100,100,100,100])

    table.setStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ('LINEABOVE', (0, 1), (-1, -1), 0.10, colors.grey),
                    ('FONTSIZE',(0,0),(-1,-1),24)])
    
    width, height = A4
    table.wrapOn(c, width, height)

    #Draw table on canvas
    table.drawOn(c, 1 * inch, 1.5 * inch)

    c.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='safe_working_tension_%s.pdf' %date_time_filename)

"""
Maintenance
"""

def wirelocationlist(request):
    wirelocations = WireLocation.objects.all()
    
    context = {
        'wirelocations': wirelocations,
        }

    return render(request, 'wwdb/inventories/wirelocationlist.html', context=context)

def wirelocationadd(request):
    context ={}
    form = WireLocationForm(request.POST or None)
    if request.method == "POST":
        form = WireLocationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/wwdb/inventories/wirelocationlist')
    else:
        form = WireLocationForm 
        if 'submitted' in request.GET:
            submitted = True
            return render(request, 'wwdb/inventories/wirelocationadd.html', {'form':form, 'submitted':submitted, 'id':id})
 
    context['form']= form

    return render(request, "wwdb/inventories/wirelocationadd.html", context)

def wirelocationedit(request, id):
    context ={}
    obj = WireLocation.objects.get(id=id)
    if request.method == 'POST':
        form = WireLocationForm(request.POST, instance = obj)
        if form.is_valid():
            form.save()
            obj.save()
            return HttpResponseRedirect('/wwdb/inventories/wirelocationlist')
    else:
        form = WireLocationForm(instance = obj)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/wwdb/inventories/%i/wirelocationedit' % obj.pk)

    context["form"] = form
    return render(request, "wwdb/inventories/wirelocationedit.html", context)

def wirelocationdelete(request, id):
    wirelocation = WireLocation.objects.get(pk=id)
    wirelocation.delete()
    return HttpResponse()

def locationlist(request):
    locations = Location.objects.all()
    
    context = {
        'locations': locations,
        }

    return render(request, 'wwdb/inventories/locationlist.html', context=context)

def locationadd(request):
    context ={}
    form = LocationForm(request.POST or None)
    if request.method == "POST":
        form = LocationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/wwdb/inventories/locationlist')
    else:
        form = LocationForm 
        if 'submitted' in request.GET:
            submitted = True
            return render(request, 'wwdb/inventories/locationadd.html', {'form':form, 'submitted':submitted, 'id':id})
 
    context['form']= form

    return render(request, "wwdb/inventories/locationadd.html", context)

def locationedit(request, id):
    context ={}
    obj = Location.objects.get(id=id)
    if request.method == 'POST':
        form = LocationForm(request.POST, instance = obj)
        if form.is_valid():
            form.save()
            obj.save()
            return HttpResponseRedirect('/wwdb/inventories/locationlist')
    else:
        form = LocationForm(instance = obj)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/wwdb/inventories/%i/locationedit' % obj.pk)

    context["form"] = form
    return render(request, "wwdb/inventories/locationedit.html", context)

def locationdelete(request, id):
    location = Location.objects.get(pk=id)
    location.delete()
    return HttpResponse()

def wirelist(request):
    wires_in_use = Wire.objects.filter(status=True)
    wires_in_storage = Wire.objects.filter(status=False)
    wires = Wire.objects.all()
    
    context = {
        'wires_in_use': wires_in_use,
        'wires_in_storage': wires_in_storage, 
        'wires' : wires,
        }

    return render(request, 'wwdb/inventories/wirelist.html', context=context)

def wireropedatalist(request):
    wireropes = WireRopeData.objects.all()
    
    context = {
        'wireropes': wireropes,
        }

    return render(request, 'wwdb/inventories/wireropedatalist.html', context=context)

def wireropedataedit(request, id):
    context ={}
    obj = get_object_or_404(WireRopeData, id = id)

    if request.method == 'POST':
        form = WireRopeDataEditForm(request.POST, instance = obj)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/wwdb/inventories/wireropedatalist")
    else:
        form = WireRopeDataEditForm(instance = obj)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/wwdb/inventories/wireropedata/%i/edit" % obj.pk)

    context["form"] = form
    return render(request, "wwdb/inventories/wireropedataedit.html", context)

def wireropedataadd(request):
    context ={}
    form = WireRopeDataAddForm(request.POST or None)
    if request.method == "POST":
        form = WireRopeDataAddForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/wwdb/inventories/wireropedatalist')
    else:
        form = WireRopeDataAddForm 
        if 'submitted' in request.GET:
            submitted = True
            return render(request, 'wwdb/inventories/wireropedataadd.html', {'form':form, 'submitted':submitted, 'id':id})
 
    context['form']= form

    return render(request, "wwdb/inventories/wireropedataadd.html", context)

def wireropedatadelete(request, id):
    wireropedata = WireRopeData.objects.get(pk=id)
    wireropedata.delete()
    return HttpResponse()

"""
WIRES
Classes related to create, update, view Wire model
"""

class WireDetail(DetailView):
    model = Wire
    template_name="wwdb/inventories/wiredetail.html"

class WireEdit(UpdateView):
    model = Wire
    template_name="wwdb/inventories/wireedit.html"
    fields=['wirerope','manufacturerid','nsfid','dateacquired','notes','status','factorofsafety']
    
    def get_form(self):
        form = super().get_form()
        form.fields['dateacquired'].widget = DateTimePickerInput()
        return form

def wireedit(request, id):
    context ={}
    obj = Wire.objects.get(id=id)
    if request.method == 'POST':
        form = WireEditForm(request.POST, instance = obj)
        if form.is_valid():
            form.save()
            obj.save()
            return HttpResponseRedirect('/wwdb/inventories/wirelist')
    else:
        form = WireEditForm(instance = obj)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/wwdb/inventories/%i/wireedit' % obj.pk)

    context["form"] = form
    return render(request, "wwdb/inventories/wireedit.html", context)

def wireadd(request):
    context ={}
    form = WireAddForm(request.POST or None)
    if request.method == "POST":
        form = WireAddForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/wwdb/inventories/wirelist')
    else:
        form = WireAddForm 
        if 'submitted' in request.GET:
            submitted = True
            return render(request, 'wwdb/inventories/wireadd.html', {'form':form, 'submitted':submitted, 'id':id})
 
    context['form']= form

    return render(request, "wwdb/inventories/wireadd.html", context)

def wiredelete(request, id):
    wire = Wire.objects.get(pk=id)
    wire.delete()
    return HttpResponse()

"""
WINCHES
Classes related to create, update, view Winch model
"""
def swttablelistget(request):
    context = {}
    wires = Wire.objects.all()
    # Filter in Python based on the active_winch property
    wires_with_active_winch = [wire for wire in wires if wire.active_winch is not None]
    
    context = {
        'wires': wires_with_active_winch
    }
    
    return render(request, 'wwdb/configuration/swttablelist.html', context)

def swttableadd(request):
    context = {'form': SWTTableForm()}
    return render(request, 'wwdb/configuration/swttableadd.html', context)

def swttableaddsubmit(request):
    context = {}
    form = SWTTableForm(request.POST)
    context['form'] = form
    if form.is_valid():
        context['wire'] = form.save()
    else:
        return render(request, 'wwdb/configuration/swttableadd.html', context)
    return render(request, 'wwdb/configuration/swttablerow.html', context)

def swttableaddcancel(request):
    return HttpResponse()

def swttabledelete(request, wire_pk):
    wire = Wire.objects.get(pk=wire_pk)
    wire.delete()
    return HttpResponse()

def swttableedit(request, wire_pk):
    wire = Wire.objects.get(pk=wire_pk)
    context = {}
    context['wire'] = wire
    context['form'] = SWTTableForm(initial={
        'factorofsafety': wire.factorofsafety,
    })

    return render(request, 'wwdb/configuration/swttableedit.html', context)

def swttableeditsubmit(request, wire_pk):
    wire = Wire.objects.get(pk=wire_pk)
    context = {}
    context['wire'] = wire
    if request.method == 'POST':
        form = SWTTableForm(request.POST, instance=wire)
        if form.is_valid():
            form.save()
        else:
            return render(request, 'wwdb/configuration/swttableedit.html', context)
    return render(request, 'wwdb/configuration/swttablerow.html', context)

def winchtablelistget(request):
    context = {}
    context['winch'] = Winch.objects.all()
    return render(request, 'wwdb/configuration/winchtablelist.html', context)

def winchtableadd(request):
    context = {'form': WinchTableForm()}
    return render(request, 'wwdb/configuration/winchtableadd.html', context)

def winchtableaddsubmit(request):
    context = {}
    form = WinchTableForm(request.POST)
    context['form'] = form
    if form.is_valid():
        context['winch'] = form.save()
    else:
        return render(request, 'wwdb/configuration/winchtableadd.html', context)
    return render(request, 'wwdb/configuration/winchtablerow.html', context)

def winchtableaddcancel(request):
    return HttpResponse()

def winchtabledelete(request, winch_pk):
    winch = Winch.objects.get(pk=winch_pk)
    winch.delete()
    return HttpResponse()

def winchtableedit(request, winch_pk):
    winch = Winch.objects.get(pk=winch_pk)
    context = {}
    context['winch'] = winch
    context['form'] = WinchTableForm(initial={
        'name':winch.name,
        'status': winch.status,
        'ship':winch.ship,
        'institution':winch.institution,
    })
    return render(request, 'wwdb/configuration/winchtableedit.html', context)

def winchtableeditsubmit(request, winch_pk):
    context = {}
    winch= Winch.objects.get(pk=winch_pk)
    context['winch'] = winch
    if request.method == 'POST':
        form = WinchTableForm(request.POST, instance=winch)
        if form.is_valid():
            form.save()
        else:
            return render(request, 'wwdb/configuration/winchtablerow.html', context)
    return render(request, 'wwdb/configuration/winchtablerow.html', context)

class WinchList(ListView):
    model = Winch
    template_name="wwdb/inventories/winchlist.html"

class WinchDetail(DetailView):
    model = Winch
    template_name="wwdb/inventories/winchdetail.html"

class WinchEdit(UpdateView):
    model = Winch
    template_name="wwdb/inventories/winchedit.html"
    fields=['locationid','ship','institution','manufacturer']

def wincheditstatus(request, id):
    context ={}
    obj = get_object_or_404(Winch, id = id)

    if request.method == 'POST':
        form = EditWinchStatusForm(request.POST, instance = obj)
        if form.is_valid():
            form.save()
            winchid=Winch.objects.get(id=id)
            return HttpResponseRedirect("/wwdb/configuration/cruiseconfiguration")
    else:
        form = EditWinchStatusForm(instance = obj)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/wwdb/inventories/winch/%i/editstatus" % winchid.pk)

    context["form"] = form
    return render(request, "wwdb/inventories/wincheditstatus.html", context)

def winchadd(request):
    context ={}
    form = WinchAddForm(request.POST or None)
    if request.method == "POST":
        form = WinchAddForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/wwdb/configuration/cruiseconfiguration')
    else:
        form = WinchAddForm 
        if 'submitted' in request.GET:
            submitted = True
            return render(request, 'wwdb/inventories/winchadd.html', {'form':form, 'submitted':submitted, 'id':id})
 
    context['form']= form

    return render(request, "wwdb/inventories/winchadd.html", context)

"""
WINCH OPERATORS
Classes related to create, update, view WinchOperators model
"""

def operatortablelistget(request):
    context = {}
    context['winchoperator'] = WinchOperator.objects.all()
    return render(request, 'wwdb/configuration/operatortablelist.html', context)

def operatortableadd(request):
    context = {'form': WinchOperatorTableForm()}
    return render(request, 'wwdb/configuration/operatortableadd.html', context)

def operatortableaddsubmit(request):
    context = {}
    form = WinchOperatorTableForm(request.POST)
    context['form'] = form
    if form.is_valid():
        context['winchoperator'] = form.save()
    else:
        return render(request, 'wwdb/configuration/operatortableadd.html', context)
    return render(request, 'wwdb/configuration/operatortablerow.html', context)

def operatortableaddcancel(request):
    return HttpResponse()

def operatortabledelete(request, winchoperator_pk):
    winchoperator = WinchOperator.objects.get(pk=winchoperator_pk)
    winchoperator.delete()
    return HttpResponse()

def operatortableedit(request, winchoperator_pk):
    winchoperator = WinchOperator.objects.get(pk=winchoperator_pk)
    context = {}
    context['winchoperator'] = winchoperator
    context['form'] = WinchOperatorTableForm(initial={
        'firstname':winchoperator.firstname,
        'lastname': winchoperator.lastname,
        'status': winchoperator.status,
        'username': winchoperator.username,
    })
    return render(request, 'wwdb/configuration/operatortableedit.html', context)

def operatortableeditsubmit(request, winchoperator_pk):
    context = {}
    winchoperator = WinchOperator.objects.get(pk=winchoperator_pk)
    context['winchoperator'] = winchoperator
    if request.method == 'POST':
        form = WinchOperatorTableForm(request.POST, instance=winchoperator)
        if form.is_valid():
            form.save()
        else:
            return render(request, 'wwdb/configuration/operatortableedit.html', context)
    return render(request, 'wwdb/configuration/operatortablerow.html', context)


class OperatorList(ListView):
    model = WinchOperator
    template_name="wwdb/configuration/operatorlist.html"

class OperatorDetail(DetailView):
    model = WinchOperator
    template_name="wwdb/configuration/operatordetail.html"

class OperatorEdit(UpdateView):
    model = WinchOperator
    template_name="wwdb/configuration/operatoredit.html"
    fields=['username','firstname','lastname','status']


def operatoreditstatus(request, id):
    context ={}
    obj = get_object_or_404(WinchOperator, id = id)

    if request.method == 'POST':
        form = EditOperatorStatusForm(request.POST, instance = obj)
        if form.is_valid():
            form.save()
            operatorid=WinchOperator.objects.get(id=id)
            return HttpResponseRedirect("/wwdb/configuration/cruiseconfiguration")
    else:
        form = EditOperatorStatusForm(instance = obj)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/wwdb/configuration/operator/%i/editstatus" % operatorid.pk)

    context["form"] = form
    return render(request, "wwdb/configuration/operatoreditstatus.html", context)

class OperatorAdd(CreateView):
    model = WinchOperator
    template_name="wwdb/configuration/operatoradd.html"
    fields=['username','firstname','lastname','status']

def operatoradd(request):
    context ={}
    form = AddOperatorForm(request.POST or None)
    if request.method == "POST":
        form = AddOperatorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/wwdb/configuration/cruiseconfiguration")
    else:
        form = AddOperatorForm 
        if 'submitted' in request.GET:
            submitted = True
            return render(request, 'wwdb/configuration/operatoradd.html', {'form':form, 'submitted':submitted, 'id':id})

    context['form']= form

    return render(request, 'wwdb/configuration/deploymentadd.html', context)

"""
DEPLOYMENTS 
Classes related to create, update, view DeploymentType model
"""
def deploymenttablelistget(request):
    context = {}
    context['deployment'] = DeploymentType.objects.all()
    return render(request, 'wwdb/configuration/deploymenttablelist.html', context)

def deploymenttableadd(request):
    context = {'form': DeploymentTableForm()}
    return render(request, 'wwdb/configuration/deploymenttableadd.html', context)

def deploymenttableaddsubmit(request):
    context = {}
    form = DeploymentTableForm(request.POST)
    context['form'] = form
    if form.is_valid():
        context['deployment'] = form.save()
    else:
        return render(request, 'wwdb/configuration/deploymenttableadd.html', context)
    return render(request, 'wwdb/configuration/deploymenttablerow.html', context)

def deploymenttableaddcancel(request):
    return HttpResponse()

def deploymenttabledelete(request, deployment_pk):
    deployment = DeploymentType.objects.get(pk=deployment_pk)
    deployment.delete()
    return HttpResponse()

def deploymenttableedit(request, deployment_pk):
    deployment = DeploymentType.objects.get(pk=deployment_pk)
    context = {}
    context['deployment'] = deployment
    context['form'] = DeploymentTableForm(initial={
        'status':deployment.status,
        'name': deployment.name,
        'equipment': deployment.equipment,
        'notes': deployment.notes,
    })
    return render(request, 'wwdb/configuration/deploymenttableedit.html', context)

def deploymenttableeditsubmit(request, deployment_pk):
    context = {}
    deployment = DeploymentType.objects.get(pk=deployment_pk)
    context['deployment'] = deployment
    if request.method == 'POST':
        form = DeploymentTableForm(request.POST, instance=deployment)
        if form.is_valid():
            form.save()
        else:
            return render(request, 'wwdb/configuration/deploymenttableedit.html', context)
    return render(request, 'wwdb/configuration/deploymenttablerow.html', context)

class DeploymentList(ListView):
    model = DeploymentType
    template_name="wwdb/configuration/deploymentlist.html"

class DeploymentDetail(DetailView):
    model = DeploymentType
    template_name="wwdb/configuration/deploymentdetail.html"

class DeploymentEdit(UpdateView):
    model = DeploymentType
    template_name="wwdb/configuration/deploymentedit.html"
    fields=['name','equipment','notes','status']


def deploymenteditstatus(request, id):
    context ={}
    obj = get_object_or_404(DeploymentType, id = id)

    if request.method == 'POST':
        form = EditDeploymentStatusForm(request.POST, instance = obj)
        if form.is_valid():
            form.save()
            deploymentid=DeploymentType.objects.get(id=id)
            return HttpResponseRedirect("/wwdb/configuration/cruiseconfiguration")
    else:
        form = EditDeploymentStatusForm(instance = obj)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/wwdb/configuration/deployment/%i/editstatus" % deploymenttypeid.pk)

    context["form"] = form
    return render(request, "wwdb/configuration/deploymenteditstatus.html", context)

def deploymentadd(request):
    context ={}
    form = AddDeploymentForm(request.POST or None)
    if request.method == "POST":
        form = AddDeploymentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/wwdb/configuration/cruiseconfiguration")
    else:
        form = AddDeploymentForm 
        if 'submitted' in request.GET:
            submitted = True
            return render(request, 'wwdb/configuration/deploymentadd.html', {'form':form, 'submitted':submitted, 'id':id})

    context['form']= form

    return render(request, 'wwdb/configuration/deploymentadd.html', context)

"""
BREAKTESTS 
Classes related to create, update, view Breaktest model
"""

class BreaktestDelete(DeleteView):
    model = Breaktest
    template_name="wwdb/maintenance/breaktestdelete.html"
    success_url= reverse_lazy('breaktestlist')

def breaktestlist(request):
    break_test = Breaktest.objects.order_by('-date')

    context = {
        'break_test': break_test, 
        }

    return render(request, 'wwdb/maintenance/breaktestlist.html', context=context)

def breaktestadd(request):
    context ={}
    form = BreaktestAddForm(request.POST or None)
    if request.method == "POST":
        form = BreaktestAddForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/wwdb/maintenance/breaktestlist')
    else:
        form = BreaktestAddForm
        if 'submitted' in request.GET:
            submitted = True
            return render(request, 'wwdb/maintenance/breaktestadd.html', {'form':form, 'submitted':submitted, 'id':id})
 
    context['form']= form

    return render(request, "wwdb/maintenance/breaktestadd.html", context)

def breaktestdetail(request, id):
    context ={}
    context["breaktest"] = Breaktest.objects.get(id = id)     
    return render(request, "wwdb/maintenance/breaktestdetail.html", context)

def breaktestedit(request, id):
    context ={}
    obj = get_object_or_404(Breaktest, id = id)

    if request.method == 'POST':
        form = BreaktestEditForm(request.POST, instance = obj)
        if form.is_valid():
            form.save()
            breaktestid=Breaktest.objects.get(id=id)
            return HttpResponseRedirect("/wwdb/maintenance/breaktestlist")
    else:
        form = BreaktestEditForm(instance = obj)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/wwdb/maintenance/breaktest/%i/edit" % breaktestid.pk)

    context["form"] = form
    return render(request, "wwdb/maintenance/breaktestedit.html", context)


"""
LUBRICATION
Classes related to create, update, view Lubrication model
"""

def lubricationlist(request):
    lubrication = Lubrication.objects.order_by('-date')

    context = {
        'lubrication': lubrication, 
        }

    return render(request, 'wwdb/maintenance/lubricationlist.html', context=context)

def lubricationadd(request):
    context ={}
    form = LubricationAddForm(request.POST or None)
    if request.method == "POST":
        form = LubricationAddForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/wwdb/maintenance/lubricationlist')
    else:
        form = LubricationAddForm
        if 'submitted' in request.GET:
            submitted = True
            return render(request, 'wwdb/maintenance/lubricationadd.html', {'form':form, 'submitted':submitted, 'id':id})
 
    context['form']= form

    return render(request, "wwdb/maintenance/lubricationadd.html", context)

def lubricationdetail(request, id):
    context ={}
    context["lubrication"] = Lubrication.objects.get(id = id)     
    return render(request, "wwdb/maintenance/lubricationdetail.html", context)

def lubricationedit(request, id):
    context ={}
    obj = get_object_or_404(Lubrication, id = id)

    if request.method == 'POST':
        form = LubricationEditForm(request.POST, instance = obj)
        if form.is_valid():
            form.save()
            lubricationid=Lubrication.objects.get(id=id)
            return HttpResponseRedirect("/wwdb/maintenance/lubricationlist")
    else:
        form = LubricationEditForm(instance = obj)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/wwdb/maintenance/lubrication/%i/edit" % lubricationid.pk)

    context["form"] = form
    return render(request, "wwdb/maintenance/lubricationedit.html", context)

class LubricationDelete(DeleteView):
    model = Lubrication
    template_name="wwdb/maintenance/lubricationdelete.html"
    success_url= reverse_lazy('lubricationlist')

"""
CUTBACKRETERMINATION
Classes related to create, update, view CutbackRetermination model
"""

def cutbackreterminationlist(request):
    cutbacks_reterminations = CutbackRetermination.objects.order_by('-date')

    context = {
        'cutbacks_reterminations': cutbacks_reterminations, 
        }

    return render(request, 'wwdb/maintenance/cutbackreterminationlist.html', context=context)


def cutbackreterminationedit(request, id):
    context ={}
    obj = get_object_or_404(CutbackRetermination, id = id)

    if request.method == 'POST':
        form = EditCutbackReterminationForm(request.POST, instance = obj)
        if form.is_valid():
            form.save()
            obj.edit_length()
            obj.save()
            return HttpResponseRedirect('/wwdb/maintenance/cutbackreterminationlist')
    else:
        form = EditCutbackReterminationForm(instance = obj)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/wwdb/maintenance/cutbackretermination/%i/edit" % cutbackreterminationid.pk)

    context["form"] = form
    return render(request, "wwdb/maintenance/cutbackreterminationedit.html", context)


class CutbackReterminationDetail(DetailView):
    model = CutbackRetermination
    template_name="wwdb/maintenance/cutbackreterminationdetail.html"

class CutbackReterminationAdd(CreateView):
    model = CutbackRetermination
    template_name="wwdb/maintenance/cutbackreterminationadd.html"
    fields=['dryendtag','wetendtag', 'lengthremoved','wireid','date','notes']

def cutbackreterminationadd(request):
    context ={}
    form = AddCutbackReterminationForm(request.POST or None)
    if request.method == "POST":
        form = AddCutbackReterminationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            obj=CutbackRetermination.objects.last()
            obj.submit_dry_end_tag()
            obj.submit_length()
            obj.save()
            return HttpResponseRedirect("/wwdb/maintenance/cutbackreterminationlist")
    else:
        form = AddCutbackReterminationForm 
        if 'submitted' in request.GET:
            submitted = True
            return render(request, 'wwdb/maintenance/cutbackreterminationadd.html', {'form':form, 'submitted':submitted, 'id':id})

    context['form']= form

    return render(request, 'wwdb/maintenance/cutbackreterminationadd.html', context)


class CutbackreterminationDelete(DeleteView):
    model = CutbackRetermination
    template_name="wwdb/maintenance/cutbackreterminationdelete.html"
    success_url= reverse_lazy('cutbackreterminationlist')

"""
Cruises
Classes related to create, update, view Cruise model
"""

def cruisetablelistget(request):
    context = {}
    context['cruise'] = Cruise.objects.all()
    return render(request, 'wwdb/configuration/cruisetablelist.html', context)

def cruisetableadd(request):
    context = {'form': CruiseTableForm()}
    return render(request, 'wwdb/configuration/cruisetableadd.html', context)

def cruisetableaddsubmit(request):
    context = {}
    form = CruiseTableForm(request.POST)
    context['form'] = form
    if form.is_valid():
        context['cruise'] = form.save()
    else:
        return render(request, 'wwdb/configuration/cruisetableadd.html', context)
    return render(request, 'wwdb/configuration/cruisetablerow.html', context)

def cruisetableaddcancel(request):
    return HttpResponse()

def cruisetabledelete(request, cruise_pk):
    cruise = Cruise.objects.get(pk=cruise_pk)
    cruise.delete()
    return HttpResponse()

def cruisetableedit(request, cruise_pk):
    cruise = Cruise.objects.get(pk=cruise_pk)
    context = {}
    context['cruise'] = cruise
    context['form'] = CruiseTableForm(initial={
        'number':cruise.number,
        'startdate': cruise.startdate,
        'enddate': cruise.enddate,
    })
    return render(request, 'wwdb/configuration/cruisetableedit.html', context)

def cruisetableeditsubmit(request, cruise_pk):
    context = {}
    cruise = Cruise.objects.get(pk=cruise_pk)
    context['cruise'] = cruise
    if request.method == 'POST':
        form = CruiseTableForm(request.POST, instance=cruise)
        if form.is_valid():
            form.save()
        else:
            return render(request, 'wwdb/configuration/cruisetablerow.html', context)
    return render(request, 'wwdb/configuration/cruisetablerow.html', context)

def cruiseedit(request, id):
    obj = get_object_or_404(Cruise, id=id)

    if request.method == 'POST':
        form = EditCruiseForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('/wwdb/configuration/cruiseconfiguration')  
    else:
        form = EditCruiseForm(instance=obj)

    context = {
        "form": form
    }
    return render(request, "wwdb/configuration/cruiseedit.html", context)

def cruiseadd(request):
    context ={}
    form = CruiseAddForm(request.POST or None)
    if request.method == "POST":
        form = CruiseAddForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("/wwdb/configuration/cruiseconfiguration")
    else:
        form = CruiseAddForm 
        if 'submitted' in request.GET:
            submitted = True
            return render(request, 'wwdb/configuration/cruiseadd.html', {'form':form, 'submitted':submitted, 'id':id})

    context['form']= form

    return render(request, 'wwdb/configuration/cruiseadd.html', context)

class CruiseDelete(DeleteView):
    model = Cruise
    template_name="wwdb/cruiseconfiguration/cruisedelete.html"
    success_url= reverse_lazy('cruiseconfigurehome')

#For Lunix systems

def check_service_status(service_name):
    try:
        # Check the status of the service using systemctl
        result = subprocess.run(['systemctl', 'is-active', service_name], capture_output=True, text=True)
        return result.stdout.strip() == "active"
    except Exception:
        return False

def get_service_logs(service_name):
    try:
        # Get the last 50 lines of logs for the given service
        result = subprocess.run(
            ['journalctl', '-u', service_name, '--no-pager', '-n', '50'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError:
        return "Error fetching logs."

def servicestatus(request):
    services = ['mysql', 'nginx', 'gunicorn', 'listen_write.service']  # Add your service names here
    service_data = []

    for service_name in services:
        is_active = check_service_status(service_name)
        service_logs = get_service_logs(service_name)
        service_data.append({
            'name': service_name,
            'is_active': is_active,
            'logs': service_logs,
        })

    context = {
        'service_data': service_data,
    }
    return render(request, 'wwdb/reports/servicestatus.html', context)
"""
import win32serviceutil

def check_service_status(service_name):
    try:
        # Get the status of the service
        status = win32serviceutil.QueryServiceStatus(service_name)[1]
        # Service status codes: 1 = SERVICE_STOPPED, 2 = SERVICE_START_PENDING, 3 = SERVICE_STOP_PENDING, 4 = SERVICE_RUNNING
        return status == 4  # Check if the service is running
    except Exception as e:
        return False

def servicestatus(request):
    service_name = 'MySQL80'  # Change this to your service name
    is_active = check_service_status(service_name)
    context = {
        'service_name': service_name,
        'is_active': is_active,
    }
    return render(request, 'wwdb/reports/servicestatus.html', context)
"""