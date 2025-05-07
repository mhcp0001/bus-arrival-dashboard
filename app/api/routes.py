from flask import jsonify, current_app
from app.api import api_bp
from app.models.bus_info import BusInfo
from datetime import datetime

@api_bp.route('/bus-info', methods=['GET'])
def get_bus_info():
    """
    Get the latest bus information for all destinations
    """
    try:
        # Get latest active bus info for each destination
        bus_info = BusInfo.get_latest_active()
        
        # Format the response
        response = {
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "system_status": {
                "data_source": "API",  # This will be updated dynamically in future
                "last_successful_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "health": "OK"
            },
            "destinations": []
        }
        
        # Add destinations to response
        for info in bus_info:
            response["destinations"].append(info.to_dict())
        
        return jsonify(response)
    
    except Exception as e:
        current_app.logger.error(f"Error retrieving bus info: {str(e)}")
        return jsonify({
            "error": "Failed to retrieve bus information",
            "details": str(e)
        }), 500


@api_bp.route('/bus-info/history', methods=['GET'])
def get_bus_history():
    """
    Get historical bus information from the past 24 hours
    """
    try:
        # This will be implemented later
        return jsonify({"message": "History endpoint not yet implemented"})
    
    except Exception as e:
        current_app.logger.error(f"Error retrieving bus history: {str(e)}")
        return jsonify({
            "error": "Failed to retrieve bus history",
            "details": str(e)
        }), 500


@api_bp.route('/system-status', methods=['GET'])
def get_system_status():
    """
    Get the current system status
    """
    try:
        # This will be enhanced later
        return jsonify({
            "status": "operational",
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "uptime": "N/A",
            "data_source": "API",
            "health": "OK"
        })
    
    except Exception as e:
        current_app.logger.error(f"Error retrieving system status: {str(e)}")
        return jsonify({
            "error": "Failed to retrieve system status",
            "details": str(e)
        }), 500