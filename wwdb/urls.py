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
    path('casts/caststartend/', views.caststartend, name='caststartend'),
    path('casts/<int:id>/manualedit/', views.castmanualedit, name='castmanualedit'),
    path('casts/<int:id>/edit/', views.castedit, name='castedit'),
    path('casts/<int:pk>/delete/', CastDelete.as_view(), name='castdelete'),
    path('casts/<id>/castend/', views.castend, name='castend'),
    path('casts/cast_end/', views.cast_end, name='cast_end'),


    #URLS related to configuration
    path('configuration/cruiseadd/', views.cruiseadd, name='cruiseadd'),
    path('configuration/<int:pk>/delete/', CruiseDelete.as_view(), name='cruisedelete'),
    path('configuration/cruise/<int:id>/edit/', views.cruiseedit, name='cruiseedit'),
    path('configuration/cruiseconfiguration/', views.cruiseconfigurehome, name='cruiseconfigurehome'),
    path('configuration/cruisetablelistget', cruisetablelistget, name='cruisetablelistget'),
    path('configuration/cruisetableadd', views.cruisetableadd, name='cruisetableadd'),
    path('configuration/cruisetableaddsubmit', views.cruisetableaddsubmit, name='cruisetableaddsubmit'),
    path('configuration/cruisetableaddcancel', views.cruisetableaddcancel, name='cruisetableaddcancel'), 
    path('configuration/<int:cruise_pk>/cruisetabledelete', views.cruisetabledelete, name='cruisetabledelete'),
    path('configuration/<int:cruise_pk>/cruisetableedit', views.cruisetableedit, name='cruisetableedit'), 
    path('configuration/<int:cruise_pk>/cruisetableeditsubmit', cruisetableeditsubmit, name='cruisetableeditsubmit'),
    path('configuration/operatorlist/', OperatorList.as_view(), name='operatorlist'),
    path('configuration/operator/<int:pk>/operatordetail', OperatorDetail.as_view(), name='operatordetail'),
    path('configuration/operator/<int:pk>/edit/', OperatorEdit.as_view(), name='operatoredit'),
    path('configuration/operator/<int:id>/editstatus/', views.operatoreditstatus, name='operatoreditstatus'),
    path('configuration/operatoradd/', views.operatoradd, name='operatoradd'),
    path('configuration/operatortablelistget', operatortablelistget, name='operatortablelistget'),
    path('configuration/operatortableadd', views.operatortableadd, name='operatortableadd'),
    path('configuration/operatortableaddsubmit', views.operatortableaddsubmit, name='operatortableaddsubmit'),
    path('configuration/operatortableaddcancel', views.operatortableaddcancel, name='operatortableaddcancel'), 
    path('configuration/<int:winchoperator_pk>/operatortabledelete', views.operatortabledelete, name='operatortabledelete'),
    path('configuration/<int:winchoperator_pk>/operatortableedit', views.operatortableedit, name='operatortableedit'), 
    path('configuration/<int:winchoperator_pk>/operatortableeditsubmit', operatortableeditsubmit, name='operatortableeditsubmit'), 
    path('configuration/deploymentlist/', DeploymentList.as_view(), name='deploymentlist'),
    path('configuration/deployment/<int:pk>/deploymentdetail', DeploymentDetail.as_view(), name='deploymentdetail'),
    path('configuration/deployment/<int:pk>/edit/', DeploymentEdit.as_view(), name='deploymentedit'),
    path('configuration/deployment/<int:id>/editstatus/', views.deploymenteditstatus, name='deploymenteditstatus'),
    path('configuration/deploymentadd/', views.deploymentadd, name='deploymentadd'),
    path('configuration/deploymenttablelistget', deploymenttablelistget, name='deploymenttablelistget'),
    path('configuration/deploymenttableadd', views.deploymenttableadd, name='deploymenttableadd'),
    path('configuration/deploymenttableaddsubmit', views.deploymenttableaddsubmit, name='deploymenttableaddsubmit'),
    path('configuration/deploymenttableaddcancel', views.deploymenttableaddcancel, name='deploymenttableaddcancel'), 
    path('configuration/<int:deployment_pk>/deploymenttabledelete', views.deploymenttabledelete, name='deploymenttabledelete'),
    path('configuration/<int:deployment_pk>/deploymenttableedit', views.deploymenttableedit, name='deploymenttableedit'), 
    path('configuration/<int:deployment_pk>/deploymenttableeditsubmit', views.deploymenttableeditsubmit, name='deploymenttableeditsubmit'),
    path('configuration/winchtablelistget', winchtablelistget, name='winchtablelistget'),
    path('configuration/winchtableadd', views.winchtableadd, name='winchtableadd'),
    path('configuration/winchtableaddsubmit', views.winchtableaddsubmit, name='winchtableaddsubmit'),
    path('configuration/winchtableaddcancel', views.winchtableaddcancel, name='winchtableaddcancel'), 
    path('configuration/<int:winch_pk>/winchtabledelete', views.winchtabledelete, name='winchtabledelete'),
    path('configuration/<int:winch_pk>/winchtableedit', views.winchtableedit, name='winchtableedit'), 
    path('configuration/<int:winch_pk>/winchtableeditsubmit', winchtableeditsubmit, name='winchtableeditsubmit'),
    path('configuration/swttablelistget', swttablelistget, name='swttablelistget'),
    path('configuration/swttableadd', views.swttableadd, name='swttableadd'),
    path('configuration/swttableaddsubmit', views.swttableaddsubmit, name='swttableaddsubmit'),
    path('configuration/swttableaddcancel', views.swttableaddcancel, name='swttableaddcancel'), 
    path('configuration/<int:wire_pk>/swttabledelete', views.swttabledelete, name='swttabledelete'),
    path('configuration/<int:wire_pk>/swttableedit', views.swttableedit, name='swttableedit'), 
    path('configuration/<int:wire_pk>/swttableeditsubmit', swttableeditsubmit, name='swttableeditsubmit'),

    #URLS related to inventories 
    path('inventories/wire/<int:pk>/wiredetail', WireDetail.as_view(), name='wiredetail'),
    path('inventories/wire/<int:id>/edit/', views.wireedit, name='wireedit'),
    path('inventories/wire/<int:id>/editfactorofsafety/', views.wireeditfactorofsafety, name='wireeditfactorofsafety'),
    path('inventories/wireadd/', views.wireadd, name='wireadd'),
    path('inventories/<int:id>/wiredelete', views.wiredelete, name='wiredelete'),
    path('inventories/wirelist/', views.wirelist, name='wirelist'),
    path('inventories/winch/<int:pk>/winchdetail', WinchDetail.as_view(), name='winchdetail'),
    path('inventories/winch/<int:pk>/edit/', WinchEdit.as_view(), name='winchedit'),
    path('inventories/winch/<int:id>/editstatus/', views.wincheditstatus, name='wincheditstatus'),
    path('inventories/winchadd/', views.winchadd, name='winchadd'),
    path('inventories/winchlist/', WinchList.as_view(), name='winchlist'),
    path('inventories/wireropedatalist/', views.wireropedatalist, name='wireropedatalist'),
    path('inventories/wireropedata/<int:id>/edit/', views.wireropedataedit, name='wireropedataedit'),
    path('inventories/wireropedataadd/', views.wireropedataadd, name='wireropedataadd'),
    path('inventories/<int:id>/wireropedatadelete', views.wireropedatadelete, name='wireropedatadelete'),
    path('inventories/wirelocationadd/', views.wirelocationadd, name='wirelocationadd'),
    path('inventories/wirelocation/<int:id>/edit/', views.wirelocationedit, name='wirelocationedit'),
    path('inventories/<int:id>/wirelocationdelete', views.wirelocationdelete, name='wirelocationdelete'),
    path('inventories/wirelocationlist/', views.wirelocationlist, name='wirelocationlist'),
    path('inventories/locationadd/', views.locationadd, name='locationadd'),
    path('inventories/location/<int:id>/edit/', views.locationedit, name='locationedit'),
    path('inventories/<int:id>/locationdelete', views.locationdelete, name='locationdelete'),
    path('inventories/locationlist/', views.locationlist, name='locationlist'),




    #URLS related to maintenance
    path('maintenance/breaktestlist/', views.breaktestlist, name='breaktestlist'),
    path('maintenance/cutbackreterminationlist/', views.cutbackreterminationlist, name='cutbackreterminationlist'),
    path('maintenance/cutbackretermination/<int:pk>/deploymentdetail', CutbackReterminationDetail.as_view(), name='cutbackreterminationdetail'),
    path('maintenance/cutbackretermination/<int:id>/edit/', views.cutbackreterminationedit, name='cutbackreterminationedit'),
    path('maintenance/cutbackreterminationadd/', views.cutbackreterminationadd, name='cutbackreterminationadd'),
    path('maintenance/<int:pk>/delete/', CutbackreterminationDelete.as_view(), name='cutbackreterminationdelete'),
    path('maintenance/breaktestadd/', views.breaktestadd, name='breaktestadd'),
    path('maintenance/breaktest/<int:id>/edit/', views.breaktestedit, name='breaktestedit'),
    path('maintenance/breaktestlist', views.breaktestlist, name='breaktestlist'),
    path('maintenance/breaktest/<int:pk>/breaktestdetail', views.breaktestdetail, name='breaktestdetail'),
    path('maintenance/breaktest/<int:pk>/delete/', BreaktestDelete.as_view(), name='Breaktestdelete'),
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
    path('reports/charts/', charts, name='charts'),
]