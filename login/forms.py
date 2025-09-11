from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, HazardReport, HazardMedia

class CustomUserCreationForm(UserCreationForm):
    wallet_address = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.HiddenInput()  # Filled via JS for admins
    )
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter email address'
    }))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter first name'
    }))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter last name'
    }))
    user_type = forms.ChoiceField(choices=UserProfile.USER_TYPES, required=True, widget=forms.Select(attrs={
        'class': 'form-control'
    }))
    phone_number = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter phone number'
    }))
    department = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Enter department'
    }))

    class Meta:
        model = User
        fields = (
            "username", "first_name", "last_name", "email",
            "password1", "password2", "user_type", "wallet_address",
            "phone_number", "department"
        )
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter username'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm password'})

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        wallet_address = cleaned_data.get('wallet_address')

        # Require wallet address if user type is admin
        if user_type == 'admin' and not wallet_address:
            raise forms.ValidationError("Admin users must connect a MetaMask wallet.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]

        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                user_type=self.cleaned_data["user_type"],
                phone_number=self.cleaned_data.get("phone_number"),
                department=self.cleaned_data.get("department"),
                wallet_address=self.cleaned_data.get("wallet_address")  # Save wallet for admins
            )
        return user


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
    )

class HazardReportForm(forms.ModelForm):
    class Meta:
        model = HazardReport
        fields = [
            'hazard_type', 'severity', 'description',
            'latitude', 'longitude', 'contact_number', 'urgent'
        ]
        widgets = {
            'hazard_type': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'severity': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the hazard situation in detail...',
                'required': True
            }),
            'contact_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your contact number (optional)'
            }),
            'urgent': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }

    def clean_latitude(self):
        latitude = self.cleaned_data.get('latitude')
        if latitude is None:
            raise forms.ValidationError("Latitude is required.")
        if not (-90 <= latitude <= 90):
            raise forms.ValidationError("Invalid latitude. Must be between -90 and 90.")
        return latitude

    def clean_longitude(self):
        longitude = self.cleaned_data.get('longitude')
        if longitude is None:
            raise forms.ValidationError("Longitude is required.")
        if not (-180 <= longitude <= 180):
            raise forms.ValidationError("Invalid longitude. Must be between -180 and 180.")
        return longitude

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('latitude') is None or cleaned_data.get('longitude') is None:
            raise forms.ValidationError("Please select a location on the map.")
        return cleaned_data

# Form for filtering reports
class ReportFilterForm(forms.Form):
    FILTER_CHOICES = [
        ('all', 'All Reports'),
        ('today', 'Today'),
        ('week', 'This Week'),
        ('month', 'This Month'),
    ]
    
    HAZARD_TYPE_FILTER = [
        ('all', 'All Types'),
        ('tsunami', 'Tsunami'),
        ('storm_surge', 'Storm Surge'),
        ('high_waves', 'High Waves'),
        ('swell_surge', 'Swell Surge'),
        ('coastal_flooding', 'Coastal Flooding'),
        ('unusual_tides', 'Unusual Tides'),
        ('coastal_erosion', 'Coastal Erosion'),
        ('other', 'Other'),
    ]
    
    SEVERITY_FILTER = [
        ('all', 'All Severities'),
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_FILTER = [
        ('all', 'All Status'),
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('investigating', 'Under Investigation'),
    ]
    
    time_filter = forms.ChoiceField(
        choices=FILTER_CHOICES,
        initial='all',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    hazard_type = forms.ChoiceField(
        choices=HAZARD_TYPE_FILTER,
        initial='all',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    severity = forms.ChoiceField(
        choices=SEVERITY_FILTER,
        initial='all',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    status = forms.ChoiceField(
        choices=STATUS_FILTER,
        initial='all',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by location or description...'
        })
    )