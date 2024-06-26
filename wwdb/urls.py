# wwdb/urls.py
from django.urls import path
from . import views
from .views import *


urlpatterns = [
    path('home/', views.home, name='home'),
    path('logout_view/', views.logout_view, name='logout_view'),

    #URLS related to cast reporting
    path('casts/<int:pk>/', views.castdetail, name='castdetail'),
    path('casts/<id>/castenddetail', views.castenddetail, name='castenddetail'),
    path('casts/', views.caststart, name='caststart'),
    path('casts/manualenter/', views.castmanualenter, name='castmanualenter'),
    path('casts/<int:id>/manualedit/', views.castmanualedit, name='castmanualedit'),
    path('casts/<int:id>/edit/', views.castedit, name='castedit'),
    path('casts/<int:pk>/delete/', CastDelete.as_view(), name='castdelete'),
    path('casts/<id>/castend/', views.castend, name='castend'),
    path('casts/cast_end/', views.cast_end, name='cast_end'),


    #URLS related to configuration
    path('configuration/cruiseadd/', views.cruiseadd, name='cruiseadd'),
    path('configuration/cruise/<int:id>/edit/', views.cruiseedit, name='cruiseedit'),
    path('configuration/cruiseconfiguration/', views.cruiseconfigurehome, name='cruiseconfigurehome'),
    path('configuration/operatorlist/', OperatorList.as_view(), name='operatorlist'),
    path('configuration/operator/<int:pk>/operatordetail', OperatorDetail.as_view(), name='operatordetail'),
    path('configuration/operator/<int:pk>/edit/', OperatorEdit.as_view(), name='operatoredit'),
    path('configuration/operator/<int:id>/editstatus/', views.operatoreditstatus, name='operatoreditstatus'),
    path('configuration/operatoradd/', views.operatoradd, name='operatoradd'),
    path('configuration/deploymentlist/', DeploymentList.as_view(), name='deploymentlist'),
    path('configuration/deployment/<int:pk>/deploymentdetail', DeploymentDetail.as_view(), name='deploymentdetail'),
    path('configuration/deployment/<int:pk>/edit/', DeploymentEdit.as_view(), name='deploymentedit'),
    path('configuration/deployment/<int:id>/editstatus/', views.deploymenteditstatus, name='deploymenteditstatus'),
    path('configuration/deploymentadd/', views.deploymentadd, name='deploymentadd'),

    #URLS related to inventories 
    path('inventories/wire/<int:pk>/wiredetail', WireDetail.as_view(), name='wiredetail'),
    path('inventories/wire/<int:pk>/edit/', WireEdit.as_view(), name='wireedit'),
    path('inventories/wire/<int:id>/editfactorofsafety/', views.wireeditfactorofsafety, name='wireeditfactorofsafety'),
    path('inventories/wireadd/', WireAdd.as_view(), name='wireadd'),
    path('inventories/wirelist/', views.wirelist, name='wirelist'),
    path('inventories/winch/<int:pk>/winchdetail', WinchDetail.as_view(), name='winchdetail'),
    path('inventories/winch/<int:pk>/edit/', WinchEdit.as_view(), name='winchedit'),
    path('inventories/winch/<int:id>/editstatus/', views.wincheditstatus, name='wincheditstatus'),
    path('inventories/winchadd/', views.winchadd, name='winchadd'),
    path('inventories/winchlist/', WinchList.as_view(), name='winchlist'),

    #URLS related to maintenance
    path('maintenance/breaktestlist/', views.breaktestlist, name='breaktestlist'),
    path('maintenance/cutbackreterminationlist/', views.cutbackreterminationlist, name='cutbackreterminationlist'),
    path('maintenance/cutbackretermination/<int:pk>/deploymentdetail', CutbackReterminationDetail.as_view(), name='cutbackreterminationdetail'),
    path('maintenance/cutbackretermination/<int:id>/edit/', views.cutbackreterminationedit, name='cutbackreterminationedit'),
    path('maintenance/cutbackreterminationadd/', views.cutbackreterminationadd, name='cutbackreterminationadd'),
    path('maintenance/breaktestadd/', views.breaktestadd, name='breaktestadd'),
    path('maintenance/breaktest/<int:id>/edit/', views.breaktestedit, name='breaktestedit'),
    path('maintenance/breaktestlist', views.breaktestlist, name='breaktestlist'),
    path('maintenance/breaktest/<int:pk>/breaktestdetail', views.breaktestdetail, name='breaktestdetail'),
    path('maintenance/lubricationadd/', views.lubricationadd, name='lubricationadd'),
    path('maintenance/lubrication/<int:id>/edit/', views.lubricationedit, name='lubricationedit'),
    path('maintenance/lubricationlist', views.lubricationlist, name='lubricationlist'),
    path('maintenance/lubrication/<int:pk>/lubricationdetail', views.lubricationdetail, name='lubricationdetail'),
    path('maintenance/lubrication/<int:pk>/delete/', LubricationDelete.as_view(), name='lubricationdelete'),

    #URLS related to reports
    path('reports/castlist/', views.castlist, name='castlist'),
    path('reports/safeworkingtensions/', views.safeworkingtensions, name='safeworkingtensions'),
    path('reports/safeworkingtensions_file/', views.safeworkingtensions_file, name='safeworkingtensions_file'),
    path('reports/<int:pk>/cruisereport/', views.cruisereport, name='cruisereport'),
    path('reports/castplot/<int:pk>/', views.castplot, name='castplot'),
    path('reports/cruiselist/', views.cruiselist, name='cruiselist'),
    path('<int:pk>/cruise_report_file', views.cruise_report_file, name='cruise_report_file'),
    path('reports/<int:pk>/wirereport/', views.wirereport, name='wirereport'),
    path('reports/castreport/', views.castreport, name='castreport'),
    path('reports/unols_report_csv/', views.unols_report_csv, name='unols_report_csv'),
    path('reports/cast_table_csv/', views.cast_table_csv, name='cast_table_csv'),
]