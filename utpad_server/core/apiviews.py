import io
import os
import tempfile
import time
import zipfile

import pandas as pd
from django.http import FileResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

import utpad_server.settings
from utpad_server.dataload import model_name_map, serializer_map, save_data_to_folder, load_data_from_folder


# noinspection PyTypeChecker
@swagger_auto_schema(
    method='get',
    operation_description="Retrieve details of the currently authenticated user.",
    responses={
        200: openapi.Response(
            description="User details retrieved successfully.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='User ID'),
                    'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
                    'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='First Name'),
                    'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Last Name'),
                    'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email Address'),
                    'is_staff': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Is Staff'),
                    'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Is Active'),
                    'date_joined': openapi.Schema(type=openapi.FORMAT_DATETIME, description='Date Joined'),
                    'last_login': openapi.Schema(type=openapi.FORMAT_DATETIME, description='Last Login'),
                    'is_superuser': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Is Superuser'),
                    'groups': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Items(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Group ID'),
                                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Group Name'),
                            }
                        ),
                        description='List of groups the user belongs to'
                    ),
                    'user_permissions': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Items(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Permission ID'),
                                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Permission Name'),
                                'codename': openapi.Schema(type=openapi.TYPE_STRING, description='Permission Codename'),
                            }
                        ),
                        description='List of user permissions'
                    ),
                }
            )
        ),
        401: "Authentication Required",
        405: "Method Not Allowed"
    }
)
@api_view(['GET'])
def get_user_profile_details(request):
    if not request.method == 'GET':
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if not request.user or not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    user = request.user
    user_details = {
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'is_staff': user.is_staff,
        'is_active': user.is_active,
        'date_joined': user.date_joined,
        'last_login': user.last_login,
        'is_superuser': user.is_superuser,
        'groups': [{'id': group.id, 'name': group.name} for group in user.groups.all()],
        'user_permissions': [{'id': perm.id, 'name': perm.name, 'codename': perm.codename} for perm in
                             user.user_permissions.all()],
    }

    return Response(user_details)


class ExportZIPDataView(APIView):
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        operation_description="Export all application data as a ZIP file. Only accessible by superusers.",
        responses={
            200: openapi.Response(
                description="Data exported successfully.",
                schema=openapi.Schema(
                    type=openapi.TYPE_FILE,
                    format='binary',
                    description='ZIP file containing exported data'
                )
            ),
            401: "Authentication Required",
            403: "Permission Denied",
            405: "Method Not Allowed"
        }
    )
    def get(self, request, *args, **kwargs):
        if not request.method == 'GET':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

        if not request.user or not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        if not request.user.is_superuser:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        zip_path = os.path.join(utpad_server.settings.MEDIA_BASE_NAME, f'exported_data_{int(time.time())}.zip')

        with tempfile.TemporaryDirectory() as temp_dir:
            save_data_to_folder(temp_dir)

            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arcname)
        response = FileResponse(open(zip_path, 'rb'), as_attachment=True, filename=os.path.basename(zip_path),
                                content_type='application/zip')
        return response


class ImportZIPDataView(APIView):
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        operation_description="Import application data from an uploaded ZIP file. Only accessible by superusers.",
        manual_parameters=[
            openapi.Parameter(
                name='file',
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                description='ZIP file containing data to import',
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Data imported successfully.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(type=openapi.TYPE_STRING, description='Import status message')
                    }
                )
            ),
            400: "Bad Request - No file provided",
            401: "Authentication Required",
            403: "Permission Denied",
            405: "Method Not Allowed"
        }
    )
    def post(self, request, *args, **kwargs):
        if not request.method == 'POST':
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

        if not request.user or not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        if not request.user.is_superuser:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        if 'file' not in request.FILES:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        uploaded_file = request.FILES['file']

        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = os.path.join(temp_dir, 'imported_data.zip')
            with open(zip_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            with zipfile.ZipFile(zip_path, 'r') as zipf:
                zipf.extractall(temp_dir)

            load_data_from_folder(temp_dir)

        return Response({'status': 'Data imported successfully'})


@swagger_auto_schema(
    method='get',
    operation_description="Export all application data as an Excel file. Only accessible by superusers.",
    responses={
        200: openapi.Response(
            description="Data exported successfully.",
            schema=openapi.Schema(
                type=openapi.TYPE_FILE,
                format='binary',
                description='Excel file containing exported data'
            )
        ),
        401: "Authentication Required",
        403: "Permission Denied",
        405: "Method Not Allowed"
    }
)
@api_view(['GET'])
def export_all_data_as_excel(request):
    if not request.method == 'GET':
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if not request.user or not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    if not request.user.is_superuser:
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

    excel_buffer = io.BytesIO()

    # noinspection PyTypeChecker
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        for app_label, models in model_name_map.items():
            for model_name, model_class in models.items():
                queryset = model_class.objects.all()
                serializer_cls = serializer_map.get(model_class)
                if serializer_cls:
                    serializer = serializer_cls(queryset, many=True, expand_relation_as_object=False)
                    df = pd.DataFrame(serializer.data)
                    if not df.empty:
                        df.to_excel(writer, sheet_name=f"{app_label}_{model_name}"[:31], index=False)

    excel_buffer.seek(0)

    response = FileResponse(excel_buffer, as_attachment=True, filename='exported_data.xlsx',
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="exported_data.xlsx"'

    return response
