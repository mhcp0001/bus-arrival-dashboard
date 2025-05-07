from datetime import datetime, timedelta
from app import db
from sqlalchemy import desc

class BusInfo(db.Model):
    """Bus information model"""
    
    id = db.Column(db.Integer, primary_key=True)
    destination = db.Column(db.String(64), nullable=False)
    bus_number = db.Column(db.String(16), nullable=False)
    stop_number = db.Column(db.String(8), nullable=True)
    scheduled_departure_time = db.Column(db.DateTime, nullable=True)
    predicted_departure_time = db.Column(db.DateTime, nullable=True)
    scheduled_arrival_time = db.Column(db.DateTime, nullable=True)
    predicted_arrival_time = db.Column(db.DateTime, nullable=True)
    estimated_departure_minutes = db.Column(db.Integer, nullable=True)
    is_next_bus = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    @classmethod
    def get_latest_active(cls):
        """
        Get the latest active bus info for each destination
        """
        # The list of destinations from the spec
        destinations = ["三鷹駅", "吉祥寺駅", "武蔵境駅南口", "調布駅北口"]
        
        results = []
        for destination in destinations:
            # Get the latest active record for each destination
            bus = cls.query.filter_by(
                destination=destination,
                is_active=True
            ).order_by(desc(cls.created_at)).first()
            
            if bus:
                results.append(bus)
        
        return results
    
    @classmethod
    def get_history(cls, hours=24):
        """
        Get historical bus information from the past X hours
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        return cls.query.filter(
            cls.created_at >= cutoff_time
        ).order_by(desc(cls.created_at)).all()
    
    @classmethod
    def deactivate_all(cls):
        """
        Deactivate all currently active bus info
        """
        active_buses = cls.query.filter_by(is_active=True).all()
        for bus in active_buses:
            bus.is_active = False
        
        db.session.commit()
    
    def to_dict(self):
        """
        Convert the model to a dictionary for API response
        """
        # Calculate delay status
        delay_status = "ON_TIME"
        if self.predicted_departure_time and self.scheduled_departure_time:
            delay = (self.predicted_departure_time - self.scheduled_departure_time).total_seconds() / 60
            if delay > 5:
                delay_status = "DELAYED"
            elif delay < -5:
                delay_status = "EARLY"
        
        return {
            "destination": self.destination,
            "bus_number": self.bus_number,
            "stop_number": self.stop_number,
            "scheduled_departure_time": self.scheduled_departure_time.strftime("%H:%M") if self.scheduled_departure_time else None,
            "predicted_departure_time": self.predicted_departure_time.strftime("%H:%M") if self.predicted_departure_time else None,
            "scheduled_arrival_time": self.scheduled_arrival_time.strftime("%H:%M") if self.scheduled_arrival_time else None,
            "predicted_arrival_time": self.predicted_arrival_time.strftime("%H:%M") if self.predicted_arrival_time else None,
            "estimated_departure_minutes": self.estimated_departure_minutes,
            "is_next_bus": self.is_next_bus,
            "delay_status": delay_status
        }