from types import NoneType
from django.db import models
from django.db.models.query_utils import select_related_descend
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Avg, Count, Min, Sum, Max
from django.core.validators import MaxValueValidator
from django.core.exceptions import ValidationError
from datetime import datetime, date
from pandas.core.base import NoNewAttributesMixin
import pyodbc 
import pandas as pd
import mysql.connector
import logging



logging.basicConfig(filename='debug.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


def validate_commas(value):
    if "," in value:
        raise ValidationError("Invalid entry: remove commas")
    else:
        return

class Breaktest(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True, blank=True, null=False)  
    wire = models.ForeignKey('Wire', models.DO_NOTHING, db_column='WireId', blank=True, null=True, verbose_name='Wire', related_name='wire_break_test')  
    date = models.DateField(db_column='Date', blank=True, null=True, verbose_name='Date', validators=[MaxValueValidator(limit_value=date.today)])  
    testedbreakingload = models.IntegerField(db_column='TestedBreakingLoad', blank=True, null=True, verbose_name='Tested breaking load')  
    notes = models.TextField(db_column='Notes', blank=True, null=True, verbose_name='Notes', validators=[validate_commas])  

    class Meta:
        managed = True
        db_table = 'BreakTest'
        verbose_name_plural = "BreakTest"

    def __str__(self):
        return str(self.date)

    @property
    def format_date(self):
        date=self.date
        formatdate=date.strftime("%Y-%m-%d")
        return formatdate

class Calibration(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True, blank=True, null=False)   
    date = models.DateField(db_column='Date', blank=True, null=True, verbose_name='Start date')  
    wire = models.ForeignKey('Wire', models.DO_NOTHING, db_column='WireId', blank=True, null=True, verbose_name='Wire')  
    winch = models.ForeignKey('Winch', models.DO_NOTHING, db_column='WinchId', related_name='calibration_winch', null=True, verbose_name='Winch')  
    notes = models.TextField(db_column='Notes', blank=True, null=True, verbose_name='Notes', validators=[validate_commas])  
    factorofsafety = models.FloatField(db_column='FactorofSafety', blank=True, null=True, verbose_name='Factor of safety')  
    safeworkingtension = models.FloatField(db_column='SafeWorkingTension', blank=True, null=True, verbose_name='Safe Working tension')  
    alarmsetpoint = models.IntegerField(db_column='AlarmSetpoint', blank=True, null=True, verbose_name='Alarm setpoint')  
    tensionmonitoringaccuracy = models.FloatField(db_column='TensionMonitoringAccuracy', blank=True, null=True, verbose_name='Tension Monitoring Accuracy')  
    weightofgear = models.IntegerField(db_column='WeightofGear', blank=True, null=True, verbose_name='Weight of gear')  
    calhighsetpoint = models.IntegerField(db_column='CalHighSetpoint', blank=True, null=True, verbose_name='Calibration high setpoint')  
    callowsetpoint = models.IntegerField(db_column='CalLowSetpoint', blank=True, null=True, verbose_name='Calibration low setpoint')  
    operator = models.TextField(db_column='Operator', blank=True, null=True, verbose_name='Operator', validators=[validate_commas])  

    class Meta:
        managed = True
        db_table = 'Calibration'
        verbose_name_plural = "Calibration"

    @property
    def get_active_winch(self):
        wire=self.wire
        winch=wire.active_winch
        return winch

    @property
    def get_active_fos(self):
        wire=self.wire
        fos=wire.factorofsafety.factorofsafety
        return fos

    @property
    def get_abl(self):
        wire=self.wire
        abl=wire.absolute_breaking_load
        return abl

    @property
    def get_swt(self):
        fos=self.get_active_fos
        abl=self.get_abl
        swt=abl/fos
        return swt
    
    @property
    def get_alarm_factor(self):
        fos=self.get_active_fos
        if fos<2:
            af=1.7
        elif fos<2.5:
            af=2.2
        elif fos<5:
            af=2.8
        else:
            af=None
        return af

    @property
    def get_tension_monitoring_accuracy(self):
        fos=self.get_active_fos
        if fos<2.5:
            tma=3
        elif fos<5:
            tma=4
        else:
            af=None
        return tma

    @property
    def get_alarm_setpoint(self):
        abl=self.get_abl
        af=self.get_alarm_factor
        alarm = (abl/af)-1
        return alarm

    @property
    def cal_high_setpoint(self):
        swt=self.get_swt
        high=swt*0.97
        return high

    @property
    def cal_low_setpoint(self):
        swt=self.get_swt
        low=swt*0.10
        return low

    def worksheet_calculation(self):
        if self.wire:

            self.winch=self.get_active_winch
            self.factorofsafety=self.get_active_fos
            self.safeworkingtension=self.get_swt
            self.alarm_factor=self.get_alarm_factor
            self.alarmsetpoint=self.get_alarm_setpoint
            self.calhighsetpoint=int(self.cal_high_setpoint)
            self.callowsetpoint=int(self.cal_low_setpoint)
            self.tensionmonitoringaccuracy=self.get_tension_monitoring_accuracy

class TensionVerification(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True, blank=True, null=False)  
    appliedload = models.IntegerField(db_column='AppliedLoad', blank=True, null=True, verbose_name='Applied load')  
    loadcelltension = models.IntegerField(db_column='LoadCellTension', blank=True, null=True, verbose_name='Load cell tension')  
    loadcellrawmv = models.FloatField(db_column='RawmV', blank=True, null=True, verbose_name='Raw mv')  
    calibration = models.ForeignKey('Calibration', db_column='CalibrationId', blank=True, null=True, verbose_name='Calibration id', on_delete=models.CASCADE)  

    class Meta:
        managed = True
        db_table = 'TensionVerification'
        verbose_name_plural = 'TensionVerification'

class TensionCalibration(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True, blank=True, null=False)  
    appliedload = models.IntegerField(db_column='AppliedLoad', blank=True, null=True, verbose_name='Applied load')  
    loadcelltension = models.IntegerField(db_column='LoadCellTension', blank=True, null=True, verbose_name='Load cell tension')  
    loadcellrawmv = models.FloatField(db_column='RawmV', blank=True, null=True, verbose_name='Raw mv')  
    calibration = models.ForeignKey('Calibration', db_column='CalibrationId', blank=True, null=True, verbose_name='Calibration id', on_delete=models.CASCADE)  

    class Meta:
        managed = True
        db_table = 'TensionCalibration'
        verbose_name_plural = 'TensionCalibration'

class CalibrationVerification(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True, blank=True, null=False)  
    appliedload = models.IntegerField(db_column='AppliedLoad', blank=True, null=True, verbose_name='Applied load')  
    loadcelltension = models.IntegerField(db_column='LoadCellTension', blank=True, null=True, verbose_name='Load cell tension')  
    loadcellrawmv = models.FloatField(db_column='RawmV', blank=True, null=True, verbose_name='Raw mv')  
    calibration = models.ForeignKey('Calibration', db_column='CalibrationId', blank=True, null=True, verbose_name='Calibration id', on_delete=models.CASCADE)  

    class Meta:
        managed = True
        db_table = 'CalibrationVerification'
        verbose_name_plural = 'CalibrationVerification'

class Cast(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True, blank=True, null=False)  
    startoperator = models.ForeignKey('WinchOperator', models.DO_NOTHING, db_column='StartOperatorId', null=True, related_name='startoperatorid', verbose_name="Start operator")  
    endoperator = models.ForeignKey('WinchOperator', models.DO_NOTHING, db_column='EndOperatorId', null=True, related_name='endoperatorid', verbose_name='End operator')  
    startdate = models.DateTimeField(db_column='StartDate', blank=True, null=True, verbose_name='Start date and time', validators=[MaxValueValidator(limit_value=datetime.today)])  
    enddate = models.DateTimeField(db_column='EndDate', blank=True, null=True, verbose_name='End date and time', validators=[MaxValueValidator(limit_value=datetime.today)])  
    deploymenttype = models.ForeignKey('Deploymenttype', models.DO_NOTHING, db_column='DeploymentTypeId', null=True, verbose_name='Deployment type')  
    wire = models.ForeignKey('Wire', models.DO_NOTHING, db_column='WireId', blank=True, null=True, verbose_name='Wire')  
    winch = models.ForeignKey('Winch', models.DO_NOTHING, db_column='WinchId', null=True, verbose_name='Winch')  
    notes = models.TextField(db_column='Notes', blank=True, null=True, verbose_name='Notes', validators=[validate_commas])  
    maxtension = models.IntegerField(db_column='MaxTension', blank=True, null=True, verbose_name='Max tension')  
    maxpayout = models.IntegerField(db_column='MaxPayout', blank=True, null=True, verbose_name='Max payout')  
    payoutmaxtension = models.IntegerField(db_column='PayoutMaxTension', blank=True, null=True, verbose_name='Payout at max tension')  
    metermaxtension = models.IntegerField(db_column='MeterMaxTension', blank=True, null=True, verbose_name='Meter mark at max tension')  
    timemaxtension = models.DateTimeField(db_column='TimeMaxTension', blank=True, null=True, verbose_name='Time at max tension')  
    flagforreview = models.BooleanField(db_column='Flagforreview', blank=True, null=True, verbose_name='Flag for review')  
    dryendtag = models.IntegerField(db_column='DryEndTag', blank=True, null=True, verbose_name='Dry end tag')  
    wetendtag = models.IntegerField(db_column='WetEndTag', blank=True, null=True, verbose_name='Wet end tag')  
    wirerinse = models.BooleanField(db_column='Wirerinse', blank=True, null=True, verbose_name='Wire rinse')  
    wirelength = models.IntegerField(db_column='WireLength', blank=True, null=True, verbose_name='Wire length')  
    factorofsafety = models.FloatField(db_column='FactorofSafety', blank=False, null=True, verbose_name='Factor of safety')  
    safeworkingtension = models.FloatField(db_column='SafeWorkingTension', blank=False, null=True, verbose_name='Safe Working tension')  
    duration = models.IntegerField(db_column='Duration', blank=True, null=True, verbose_name='Duration')  


    class Meta:
        managed = True
        db_table = 'Cast'
        verbose_name_plural = "Cast"

    def get_absolute_url(self):
        return reverse('castdetail', kwargs={'pk':self.pk})

    def __str__(self):
        return str(self.startdate)

    @property
    def dry_end_tag(self):
        wire=self.wire
        if wire and wire.active_dryendtag:
            dryend=wire.dryendtag
            return dryend

    @property
    def wet_end_tag(self):
        wire=self.wire
        if wire and wire.active_wetendtag:
            wetend=wire.active_wetendtag
            return wetend

    @property
    def active_winch(self):
        if self.winch.name:
            d=self.winch.name
            return d

    @property
    def active_wire(self):
        if self.winch and self.winch.active_wire:
            d=self.winch.active_wire
            return d
    
    @property
    def active_wire_length(self):
        if self.active_wire:
            d=self.active_wire.active_length
            return d

    @property
    def active_wire_safeworkingtension(self):
        if self.active_wire:
            d=self.active_wire.safe_working_tension
            return d

    @property
    def active_wire_factorofsafety(self):
        if self.active_wire:
            d=self.active_wire.factorofsafety 
            return d

    @property
    def format_startdate(self):
        if self.startdate:
            date=self.startdate
            formatdate=date.strftime("%Y-%m-%d, %H:%M:%S")
            return formatdate

    @property
    def format_startdate_csv(self):
        if self.startdate:
            date=self.startdate
            formatdate=date.strftime("%Y-%m-%d %H:%M:%S")
            return formatdate

    @property
    def format_startdate_url(self):
        if self.startdate:
            date=self.startdate
            formatdate=date.strftime("%Y-%m-%d")
            return formatdate

    @property
    def format_enddate_url(self):
        if self.enddate:
            date=self.enddate
            formatdate=date.strftime("%Y-%m-%d")
            return formatdate

    @property
    def format_timemaxtension(self):
        if not self.timemaxtension:
            return
        date=self.timemaxtension
        formatdate=date.strftime("%Y-%m-%d, %H:%M:%S")
        return formatdate

    @property
    def wire_in(self):
        if self.wirelength and self.payoutmaxtension:
            wirein=self.wirelength-self.payoutmaxtension
            return wirein

    def get_active_wire(self):
        if self.active_wire:
            self.wire=self.active_wire
        return

    def get_active_length(self):
        if self.active_wire_length:
            self.wirelength=self.active_wire_length
        return

    def get_active_factorofsafety(self):
        if self.active_wire_factorofsafety:
            self.factorofsafety=self.active_wire_factorofsafety.factorofsafety
        return

    def get_active_safeworkingtension(self):
        if self.active_wire_safeworkingtension:
            self.safeworkingtension=self.active_wire_safeworkingtension
        return

    def endcastcal(self):
        logging.debug("endcastcal() called for cast %s", self.pk)
        winch = self.winch.name
        wetend = int(self.wet_end_tag) if self.wet_end_tag else None
        dryend = int(self.dry_end_tag) if self.dry_end_tag else None

        try:
            conn = mysql.connector.connect(
                host='127.0.0.1',
                user='root',
                password='b1uz00!!2SQ',
                database='winch_data'
            )

            startcal = str(self.startdate)
            endcal = str(self.enddate)
            df = pd.read_sql_query(
                f"SELECT * FROM {winch} WHERE date_time BETWEEN '{startcal}' AND '{endcal}'",
                conn
            )

            if not df.empty:
                logging.debug("DataFrame shape: %s", df.shape)

                castmaxtensiondf = df[df.tension_load_cell == df.tension_load_cell.max()]
                castmaxtension = castmaxtensiondf['tension_load_cell'].max()
                castmaxpayout = df['payout'].max()
                castpayoutmaxtension = castmaxtensiondf['payout'].max()
                casttimemaxtension = castmaxtensiondf['date_time'].max()

                if wetend is not None and dryend is not None:
                    if wetend > dryend:
                        castmetermaxtension = wetend - int(castpayoutmaxtension)
                    else:
                        castmetermaxtension = wetend + int(castpayoutmaxtension)

                self.maxtension = castmaxtension
                self.maxpayout = castmaxpayout
                self.payoutmaxtension = castpayoutmaxtension
                self.timemaxtension = casttimemaxtension
                self.metermaxtension = castmetermaxtension
                logging.debug("max tension is: %s", castmaxtension)
                logging.debug("max payout is: %s", castmaxpayout)

            else:
                logging.warning("No data was found for the timeframe entered. Start: %s, End: %s", startcal, endcal)
                self.maxtension = None
                self.maxpayout = None
                self.payoutmaxtension = None
                self.timemaxtension = None
                self.metermaxtension = None

            conn.close()

        except Exception as e:
            logging.error("Unexpected error during endcastcal: %s", e, exc_info=True)   

            if self.wet_end_tag and self.dry_end_tag:
                wetend=int(self.wet_end_tag)
                self.wetendtag=wetend
                dryend=int(self.dry_end_tag)
                self.dryendtag=dryend
            return

    def startcast_get_datetime(self):
        if self.startdate is None:
            current_datetime = datetime.now()
            self.startdate = current_datetime

    def endcast_get_datetime(self):
        if self.enddate is None:
            current_datetime = datetime.now()
            self.enddate = current_datetime

    def get_cast_duration(self):
        if self.enddate and self.startdate:
            start = self.startdate
            end = self.enddate
            duration = (end - start)
            duration_in_minutes = round(duration.total_seconds() / 60)
            self.duration = duration_in_minutes


class Cruise(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True, blank=True, null=False)   
    number = models.TextField(db_column='Number', blank=True, null=True, verbose_name='Cruise number', validators=[validate_commas])   
    startdate = models.DateField(db_column='StartDate', blank=True, null=True, verbose_name='Start date')   
    enddate = models.DateField(db_column='EndDate', blank=True, null=True, verbose_name='End date')   
    winchnotes = models.TextField(db_column='WinchNotes', blank=True, null=True, verbose_name='Winch Notes', validators=[validate_commas])   
    scienceprovidedwinchnotes = models.TextField(db_column='ScienceProvidedWinch', blank=True, null=True, verbose_name='Science Provided Winch', validators=[validate_commas])   

    class Meta:
        managed = True
        db_table = 'Cruise'
        verbose_name_plural = 'cruise'

    def __str__(self):
        return str(self.number)

    @property
    def format_startdate(self):
        date=self.startdate
        formatdate=date.strftime("%Y-%m-%d")
        return formatdate

    @property
    def format_enddate(self):
        if not self.enddate:
            return
        date=self.enddate
        formatdate=date.strftime("%Y-%m-%d")
        return formatdate

class CutbackRetermination(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True, blank=True, null=False)  
    wetendtag = models.IntegerField(db_column='WetEndTag', blank=True, null=True, verbose_name='Wet end tag value (m)')  
    dryendtag = models.IntegerField(db_column='DryEndTag', blank=True, null=True, verbose_name='Dry end tag value (m)')  
    wire = models.ForeignKey('Wire', models.DO_NOTHING, db_column='WireId', blank=True, null=True, related_name='wire_cutback_retermination', verbose_name='Wire')  
    terminationtype = models.ForeignKey('TerminationType', models.DO_NOTHING, db_column='TerminationType', blank=True, null=True, related_name='wire_termination_type', verbose_name='Termination Type')  
    notes = models.TextField(db_column='Notes', blank=True, null=True, verbose_name='Notes', validators=[validate_commas])  
    date = models.DateField(db_column='Date', blank=True, null=True, verbose_name='Date', validators=[MaxValueValidator(limit_value=date.today)])
    lengthaftercutback = models.IntegerField(db_column='LengthAfterCutback', blank=True, null=True, verbose_name='Length after cutback')  

    class Meta:
        managed = True
        db_table = 'CutbackRetermination'
        verbose_name_plural = "CutbackRetermination"

    def __str__(self):
        return str(self.date)

    @property
    def wire_dry_end_tag(self):
        w=self.wire.dryendtag
        return w

    @property
    def length(self):
        if self.wire_dry_end_tag and self.wetendtag:
            dryendlength=self.wire_dry_end_tag
            wetendlength=self.wetendtag
            length=wetendlength-dryendlength
            return length

    @property
    def format_date(self):
        date=self.date
        formatdate=date.strftime("%Y-%m-%d")
        return formatdate

    def submit_length(self):
        if not self.wire_dry_end_tag and not self.wetendtag:
            print(self.wire_dry_end_tag, self.wetendtag)
            return
        else:
            dryendlength=self.wire_dry_end_tag
            wetendlength=self.wetendtag
            length=wetendlength-dryendlength
            self.lengthaftercutback=abs(int(length))
            return

    def submit_dry_end_tag(self):
        if self.wire_dry_end_tag:
            dryendtag=self.wire_dry_end_tag
            self.dryendtag=dryendtag
            return

    def edit_length(self):
        if not self.wire_dry_end_tag and self.wetendtag:
            return
        else:
            dryendlength=self.wire_dry_end_tag
            wetendlength=self.wetendtag
            length=wetendlength-dryendlength
            self.lengthaftercutback=abs(int(length))
            return

class TerminationType(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True, blank=True, null=False)  
    name = models.TextField(db_column='Name', blank=True, null=False, verbose_name='Termination Type', validators=[validate_commas])  
    
    class Meta:
        managed = True
        db_table = 'TerminationType'
        verbose_name_plural = "TerminationType"

    def __str__(self):
        return str(self.name)


class DeploymentType(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True, blank=True, null=False)  
    status = models.BooleanField(db_column='Status', blank=True, null=True, verbose_name='Status')  
    name = models.TextField(db_column='Name', blank=True, null=True, verbose_name='Name', validators=[validate_commas])
    equipment = models.TextField(db_column='Equipment', blank=True, null=True, verbose_name='Equipment', validators=[validate_commas])  
    notes = models.TextField(db_column='Notes', blank=True, null=True, verbose_name='Notes', validators=[validate_commas])  

    class Meta:
        managed = True
        db_table = 'DeploymentType'
        verbose_name_plural = "DeploymentType"
        ordering = ['name']

    def get_absolute_url(self):
        return reverse('deploymentdetail', kwargs={'pk':self.pk})

    def __str__(self):
        return str(self.name)

class Location(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True, blank=True, null=False)  
    location = models.TextField(db_column='Location', blank=True, null=True, verbose_name='Location', validators=[validate_commas])  

    class Meta:
        managed = True
        db_table = 'Location'
        verbose_name_plural = "Location"
        ordering = ['location']


    def __str__(self):
        return str(self.location)
		

class Dynomometer(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True, blank=True, null=False)  
    name = models.TextField(db_column='Name', blank=True, null=True, verbose_name='Name', validators=[validate_commas])  
    dynomometertype = models.TextField(db_column='DynomometerType', blank=True, null=True, verbose_name='Dynomometer type', validators=[validate_commas])  
    comments = models.TextField(db_column='Comments', blank=True, null=True, verbose_name='notes', validators=[validate_commas])  

    class Meta:
        managed = True
        db_table = 'Dynomometer'
        verbose_name_plural = "Dynomometer"

    def __str__(self):
        return str(self.name)

class Frame(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True, blank=True, null=False)  
    name = models.TextField(db_column='Name', blank=True, null=True, verbose_name='Name', validators=[validate_commas])  
    frametype = models.TextField(db_column='FrameType', blank=True, null=True, verbose_name='Frame type', validators=[validate_commas])  

    class Meta:
        managed = True
        db_table = 'Frame'
        verbose_name_plural = "Frame"

    def __str__(self):
        return str(self.name)

class Lubrication(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True, blank=True, null=False)  
    wire = models.ForeignKey('Wire', models.DO_NOTHING, db_column='WireId', blank=True, null=True, verbose_name='Wire')  
    lubetype = models.TextField(db_column='LubeType', blank=True, null=True, verbose_name='Lube type', validators=[validate_commas])  
    date = models.DateField(db_column='Date', blank=True, null=True, verbose_name='Date', validators=[MaxValueValidator(limit_value=date.today)])  
    lubelength = models.IntegerField(db_column='LubeLength', blank=True, null=True, verbose_name='Length lubed')
    lubestartmetermark = models.IntegerField(db_column='LubeStartMeterMark', blank=True, null=True, verbose_name='Start meter mark')
    lubeendmetermark = models.IntegerField(db_column='LubeEndMeterMark', blank=True, null=True, verbose_name='End meter mark')
    notes = models.TextField(db_column='Notes', blank=True, null=True, verbose_name='Notes', validators=[validate_commas])  

    class Meta:
        managed = True
        db_table = 'Lubrication'
        verbose_name_plural = "Lubrication"

    def __str__(self):
        return str(self.date)

    @property
    def format_date(self):
        date=self.date
        formatdate=date.strftime("%Y-%m-%d")
        return formatdate

class FactorOfSafety(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True, blank=True, null=False)  
    factorofsafety = models.FloatField(db_column='FactorofSafety', blank=False, null=False, default=5.0, verbose_name='Factor of safety')  

    class Meta:
        managed = True
        db_table = 'FactorOfSafety'
        verbose_name_plural = "FactorOfSafety"
        ordering = ['factorofsafety']
        
    def __str__(self):
        return str(self.factorofsafety)

class Winch(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True, blank=True, null=False)  
    name = models.TextField(db_column='Name', blank=True, null=True, verbose_name='Name', validators=[validate_commas])
    ship = models.TextField(db_column='Ship', blank=True, null=True, verbose_name='Ship', validators=[validate_commas])  
    institution = models.TextField(db_column='Institution', blank=True, null=True, verbose_name='Institution', validators=[validate_commas])  
    manufacturer = models.TextField(db_column='Manufacturer', blank=True, null=True, verbose_name='Manufacturer', validators=[validate_commas])  
    status = models.BooleanField(db_column='Status', blank=True, null=True, verbose_name='Status')  

    class Meta:
        managed = True
        db_table = 'Winch'
        verbose_name_plural = "Winch"
        ordering = ['name']

    def get_absolute_url(self):
        return reverse('winchdetail', kwargs={'pk':self.pk})

    def __str__(self):
        return str(self.name)

    @property
    def active_wire(self):
        if self.wirelocation_set:
            lastlocation=self.wirelocation_set.order_by('date').last()
            if lastlocation:
                lastwire=lastlocation.active_wire
                active_wire_winch=lastwire.active_winch
                if active_wire_winch == self:
                    return lastwire
                else:
                    return None
        

class WinchOperator(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True, blank=True, null=False)    
    status = models.BooleanField(db_column='Status', blank=True, null=True, verbose_name='Status')  
    firstname = models.TextField(db_column='FirstName', blank=True, null=True, verbose_name='First name', validators=[validate_commas])  
    lastname = models.TextField(db_column='LastName', blank=True, null=True, verbose_name='Last name', validators=[validate_commas])  
    username = models.TextField(db_column='UserName', blank=True, null=True, verbose_name='User name', validators=[validate_commas])  


    class Meta:
        managed = True
        db_table = 'WinchOperator'
        verbose_name_plural = "WinchOperator"
        ordering = ['username']

    def get_absolute_url(self):
        return reverse('operatordetail', kwargs={'pk':self.pk})

    def __str__(self):
        return str(self.username)

class WireRopeData(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True, blank=True, null=False)  
    name = models.TextField(db_column='Name', blank=True, null=True, verbose_name='Name', validators=[validate_commas])
    manufacturer = models.TextField(db_column='Manufacturer',blank=True, null=True, verbose_name='Manufacturer', validators=[validate_commas])
    manufacturerpartnumber = models.TextField(db_column='ManufacturerPartNumber', blank=True, null=True, verbose_name='Manufacturer part number', validators=[validate_commas])  
    cabletype = models.TextField(db_column='CableType', blank=True, null=True, verbose_name='Cable type', validators=[validate_commas])  
    nominalbreakingload = models.IntegerField(db_column='nominalbreakingload', blank=True, null=True, verbose_name='Nominal breaking load')  
    weightperfoot = models.FloatField(db_column='WeightPerFoot', blank=True, null=True, verbose_name='Weight per foot')  
    
    class Meta:
        managed = True
        db_table = 'WireRopeData'
        verbose_name_plural = 'WireRopeData'

    def __str__(self):
        return str(self.name)

class OwnershipStatus(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True, blank=True, null=False)    
    status = models.TextField(db_column='Status', blank=True, null=True, verbose_name='Status', validators=[validate_commas])  


    class Meta:
        managed = True
        db_table = 'OwnershipStatus'
        verbose_name_plural = "OwnershipStatus"

    def __str__(self):
        return str(self.status)

class Wire(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True, blank=True, null=False)  
    wirerope = models.ForeignKey(WireRopeData, models.DO_NOTHING, db_column='WireRopeId', blank=True, null=True, verbose_name='Wire type')    
    manufacturerid = models.TextField(db_column='ManufacturerId', blank=True, null=True, verbose_name='Manufacturer id', validators=[validate_commas])  
    nsfid = models.TextField(db_column='NsfId', blank=True, null=True, verbose_name='NSF id', validators=[validate_commas])  
    dateacquired = models.DateField(db_column='DateAcquired', blank=True, null=True, verbose_name='Date acquired', validators=[MaxValueValidator(limit_value=date.today)])  
    notes = models.TextField(db_column='Notes', blank=True, null=True, verbose_name='notes', validators=[validate_commas])  
    status = models.BooleanField(db_column='Status', blank=True, null=True, verbose_name='Active status')
    ownershipstatus = models.ForeignKey(OwnershipStatus, models.DO_NOTHING, db_column='OwnershipStatusId', blank=True, null=True, verbose_name='Ownership status')  
    factorofsafety = models.ForeignKey(FactorOfSafety, models.DO_NOTHING, db_column='FactorofSafety', blank=True, null=True, related_name='wirefactorofsafety', verbose_name='Factor of safety')  
    dryendtag = models.IntegerField(db_column='DryEndTag', blank=True, null=True, verbose_name='Dry end tag value (m)')  

    class Meta:
        managed = True
        db_table = 'Wire'
        verbose_name_plural = "Wire"


    def get_absolute_url(self):
        return reverse('wiredetail', kwargs={'pk':self.pk})

    def __str__(self):
        return str(self.nsfid)

    @property
    def active_wire_location(self):
        if not self.wirelocation_set:
            return None
        d=self.wirelocation_set.order_by('date').last()
        return d

    @property
    def active_location(self):
        if not self.active_wire_location:
            return None
        d=self.active_wire_location.location
        return d

    @property
    def active_winch(self):
        if not self.active_wire_location:
            return None
        d=self.active_wire_location.winch
        return d

    @property 
    def active_wire_cutback(self):
        if self.wire_cutback_retermination:
            c=self.wire_cutback_retermination.order_by('date').last()
            return c    

    @property
    def active_wetendtag(self):
        if self.active_wire_cutback:
            w=self.active_wire_cutback.wetendtag
            return w

    @property
    def active_dryendtag(self):
        if self.active_wire_cutback:
            w=self.active_wire_cutback.dryendtag
            return w

    @property 
    def active_length(self):
        if not self.active_wire_cutback:
           return None
        else:
            if self.dryendtag is not None:
                dryend=self.dryendtag
                wetend=self.active_wire_cutback.wetendtag
                length=(wetend-dryend)
                abslength=abs(length)
                print(abslength)
                return abslength
            else:
                None
    @property
    def active_break_test(self):
        b=self.wire_break_test.order_by('date').last()
        return b

    @property
    def tested_breaking_load(self):
        if not self.active_break_test:
            return None
        f=self.active_break_test.testedbreakingload
        return f

    @property
    def nominal_breaking_load(self):
        w=Wire.wirerope.get_object(self)
        n=w.nominalbreakingload
        return n

    @property 
    def absolute_breaking_load(self):
        wire=Wire.wirerope.get_object(self)
        nominal=wire.nominalbreakingload
        if not self.active_break_test:
            return None
        tested=self.active_break_test.testedbreakingload
        if nominal > tested:
            return tested
        else:
            return nominal

    @property 
    def safe_working_tension(self):
        if not self.factorofsafety:
            return None
        if not self.factorofsafety.factorofsafety:
            return None
        if not self.absolute_breaking_load:
            return None
        s=self.factorofsafety.factorofsafety
        i=self.absolute_breaking_load
        swl=i/s 
        swl=int(swl)
        return swl


class WireLocation(models.Model):
    id = models.AutoField(db_column='Id', primary_key=True, blank=True, null=False)  
    date= models.DateField(db_column='Date', blank=True, null=True, verbose_name='Date', validators=[MaxValueValidator(limit_value=date.today)])  
    enteredby = models.ForeignKey(User, models.DO_NOTHING, db_column='EnteredBy', blank=True, null=True, verbose_name='Entered by')  
    wireid = models.ForeignKey(Wire, models.DO_NOTHING, db_column='WireId', blank=True, null=True, verbose_name='Wire')  
    winch = models.ForeignKey(Winch, models.DO_NOTHING, db_column='WinchId', blank=True, null=True, verbose_name='Winch')  
    location = models.ForeignKey(Location, models.DO_NOTHING, db_column='LocationId', blank=True, null=True, verbose_name='Location')  
    notes = models.TextField(db_column='Notes', blank=True, null=True, verbose_name='notes', validators=[validate_commas])  

    class Meta:
        managed = True
        db_table = 'WireLocation'
        verbose_name_plural = "WireLocation"
        
    def __str__(self):
        return str(self.location)

    @property
    def active_wire(self):
        wire=self.wireid
        if not wire:
            return None
        else:
            wire=self.wireid
            return wire

    @property
    def format_date(self):
        if not self.date:
            return None
        else:
            date=self.date
            formatdate=date.strftime("%Y-%m-%d")
            return formatdate


