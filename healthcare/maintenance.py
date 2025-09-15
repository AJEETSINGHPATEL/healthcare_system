"""
Maintenance mode configuration for the healthcare system.
This module contains functions to control system access during maintenance.
"""

def is_maintenance_mode():
    """
    Check if the system is in maintenance mode (login disabled).
    
    Returns:
        bool: True if maintenance mode is active, False otherwise.
    
    To enable login: Change return value to False
    To disable login: Change return value to True
    """
    return False  # Set to False to enable logins

def get_maintenance_message():
    """
    Get the maintenance mode message.
    
    Returns:
        str: Maintenance mode message
    """
    if is_maintenance_mode():
        return 'System is currently in maintenance mode. User login and registration are disabled.'
    return ''

def get_maintenance_status():
    """
    Get the current maintenance mode status.
    
    Returns:
        dict: Dictionary containing maintenance mode status and message
    """
    return {
        'maintenance_mode': is_maintenance_mode(),
        'maintenance_message': get_maintenance_message()
    }
