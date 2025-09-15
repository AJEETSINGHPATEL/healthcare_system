from .maintenance import get_maintenance_status

def maintenance_mode_processor(request):
    """Add maintenance mode status to all template contexts"""
    status = get_maintenance_status()
    return {
        'maintenance_mode': status['maintenance_mode'],
        'maintenance_message': status['maintenance_message']
    }
