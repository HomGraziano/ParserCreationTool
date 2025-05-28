from django import forms

class TuroForm(forms.Form):
    tenant_name = forms.CharField(label="Tenant Name")
    vehicle_field = forms.CharField(label="Vehicle Field ID")
    security_deposit = forms.CharField(label="Security Deposit ID")
    number_of_locations = forms.IntegerField(label="Number of Locations")
    number_of_charges = forms.IntegerField(label="Number of Charges")

class LocationForm(forms.Form):
    address = forms.CharField(label="Address")
    location_id = forms.IntegerField(label="Corresponding ID")

class VehicleClassForm(forms.Form):
    sipp_code = forms.CharField(label="SIPP Code or Class Name")
    class_id = forms.IntegerField(label="Vehicle Class ID")

class ParserForm(forms.Form):
    tenant_name = forms.CharField(label="Tenant Name")
    parsername = forms.CharField(label="OTA")
    payment_reference = forms.CharField(label="Payment Reference")
    security_deposit_id = forms.CharField(label="Security Deposit ID")
    number_of_additional_charges = forms.IntegerField(label="Number of Additional Charges")
    number_of_vehicle_classes = forms.IntegerField(label="Number of Vehicle Classes")
    number_of_locations = forms.IntegerField(label="Number of Locations")