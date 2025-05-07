import json
from app.models.bus_info import BusInfo
from datetime import datetime, timedelta

def test_get_bus_info_empty(client):
    """Test the bus info API with no data"""
    response = client.get('/api/bus-info')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'update_time' in data
    assert 'system_status' in data
    assert 'destinations' in data
    assert len(data['destinations']) == 0

def test_get_bus_info_with_data(client, app):
    """Test the bus info API with sample data"""
    with app.app_context():
        # Create test data
        now = datetime.now()
        
        for i, dest in enumerate(['三鷹駅', '吉祥寺駅', '武蔵境駅南口', '調布駅北口']):
            bus = BusInfo(
                destination=dest,
                bus_number=f'バス{i+1}',
                stop_number=str(i+1),
                scheduled_departure_time=now + timedelta(minutes=15),
                predicted_departure_time=now + timedelta(minutes=18),
                scheduled_arrival_time=now + timedelta(minutes=35),
                predicted_arrival_time=now + timedelta(minutes=38),
                estimated_departure_minutes=18,
                is_next_bus=True,
                is_active=True
            )
            BusInfo.query.session.add(bus)
        
        BusInfo.query.session.commit()
    
    # Test API response
    response = client.get('/api/bus-info')
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert 'destinations' in data
    assert len(data['destinations']) == 4
    
    # Check first destination
    first_dest = data['destinations'][0]
    assert 'destination' in first_dest
    assert 'bus_number' in first_dest
    assert 'scheduled_departure_time' in first_dest
    assert 'delay_status' in first_dest

def test_system_status(client):
    """Test the system status API"""
    response = client.get('/api/system-status')
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert 'status' in data
    assert 'last_update' in data
    assert 'health' in data