from rest_framework.permissions import BasePermission, SAFE_METHODS



class IsCompany(BasePermission):
    """
    Only company-role users can access this endpoint
    """
    message = 'Only company accounts can perform this action.'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.is_company
        )
    
class IsCandidate(BasePermission):
    """
    Only Candidate-role users can access this endpoint
    """
    message = 'Only candidate accounts can perform this action.'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.is_candidate
        )
    
class IsCompanyOrReadOnly(BasePermission):
    """
    GET requests → anyone can access.
    POST/PUT/PATCH/DELETE → only company users.
    """
    message = 'Only company accounts can modify this resource.'

    def has_permission(self, request, view):
        # SAFE_METHODS = ( 'GET', 'HEAD', 'OPTIONS')
        if request.method in SAFE_METHODS:
            return True
        return(
            request.user.is_authenticated and
            request.user.is_company
        )
    
class IsOwnerOrReadOnly(BasePermission):
    """
    GET requests → anyone can access.
    PUT/PATCH/DELETE → only the company that owns this job.
    """
    message = 'You can only modify your own resources.'

    def has_permission(self, request, view):
        # view-level: allow read always, write requires auth
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # object-level : read always allowed
        if request.method in SAFE_METHODS:
            return True
        
        # write: only the company that owns the job
        # obj is the JobListing instance
        return obj.company.user == request.user
    
class IsAdminOrReadOnly(BasePermission):
    """
    GET requests → anyone.
    Everything else → admin only.
    """
    message = 'Only admins can perform this action.'

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return (
            request.user.is_authticated and
            request.user.is_admin
        )

