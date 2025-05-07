from app.models.bus_info import BusInfo
from datetime import datetime, timedelta

def test_bus_info_model(app):
    """Test the BusInfo model"""
    with app.app_context():
        # Create test bus info
        now = datetime.now()
        
        bus = BusInfo(
            destination='三鷹駅',
            bus_number='鷹52',
            stop_number='4',
            scheduled_departure_time=now + timedelta(minutes=10),
            predicted_departure_time=now + timedelta(minutes=15),
            scheduled_arrival_time=now + timedelta(minutes=30),
            predicted_arrival_time=now + timedelta(minutes=35),
            estimated_departure_minutes=15,
            is_next_bus=True,
            is_active=True
        )
        
        BusInfo.query.session.add(bus)
        BusInfo.query.session.commit()
        
        # Test retrieval
        saved_bus = BusInfo.query.first()
        assert saved_bus is not None
        assert saved_bus.destination == '三鷹駅'
        assert saved_bus.bus_number == '鷹52'
        assert saved_bus.is_active is True
        
        # Test to_dict
        bus_dict = saved_bus.to_dict()
        assert bus_dict['destination'] == '三鷹駅'
        assert bus_dict['bus_number'] == '鷹52'
        assert 'delay_status' in bus_dict
        
        # Test deactivation
        BusInfo.deactivate_all()
        saved_bus = BusInfo.query.first()
        assert saved_bus.is_active is False
        
        # Test get_latest_active (should now be empty)
        active_buses = BusInfo.get_latest_active()
        assert len(active_buses) == 0
        
        # Reactivate and test again
        saved_bus.is_active = True
        BusInfo.query.session.commit()
        
        active_buses = BusInfo.get_latest_active()
        assert len(active_buses) == 1
        assert active_buses[0].destination == '三鷹駅'