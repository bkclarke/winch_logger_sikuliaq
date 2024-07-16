from django import forms
from django.forms import ModelForm
from .models import *
from bootstrap_datepicker_plus.widgets import DatePickerInput, DateTimePickerInput
from django.forms.widgets import HiddenInput
from datetime import datetime


class StartCastForm(ModelForm):
    flagforreview = forms.BooleanField(required=False)

    class Meta:
        model = Cast
        fields = [
            'startoperator',
            'startdate',
            'deploymenttype',
            'winch',
            'notes',
            'flagforreview',
        ]

        widgets = {            
            "notes": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "style": "max-width: 100%; align: center;",
                    "placeholder": "Notes",
                }
            ),
            'startdate': DateTimePickerInput()
            }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        active_operators = WinchOperator.objects.filter(status=True)
        active_winches = Winch.objects.filter(status=True)
        active_deployments = DeploymentType.objects.filter(status=True)
        self.fields['startoperator'].queryset  = active_operators
        self.fields['winch'].queryset  = active_winches
        self.fields['deploymenttype'].queryset  = active_deployments


class ManualCastForm(ModelForm):

    class Meta:
        model = Cast
        fields = [
            'startoperator',
            'endoperator',
            'startdate',
            'enddate',
            'deploymenttype',
            'winch',
            'wire',
            'notes',
            'maxtension',
            'maxpayout',
        ]

        widgets = {
            "notes": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "style": "max-width: 100%; align: center;",
                    "placeholder": "Notes",
                }
            ),
            'startdate': DateTimePickerInput(), 
            'enddate': DateTimePickerInput()
            }

class EndCastForm(ModelForm):
    flagforreview = forms.BooleanField(required=False)
    wirerinse = forms.BooleanField(required=False)
  
    class Meta:
        model = Cast
  
        fields = [
            'endoperator',
            'startdate',
            'enddate',
            'notes',
            'wirerinse',
            'flagforreview',
        ]

        widgets = {
            "notes": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "style": "max-width: 100%; align: center;",
                    "placeholder": "Notes",
                }
            ),
            'startdate': DateTimePickerInput(), 
            'enddate': DateTimePickerInput(),
            'startdate': forms.HiddenInput(),
            }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        active_operators = WinchOperator.objects.filter(status=True)
        self.fields['endoperator'].queryset  = active_operators

        
    def is_valid(self):
        valid = super().is_valid()

        if hasattr(self, 'cleaned_data') and valid:

            start_date = self.cleaned_data.get('startdate')
            end_date = self.cleaned_data.get('enddate')
            if not end_date:
                self.add_error('enddate', 'Please enter end date')
                valid = False
            elif end_date < start_date:
                self.add_error('enddate', 'End date must be greater than start date')
                valid = False
        return valid     


class EditCastForm(ModelForm):
    flagforreview = forms.BooleanField(required=False)
  
    class Meta:
        model = Cast
  
        fields = [
            'startoperator',
            'endoperator',
            'startdate',
            'enddate',
            'deploymenttype',
            'winch',
            'notes',
            'flagforreview',
        ]

        widgets = {
            "notes": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "style": "max-width: 100%; align: center;",
                    "placeholder": "Notes",
                }
            ),
            'startdate': DateTimePickerInput(), 
            'enddate': DateTimePickerInput()
            }

        def is_valid(self):
            valid = super().is_valid()

            if hasattr(self, 'cleaned_data') and valid:

                start_date = self.cleaned_data.get('startdate')
                end_date = self.cleaned_data.get('enddate')
                if not end_date:
                    self.add_error('enddate', 'Please enter end date')
                    valid = False
                elif end_date < start_date:
                    self.add_error('enddate', 'End date must be greater than start date')
                    valid = False
            return valid  

class EditFactorofSafetyForm(ModelForm):
  
    class Meta:
        model = Wire
  
        fields = [
            'factorofsafety',
        ]

class EditWinchStatusForm(ModelForm):
  
    class Meta:
        model = Winch
  
        fields = [
            'status',
        ]
        
class EditOperatorStatusForm(ModelForm):
  
    class Meta:
        model = WinchOperator
  
        fields = [
            'firstname',
            'lastname',
            'username',
            'status',
        ]

class EditDeploymentStatusForm(ModelForm):
  
    class Meta:
        model = DeploymentType
  
        fields = [
            'status',
        ]

class AddDeploymentForm(ModelForm):

    class Meta:
        model = DeploymentType
        fields = [
            'name',
            'equipment',
            'notes',
            'status',
        ]

class EditCruiseForm(ModelForm):
  
    class Meta:
        model = Cruise
  
        fields = [
            'number',
            'startdate',
            'enddate',
        ]
 
        widgets = {'startdate': DatePickerInput(
                    options={
                    "format": "YYYY-MM-DD"}
                    ),
                   'enddate': DatePickerInput(
                    options={
                    "format": "YYYY-MM-DD"}
                    )}

class AddCutbackReterminationForm(ModelForm):

    class Meta:
        model = CutbackRetermination
        fields = [
            'date',
            'wire',
            'wetendtag',
            'notes',
        ]

        widgets = {
            "notes": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "style": "max-width: 100%; align: center;",
                    "placeholder": "Notes",
                }
            ),
            'date': DatePickerInput(
                    options={
                    "format": "YYYY-MM-DD"}
        )}

class EditCutbackReterminationForm(ModelForm):
  
    class Meta:
        model = CutbackRetermination
  
        fields = [
            'date',
            'wire',
            'notes',
        ]

        widgets = {
            "notes": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "style": "max-width: 100%; align: center;",
                    "placeholder": "Notes",
                }
            ),
            'date': DatePickerInput(
                    options={
                    "format": "YYYY-MM-DD"})
            }


class CruiseAddForm(ModelForm):

    class Meta:
        model = Cruise
        fields = [
            'number',
            'startdate',
            'enddate',
        ]

        widgets = {'startdate': DatePickerInput(
                    options={
                    "format": "YYYY-MM-DD"}
                    ),
					'enddate': DatePickerInput(
                    options={
                    "format": "YYYY-MM-DD"}
                    )}

class AddOperatorForm(ModelForm):

    class Meta:
        model = WinchOperator
        fields = [
            'firstname',
            'lastname',
            'username',
            'status',
        ]

class CruiseReportForm(forms.Form):
    start_date = forms.DateField()
    end_date = forms.DateField()

    widgets = {'start_date': DateTimePickerInput(), 
            'end_date': DateTimePickerInput(),}
    
    def clean_start_date(self):
        start = self.cleaned_data['start_date']
        end = self.cleaned_data['end_date']

        if end < start:
            raise ValidationError(_('end date must be after start date'))

        return data
		
class WinchAddForm(ModelForm):

    class Meta:
        model = Winch
        fields = [
            'name',
            'institution',
            'status',
        ]

class BreaktestAddForm(ModelForm):

    class Meta:
        model = Breaktest
        fields = [
            'wire',
            'date',
            'testedbreakingload',
            'notes',
        ] 

        widgets = {
            "notes": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "style": "max-width: 100%; align: center;",
                    "placeholder": "Notes",
                }
            ),
            'date': DatePickerInput(
            options={
            "format": "YYYY-MM-DD"}
            )}

class BreaktestEditForm(ModelForm):

    class Meta:
        model = Breaktest
        fields = [
            'wire',
            'date',
            'testedbreakingload',
            'notes',
        ] 

        widgets = {
            "notes": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "style": "max-width: 100%; align: center;",
                    "placeholder": "Notes",
                }
            ),
            'date': DatePickerInput(
            options={
            "format": "YYYY-MM-DD"}
            )}

class LubricationAddForm(ModelForm):

    class Meta:
        model = Lubrication
        fields = [
            'date',
            'wire',
            'lubetype',
            'lubelength',
            'notes',
        ] 

        widgets = {
            "lubetype": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "style": "max-width: 100%; align: center;",
                    "placeholder": "Lube type",
                }
            ),
            "notes": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "style": "max-width: 100%; align: center;",
                    "placeholder": "Notes",
                }
            ),
            'date': DatePickerInput(
            options={
            "format": "YYYY-MM-DD"}
            )}

class LubricationEditForm(ModelForm):

    class Meta:
        model = Lubrication
        fields = [
            'date',
            'wire',
            'lubetype',
            'lubelength',
            'notes',
        ] 

        widgets = {
            "lubetype": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "style": "max-width: 100%; align: center;",
                    "placeholder": "Lube type",
                }
            ),
            "notes": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "style": "max-width: 100%; align: center;",
                    "placeholder": "Notes",
                }
            ),
            'date': DatePickerInput(
            options={
            "format": "YYYY-MM-DD"}
            )}

class UnolsWireReportForm(ModelForm):

    class Meta:
        model = Cast
        fields = [
            'startdate',
            'enddate',
        ]

        widgets = {'startdate': DateTimePickerInput(), 
                   'enddate': DateTimePickerInput()}

class WinchOperatorTableForm(forms.ModelForm):
    status = forms.BooleanField(required=False)

    class Meta:
        model = WinchOperator
        exclude = []

        widgets = {
            "firstname": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "style": "max-width: 450px; align: center;",
                    "placeholder": "Title",
                }
            ),
            "lastname": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "style": "max-width: 450px; align: center;",
                    "placeholder": "Title",
                }
            ),
            "username": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "style": "max-width: 450px; align: center;",
                    "placeholder": "Title",
                }
            ),
        }

class CruiseTableForm(forms.ModelForm):
    class Meta:
        model = Cruise
        exclude = []

        widgets = {
            "number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "style": "max-width: 450px; align: center;",
                    "placeholder": "cruise number",
                }),
        }

class DeploymentTableForm(forms.ModelForm):
    status = forms.BooleanField(required=False)

    class Meta:
        model = DeploymentType
        exclude = []

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "style": "max-width: 450px; align: center;",
                    "placeholder": "name",
                }),
            "equipment": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "style": "max-width: 450px; align: center;",
                    "placeholder": "equipment details",
                }),
            "notes": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "style": "max-width: 450px; align: center;",
                    "placeholder": "notes",
                }),
        }

class WinchTableForm(forms.ModelForm):
    status = forms.BooleanField(required=False)

    class Meta:
        model = Winch
        exclude = []

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "style": "max-width: 450px; align: center;",
                    "placeholder": "name",
                }),
        }

class SWTTableForm(forms.ModelForm):
    class Meta:
        model = Wire
        exclude = []

class WireEditForm(ModelForm):

    class Meta:
        model = Wire
        fields = [
            'nsfid',
            'wirerope',
            'dateacquired',
            'notes',
            'status',
            'ownershipstatus',
            'factorofsafety',
            'dryendtag',

        ]

        widgets = {
            'dateacquired': DatePickerInput(
                    options={
                    "format": "YYYY-MM-DD"}
                    ),
            "nsfid": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "style": "max-width: ;100% align: center;",
                    "placeholder": "name",
                }),
            "manufacturerid": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "style": "max-width: 100%; align: center;",
                    "placeholder": "name",
                }),
            "notes": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "style": "max-width: 100%; align: center;",
                    "placeholder": "name",
                }),
        }

class WireAddForm(ModelForm):

    class Meta:
        model = Wire
        fields = [
            'nsfid',
            'wirerope',
            'dateacquired',
            'status',
            'ownershipstatus',
            'factorofsafety',
            'dryendtag',
            'notes',
        ]

        widgets = {
            'dateacquired': DatePickerInput(
                    options={
                    "format": "YYYY-MM-DD"}
                    ),
            "nsfid": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "style": "max-width: ;100% align: center;",
                    "placeholder": "nsf id",
                }),
            "notes": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "style": "max-width: 100%; align: center;",
                    "placeholder": "notes",
                }),
        }

class WireRopeDataEditForm(ModelForm):

    class Meta:
        model = WireRopeData
        fields = [
            'name',
            'manufacturer',
            'manufacturerpartnumber',
            'cabletype',
            'nominalbreakingload',
            'weightperfoot',

        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "style": "max-width: ;100% align: center;",
                    "placeholder": "name",
                }),
            "manufacturer": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "style": "max-width: ;100% align: center;",
                    "placeholder": "name",
                }),
            "manufacturerpartnumber": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "style": "max-width: 100%; align: center;",
                    "placeholder": "name",
                }),
            "cabletype": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "style": "max-width: 100%; align: center;",
                    "placeholder": "name",
                }),
        }

class WireRopeDataAddForm(ModelForm):

    class Meta:
        model = WireRopeData
        fields = [
            'name',
            'manufacturer',
            'manufacturerpartnumber',
            'cabletype',
            'nominalbreakingload',
            'weightperfoot',

        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "style": "max-width: ;100% align: center;",
                    "placeholder": "name",
                }),
            "manufacturer": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "style": "max-width: ;100% align: center;",
                    "placeholder": "manufacturer",
                }),
            "manufacturerpartnumber": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "style": "max-width: 100%; align: center;",
                    "placeholder": "manufacturer part number",
                }),
            "cabletype": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "style": "max-width: 100%; align: center;",
                    "placeholder": "cable type",
                }),
        }
