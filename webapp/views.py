from django.shortcuts import render, redirect
from .forms import TuroForm, LocationForm, ParserForm, VehicleClassForm
from .functions import chargesloop
from django.forms import formset_factory
import json
from django.http import HttpResponse

#Turo Parser ----------------------------------------------------------------------------------

def turo_parser(request):
    LocationFormSet = formset_factory(LocationForm, extra=0)

    # STEP 1: Handle main form
    if request.method == 'POST' and 'step' not in request.POST:
        form = TuroForm(request.POST)
        if form.is_valid():
            request.session['main_form'] = form.cleaned_data
            num_locations = form.cleaned_data['number_of_locations']
            LocationFormSet = formset_factory(LocationForm, extra=num_locations)
            formset = LocationFormSet()
            return render(request, 'webapp/location_entry.html', {
                'formset': formset
            })
        else:
            return render(request, 'webapp/parser.html', {'form': form})

    # STEP 2: Handle location formset
    elif request.method == 'POST' and request.POST.get('step') == 'location':
        main_data = request.session.get('main_form')
        if not main_data:
            return redirect('turo_parser')

        num_locations = main_data['number_of_locations']
        LocationFormSet = formset_factory(LocationForm, extra=num_locations)
        formset = LocationFormSet(request.POST)

        if formset.is_valid():
            locations = {}
            for loc_form in formset:
                cleaned = loc_form.cleaned_data
                address = cleaned.get('address', '').strip()
                loc_id = cleaned.get('location_id')
                if address and loc_id is not None:
                    locations[address] = loc_id

            tenant = main_data['tenant_name']
            vehicle_field = main_data['vehicle_field']
            deposit = main_data['security_deposit']
            num_charges = main_data['number_of_charges']

            charges = chargesloop(num_charges)
            adjustment_charge = num_charges + 1
            parsername = "Turo"

            result = {
                "rules_a": {
                    "prepaid": {
                        "total_paid": "full",
                        "payment_type": "Pre-Paid Turo"
                    }
                },
                "brand_id": 1,
                "locations": locations,
                "forced_fees": {
                    "abb_tax": 0,
                    "location_fee": 0,
                    "government_tax": "0",
                    "forced_security_deposit_id": deposit
                },
                "payment_type": "Pre-Paid Turo",
                "vehicle_field_id": vehicle_field,
                "enable_auto_return": True,
                "forced_date_format": "d/m/y g:i a",
                "enable_auto_pick_up": True,
                "mandatory_additional_charges": charges,
                "additional_charge_for_adjustments": str(adjustment_charge),
                "refund_pre_payments_on_cancellations": True
            }

            request.session['last_json'] = result
            request.session['last_tenant'] = tenant
            request.session['last_platform'] = parsername
            return render(request, 'webapp/data_result.html', {
                'data': json.dumps(result, indent=2),
                'tenant': tenant
            })
        else:
            return render(request, 'webapp/location_entry.html', {'formset': formset})

    else:
        form = TuroForm()
        return render(request, 'webapp/parser.html', {'form': form})

    

#Generic Parser ----------------------------------------------------------------------------------

def parserg(request):
    LocationFormSet = formset_factory(LocationForm, extra=0)
    VehicleClassFormSet = formset_factory(VehicleClassForm, extra=0)

    # STEP 1: Handle main form
    if request.method == 'POST' and request.POST.get('step') is None:
        form = ParserForm(request.POST)
        if form.is_valid():
            request.session['parser_form'] = form.cleaned_data
            num_locations = form.cleaned_data['number_of_locations']
            LocationFormSet = formset_factory(LocationForm, extra=num_locations)
            formset = LocationFormSet()
            return render(request, 'webapp/location_entry.html', {
                'formset': formset,
                'step': 'location'
            })

    # STEP 2: Handle location formset
    elif request.method == 'POST' and request.POST.get('step') == 'location':
        main_data = request.session.get('parser_form')
        if not main_data:
            return redirect('parserg')

        num_locations = main_data['number_of_locations']
        LocationFormSet = formset_factory(LocationForm, extra=num_locations)
        formset = LocationFormSet(request.POST)

        if formset.is_valid():
            locations = {}
            for form in formset:
                cleaned = form.cleaned_data
                address = cleaned.get('address', '').strip()
                loc_id = cleaned.get('location_id')
                if address and loc_id is not None:
                    locations[address.lower()] = loc_id

            request.session['locations'] = locations

            num_vehicle_classes = main_data['number_of_vehicle_classes']
            VehicleClassFormSet = formset_factory(VehicleClassForm, extra=num_vehicle_classes)
            vehicle_formset = VehicleClassFormSet()
            return render(request, 'webapp/vehicle_entry.html', {
                'formset': vehicle_formset,
                'step': 'vehicles'
            })

    # STEP 3: Handle vehicle formset
    elif request.method == 'POST' and request.POST.get('step') == 'vehicles':
        main_data = request.session.get('parser_form')
        locations = request.session.get('locations')
        if not main_data or not locations:
            return redirect('parserg')

        num_vehicle_classes = main_data['number_of_vehicle_classes']
        VehicleClassFormSet = formset_factory(VehicleClassForm, extra=num_vehicle_classes)
        formset = VehicleClassFormSet(request.POST)

        if formset.is_valid():
            vehicle_classes = {}
            for form in formset:
                cleaned = form.cleaned_data
                sipp = cleaned.get('sipp_code')
                class_id = cleaned.get('class_id')
                if sipp and class_id is not None:
                    vehicle_classes[sipp] = class_id

            payment_reference = main_data['payment_reference']
            deposit = main_data['security_deposit_id']
            num_charges = main_data['number_of_additional_charges']

            charges = [
                {"id": str(i + 1), "amount": 0, "quantity": "1", "only_if_added": True}
                for i in range(num_charges)
            ]
            adjustment_charge = str(num_charges + 1)
            tenant = main_data['tenant_name']

            result = {
                "rules_a": {
                    "prepaid": {
                        "total_paid": "full",
                        "payment_type": payment_reference
                    }
                },
                "brand_id": 1,
                "locations": locations,
                "forced_fees": {
                    "forced_security_deposit_id": deposit,
                    "location_fee": 0,
                    "abb_tax": 0,
                    "government_tax": "0"
                },
                "mandatory_additional_charges": charges,
                "vehicle_classes": vehicle_classes,
                "additional_charge_for_adjustments": adjustment_charge,
                "refund_pre_payments_on_cancellations": True,
                "payment_type": payment_reference
            }

            request.session['last_json'] = result
            request.session['last_tenant'] = tenant
            request.session['last_platform'] = main_data['parsername']
            return render(request, 'webapp/data_result.html', {
                'data': json.dumps(result, indent=2),
                'tenant': tenant
            })

    else:
        form = ParserForm()
        return render(request, 'webapp/parser.html', {'form': form})

#Download JSON ----------------------------------------------------------------------------------

def download_json(request):
    result = request.session.get('last_json')
    tenant = request.session.get('last_tenant', 'output')
    platform = request.session.get('last_platform', 'parser')

    if not result:
        return redirect('home')

    # Generate filename: tenantname_parsername.json
    filename = f"{tenant.strip().lower().replace(' ', '_')}_{platform.strip().lower().replace(' ', '_')}.json"

    json_data = json.dumps(result, indent=2)
    response = HttpResponse(json_data, content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


#Home ----------------------------------------------------------------------------------

def home(request):
    return render(request, 'webapp/home.html')

def about(request):
    return render(request, 'webapp/about.html')

def surprice(request):
    return render(request, 'webapp/surprice.html')

def vehicleparser(request):
    return render(request, 'webapp/vehicleparser.html')


