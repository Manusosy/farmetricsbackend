"""
Middleware for audit logging.
"""

import json
from django.utils.deprecation import MiddlewareMixin
from .audit import log_audit_event


class AuditLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to automatically log certain actions.
    """
    
    # Actions that should be logged
    LOGGED_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']
    
    # Paths to exclude from logging
    EXCLUDED_PATHS = [
        '/admin/jsi18n/',
        '/api/docs/',
        '/api/redoc/',
        '/api/schema/',
        '/static/',
        '/media/',
    ]
    
    def process_response(self, request, response):
        """Log request if it matches criteria."""
        # Skip if excluded path
        if any(request.path.startswith(path) for path in self.EXCLUDED_PATHS):
            return response
        
        # Only log successful requests for logged methods
        if (request.method in self.LOGGED_METHODS and 
            200 <= response.status_code < 400):
            
            # Extract action from request path and method
            action = self._determine_action(request, response)
            
            if action:
                try:
                    log_audit_event(
                        action=action,
                        request=request,
                        description=f"{request.method} {request.path}",
                        metadata={
                            'status_code': response.status_code,
                            'content_type': response.get('Content-Type', '')
                        }
                    )
                except Exception:
                    # Don't fail request if audit logging fails
                    pass
        
        return response
    
    def _determine_action(self, request, response):
        """Determine action type from request."""
        path = request.path.lower()
        method = request.method
        
        # Login/Logout
        if '/login' in path and method == 'POST':
            return 'login'
        if '/logout' in path and method == 'POST':
            return 'logout'
        
        # Password change
        if '/password/change' in path and method == 'POST':
            return 'password_change'
        
        # Submit actions
        if '/submit' in path and method == 'POST':
            return 'submit'
        
        # Approve/Reject
        if '/approve' in path and method == 'POST':
            return 'approve'
        if '/reject' in path or '/rejected' in path:
            return 'reject'
        
        # Verify
        if '/verify' in path and method == 'POST':
            return 'verify'
        
        # Merge
        if '/merge' in path and method == 'POST':
            return 'merge'
        
        # Generic CRUD
        if method == 'POST':
            return 'create'
        if method in ['PUT', 'PATCH']:
            return 'update'
        if method == 'DELETE':
            return 'delete'
        
        return None

