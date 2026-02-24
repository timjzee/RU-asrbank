"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils.html import escape
from django.utils.safestring import mark_safe

import re       # Regular expession for validation

from asrbank.transcription.models import *
pat_Year = re.compile("^[0-9][0-9][0-9][0-9]$")


def init_choices(obj, sFieldName, sSet, maybe_empty=False):
    if (obj.fields != None and sFieldName in obj.fields):
        obj.fields[sFieldName].choices = build_choice_list(sSet, maybe_empty=maybe_empty)
        obj.fields[sFieldName].help_text = get_help(sSet)

def validate_year(value):
    if value == None or value == "":
        return 'Please specify a year'
    if value != "unknown" and value != "-":
        # Now it must be an integer
        if not pat_Year.match(value):
            return 'Specify a year (JJJJ) or "unknown"'
        # Convert to number
        try:
            iValue = int(value)
        except:
            return 'Specify a year (JJJJ) or "unknown"'
        # Test the number
        if iValue > datetime.now().year + 10:
            return 'The year may not be larger than the current year + 10'
        if iValue < 0:
            return 'The year must be a positive number'
    return ""

def add_required_label_tag(original_function):
    """Adds the 'required' CSS class and an asterisks to required field labels."""

    def required_label_tag(self, contents=None, attrs=None, label_suffix=None):
        contents = contents or escape(self.label)
        asterisk = ""
        if self.field.required:
            asterisk = "<span class=\"required-star\">*</span>"
        # Get the original <label> creation
        bk = original_function(self, contents, attrs, label_suffix)
        # Combine this using the mark_safe() function
        sBack = mark_safe("{}\n{}".format(bk, asterisk))
        return sBack
    return required_label_tag

def decorate_bound_field():
    """Override the [label_tag()] function for Bound fields"""

    from django.forms.forms import BoundField
    BoundField.label_tag = add_required_label_tag(BoundField.label_tag)

# Call the above
decorate_bound_field()

class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'User name'}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Password'}))
    

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )


class LanguageAdminForm(forms.ModelForm):

    class Meta:
        model = Language
        fields = ['name']
        widgets = { 'name': forms.Select(attrs={'width': 30}) }

    def __init__(self, *args, **kwargs):
        super(LanguageAdminForm, self).__init__(*args, **kwargs)
        init_choices(self, 'name', INTERVIEW_LANGUAGE)
        self.fields['name'].initial = choice_value(INTERVIEW_LANGUAGE, "unknown")


class FileFormatAdminForm(forms.ModelForm):

    class Meta:
        model = FileFormat
        fields = ['name']
        widgets = { 'name': forms.Select(attrs={'width': 30, 'simple': True}) }

    def __init__(self, *args, **kwargs):
        super(FileFormatAdminForm, self).__init__(*args, **kwargs)
        init_choices(self, 'name', AUDIOVIDEO_FORMAT)
        self.fields['name'].initial = choice_value(AUDIOVIDEO_FORMAT, "unknown")


class AvailabilityAdminForm(forms.ModelForm):

    class Meta:
        model = Availability
        fields = ['name']
        widgets = { 'name': forms.Select(attrs={'width': 30, 'simple': True}) }

    def __init__(self, *args, **kwargs):
        super(AvailabilityAdminForm, self).__init__(*args, **kwargs)
        init_choices(self, 'name', AVAILABILITY)
        self.fields['name'].initial = choice_value(AVAILABILITY, "unknown")


class IntervieweeAdminForm(forms.ModelForm):

    class Meta:
        model = Interviewee
        fields = ['code', 'name', 'gender', 'age']
        widgets = {'code': forms.Textarea(attrs={'rows': 1, 'cols': 20}),
                   'name': forms.Textarea(attrs={'rows': 1, 'cols': 80}),
                   'gender': forms.Select(attrs={'width': 30}),
                   'age': forms.Textarea(attrs={'rows': 1, 'cols': 5})  }

    def __init__(self, *args, **kwargs):
        super(IntervieweeAdminForm, self).__init__(*args, **kwargs)
        init_choices(self, 'gender', PARTICIPANT_GENDER, True)
        self.fields['gender'].initial = '0'


class InterviewerAdminForm(forms.ModelForm):

    class Meta:
        model = Interviewer
        fields = ['code', 'name', 'gender', 'age']
        widgets = {'code': forms.Textarea(attrs={'rows': 1, 'cols': 20}),
                   'name': forms.Textarea(attrs={'rows': 1, 'cols': 80}),
                   'gender': forms.Select(attrs={'width': 30}),
                   'age': forms.Textarea(attrs={'rows': 1, 'cols': 5})  }

    def __init__(self, *args, **kwargs):
        super(InterviewerAdminForm, self).__init__(*args, **kwargs)
        init_choices(self, 'gender', PARTICIPANT_GENDER, True)
        self.fields['gender'].initial = choice_value(PARTICIPANT_GENDER, "unknown")


class TemporalCoverageAdminForm(forms.ModelForm):

    class Meta:
        model = TemporalCoverage
        fields = ['startYear', 'endYear']
        widgets = {'startYear': forms.Textarea(attrs={'rows': 1, 'cols': 20, 'simple': True}),
                   'endYear': forms.Textarea(attrs={'rows': 1, 'cols': 20, 'simple': True})}

    def clean(self):
        cleaned_data = super(TemporalCoverageAdminForm, self).clean()
        # Treat the first year
        yr1 = cleaned_data['startYear']
        val_yr1 = validate_year(yr1)
        if val_yr1 != "":
            raise forms.ValidationError(val_yr1)
        # Treat the second year
        yr2 = cleaned_data['endYear']
        val_yr2 = validate_year(yr2)
        if val_yr2 != "":
            raise forms.ValidationError(val_yr2)
        # Check if we may continue
        if val_yr1 == "" and val_yr2 == "":
            # Compare the values
            if pat_Year.match(yr2) and pat_Year.match(yr1) and int(yr2) < int(yr1):
                raise forms.ValidationError("The end year must be later than the start year")

class SpatialCoverageAdminForm(forms.ModelForm):

    class Meta:
        model = SpatialCoverage
        fields = ['country', 'place']
        widgets = {'country': forms.Select(attrs={'width': 30, 'simple': True}),
                   'place': forms.Textarea(attrs={'rows': 1, 'cols': 80})  }

    def __init__(self, *args, **kwargs):
        super(SpatialCoverageAdminForm, self).__init__(*args, **kwargs)
        init_choices(self, 'country', COVERAGE_SPATIAL_COUNTRY, True)
        self.fields['country'].initial = '0'


class TopicAdminForm(forms.ModelForm):

    class Meta:
        model = Topic
        fields = ['name']
        widgets = { 'name': forms.Textarea(attrs={'rows': 1, 'cols': 80, 'simple': True}) }


class GenreAdminForm(forms.ModelForm):

    class Meta:
        model = Genre
        fields = ['name']
        widgets = { 'name': forms.Select(attrs={'width': 30}) }

    def __init__(self, *args, **kwargs):
        super(GenreAdminForm, self).__init__(*args, **kwargs)
        init_choices(self, 'name', INTERVIEW_GENRE)
        self.fields['name'].initial = choice_value(INTERVIEW_GENRE, "interviews")


class AnnotationAdminForm(forms.ModelForm):

    class Meta:
        model = Annotation
        fields = ['type', 'mode', 'format']
        widgets = { 'type':   forms.Select(attrs={'width': 30}),
                    'mode':   forms.Select(attrs={'width': 30}),
                    'format': forms.Select(attrs={'width': 30}) }

    def __init__(self, *args, **kwargs):
        super(AnnotationAdminForm, self).__init__(*args, **kwargs)
        init_choices(self, 'type', ANNOTATION_TYPE)
        init_choices(self, 'mode', ANNOTATION_MODE, True)
        init_choices(self, 'format', ANNOTATION_FORMAT, True)
        self.fields['type'].initial = choice_value(ANNOTATION_TYPE, "orthographicTranscription")
        self.fields['mode'].initial = '0'
        self.fields['format'].initial = '0'


class AnonymisationAdminForm(forms.ModelForm):

    class Meta:
        model = Anonymisation
        fields = ['name']
        widgets = { 'name': forms.Select(attrs={'width': 30}) }

    def __init__(self, *args, **kwargs):
        super(AnonymisationAdminForm, self).__init__(*args, **kwargs)
        init_choices(self, 'name', ANONYMISATION)
        self.fields['name'].initial = choice_value(ANONYMISATION, "other")


class DescriptorAdminForm(forms.ModelForm):

    class Meta:
        model = Descriptor
        fields = ['identifier', 'access', 'projectTitle', 'interviewId', 'interviewDate', 'interviewLength', 'copyright','modality']
        # Hide the 'copyright' field: https://code.djangoproject.com/ticket/22137
        widgets = {
            'copyright': forms.TextInput(attrs={'type': 'hidden'})
            }

    def __init__(self, *args, **kwargs):
        super(DescriptorAdminForm, self).__init__(*args, **kwargs)
        # Initialize FieldChoice fields on the main page
        init_choices(self, 'modality', INTERVIEW_MODALITY)
        init_choices(self, 'access', DESCRIPTOR_ACCESS)
        # Set the initial/default value for some fields
        self.fields['modality'].initial = choice_value(INTERVIEW_MODALITY, "spoken")
        self.fields['access'].initial = choice_value(DESCRIPTOR_ACCESS, "just me")



