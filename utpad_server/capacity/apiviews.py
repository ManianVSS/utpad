from datetime import datetime, timedelta

import numpy
from django.http import HttpResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import OrgGroup, Engineer, SiteHoliday, Leave, EngineerOrgGroupParticipation
from .serializers import SiteHolidaySerializer, LeaveSerializer

# TODO: Consider making work days configurable per org group or site
WORK_DAYS_MASK = [1, 1, 1, 1, 1, 0, 0]


def get_capacity_data_for_org_group(org_group, from_date, to_date):
    work_days = numpy.busday_count(from_date,
                                   to_date + timedelta(days=1),
                                   weekmask=WORK_DAYS_MASK
                                   )

    org_group_participation_qs = EngineerOrgGroupParticipation.objects.filter(org_group=org_group)

    total_capacity = 0
    engineer_data = {}
    for org_group_participation in org_group_participation_qs:
        engineer = org_group_participation.engineer
        engineer_leave_plans = Leave.objects.filter(engineer=engineer,
                                                    start_date__gte=from_date, start_date__lte=to_date,
                                                    end_date__gte=from_date, end_date__lte=to_date)
        engineer_site_holidays = SiteHoliday.objects.filter(site=engineer.site,
                                                            date__gte=from_date,
                                                            date__lte=to_date)
        engineer_site_holidays_dates = [item.date for item in engineer_site_holidays]
        leave_count = 0
        for engineer_leave in engineer_leave_plans:
            leave_count = leave_count + numpy.busday_count(engineer_leave.start_date,
                                                           engineer_leave.end_date + timedelta(days=1),
                                                           weekmask=WORK_DAYS_MASK,
                                                           holidays=engineer_site_holidays_dates)
        site_holiday_count = len(engineer_site_holidays_dates)
        available_days = work_days - leave_count - site_holiday_count
        capacity = available_days * org_group_participation.capacity
        total_capacity = total_capacity + capacity
        engineer_data[engineer.employee_id] = {'employee_id': engineer.employee_id,
                                               'name': engineer.auth_user.username,
                                               'leave_plans': LeaveSerializer(engineer_leave_plans, many=True).data,
                                               'site_holidays': SiteHolidaySerializer(engineer_site_holidays,
                                                                                      many=True).data,
                                               'engineer_site_holidays_dates': engineer_site_holidays_dates,
                                               'leave_count': leave_count,
                                               'site_holiday_count': site_holiday_count,
                                               'available_days': available_days,
                                               'participation_capacity': org_group_participation.capacity,
                                               'capacity': capacity,
                                               }

    capacity_data = {
        'work_days': work_days,
        'total_capacity': total_capacity,
        'engineer_data': engineer_data,
    }

    return capacity_data


@swagger_auto_schema(
    method='get',
    operation_description="Get capacity data for an org group and its transitive sub-groups for a time range",
    manual_parameters=[
        openapi.Parameter('org_group', openapi.IN_QUERY, description="Org group ID", type=openapi.TYPE_INTEGER,
                          required=True),
        openapi.Parameter('from', openapi.IN_QUERY, description="From date (yyyy-mm-dd)", type=openapi.TYPE_STRING,
                          required=True),
        openapi.Parameter('to', openapi.IN_QUERY, description="To date (yyyy-mm-dd)", type=openapi.TYPE_STRING,
                          required=True),
    ],
    responses={
        200: 'Capacity data returned',
        400: 'One of the parameters (org_group/from/to) missing',
        404: 'Could not find org_group passed',
        405: 'Method not allowed'
    }
)
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_org_capacity_for_time_range(request):
    if not request.method == 'GET':
        return HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if not (('org_group' in request.GET) and ('from' in request.GET) and ('to' in request.GET)):
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST,
                            content='One of the parameters (org_group/from/to) missing')

    try:
        org_group = OrgGroup.objects.get(pk=request.query_params.get('org_group'))
    except OrgGroup.DoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND, content='Could not find org_group passed')

    from_date = datetime.strptime(request.query_params.get('from'), '%Y-%m-%d').date()
    to_date = datetime.strptime(request.query_params.get('to'), '%Y-%m-%d').date()

    capacity_data_for_org_groups = {org_group.name: get_capacity_data_for_org_group(org_group, from_date, to_date)}

    for transitive_sub_group_id in org_group.get_transitive_sub_groups():
        transitive_sub_group = OrgGroup.objects.get(id=transitive_sub_group_id)
        capacity_data_for_org_groups[transitive_sub_group.name] = get_capacity_data_for_org_group(transitive_sub_group,
                                                                                                  from_date, to_date)

    return Response(capacity_data_for_org_groups)


@swagger_auto_schema(
    method='get',
    operation_description="Get capacity data for an engineer for a time range",
    manual_parameters=[
        openapi.Parameter('engineer', openapi.IN_QUERY, description="Engineer ID", type=openapi.TYPE_INTEGER,
                          required=True),
        openapi.Parameter('from', openapi.IN_QUERY, description="From date (yyyy-mm-dd)", type=openapi.TYPE_STRING,
                          required=True),
        openapi.Parameter('to', openapi.IN_QUERY, description="To date (yyyy-mm-dd)", type=openapi.TYPE_STRING,
                          required=True),
    ],
    responses={
        200: 'Capacity data returned',
        400: 'One of the parameters (engineer/from/to) missing',
        404: 'Could not find engineer passed',
        405: 'Method not allowed'
    }
)
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def get_engineer_capacity_for_time_range(request):
    if not request.method == 'GET':
        return HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if not (('engineer' in request.GET) and ('from' in request.GET) and ('to' in request.GET)):
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST,
                            content='One of the parameters (engineer/from/to) missing')

    try:
        engineer = Engineer.objects.get(pk=request.query_params.get('engineer'))
    except Engineer.DoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND, content='Could not find engineer passed')

    from_date = datetime.strptime(request.query_params.get('from'), '%Y-%m-%d').date()
    to_date = datetime.strptime(request.query_params.get('to'), '%Y-%m-%d').date()

    org_group_participation_qs = EngineerOrgGroupParticipation.objects.filter(engineer=engineer)

    work_days = numpy.busday_count(from_date,
                                   to_date + timedelta(days=1),
                                   weekmask=WORK_DAYS_MASK
                                   )

    engineer_leave_plans = Leave.objects.filter(engineer=engineer,
                                                start_date__gte=from_date, start_date__lte=to_date,
                                                end_date__gte=from_date, end_date__lte=to_date)
    engineer_site_holidays = SiteHoliday.objects.filter(site=engineer.site,
                                                        date__gte=from_date,
                                                        date__lte=to_date)
    engineer_site_holidays_dates = [item.date for item in engineer_site_holidays]
    leave_count = 0
    for engineer_leave in engineer_leave_plans:
        leave_count = leave_count + numpy.busday_count(engineer_leave.start_date,
                                                       engineer_leave.end_date + timedelta(days=1),
                                                       weekmask=WORK_DAYS_MASK,
                                                       holidays=engineer_site_holidays_dates)
    site_holiday_count = len(engineer_site_holidays_dates)
    available_days = work_days - leave_count - site_holiday_count

    org_capacity_data = {}
    for org_group_participation in org_group_participation_qs:
        org_group = org_group_participation.org_group
        participation_capacity = org_group_participation.capacity
        capacity = participation_capacity * available_days
        org_capacity_data[org_group.name] = {
            'name': org_group.name,
            'participation_capacity': participation_capacity,
            'capacity': capacity,
        }

    capacity_data = {
        'work_days': work_days,
        'employee_id': engineer.employee_id,
        'name': engineer.auth_user.username,
        'leave_plans': LeaveSerializer(engineer_leave_plans, many=True).data,
        'engineer_site_holidays_dates': engineer_site_holidays_dates,
        'leave_count': leave_count,
        'site_holidays': SiteHolidaySerializer(engineer_site_holidays,
                                               many=True).data,
        'site_holiday_count': site_holiday_count,
        'available_days': available_days,
        'org_capacity_data': org_capacity_data,
    }

    return Response(capacity_data)
