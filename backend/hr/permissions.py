from rest_framework.permissions import BasePermission


class IsOfficeAdmin(BasePermission):
    message = 'this allowed only for office Admin'

    def has_permission(self, request, view):
        try:
            role = request.user.role
            if role and role.name == 'Admin':
                office = request.user.office
                if office and (str(office.id) == view.kwargs['office_id']):
                    return True

        except:
            pass
        return False