// Configuration
const API_URL = '/api/bus-info';
const SYSTEM_STATUS_URL = '/api/system-status';
const REFRESH_INTERVAL = 60000; // 1 minute in milliseconds

// DOM Elements
const busInfoContainer = document.getElementById('bus-info-container');
const updateTimeElement = document.getElementById('update-time');
const systemStatusElement = document.getElementById('system-status');
const busCardTemplate = document.getElementById('bus-card-template');

// State
let busData = [];
let lastUpdateTime = null;
let updateTimer = null;
let countdownIntervals = [];

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    fetchBusData();
    
    // Set up regular refresh
    updateTimer = setInterval(fetchBusData, REFRESH_INTERVAL);
    
    // Set up visibility change detection (to pause/resume when tab is inactive)
    document.addEventListener('visibilitychange', handleVisibilityChange);
}

function handleVisibilityChange() {
    if (document.hidden) {
        // Pause countdown timers when tab is not visible
        clearCountdownIntervals();
    } else {
        // Refresh data and restart countdown when tab becomes visible again
        fetchBusData();
    }
}

async function fetchBusData() {
    try {
        // Show loading state if this is the first load
        if (!lastUpdateTime) {
            busInfoContainer.innerHTML = '<div class="loading">データを読み込み中...</div>';
        }
        
        // Fetch the bus data
        const response = await fetch(API_URL);
        
        if (!response.ok) {
            throw new Error(`API responded with status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Update the UI
        updateBusInfo(data);
        updateSystemStatus(data.system_status);
        
        // Update last update time
        lastUpdateTime = data.update_time;
        updateTimeElement.textContent = formatTime(lastUpdateTime);
        
    } catch (error) {
        console.error('Error fetching bus data:', error);
        systemStatusElement.textContent = 'エラー - データを取得できません';
        systemStatusElement.style.color = 'red';
    }
}

function updateBusInfo(data) {
    // Clear existing content and intervals
    busInfoContainer.innerHTML = '';
    clearCountdownIntervals();
    
    // No destinations data
    if (!data.destinations || data.destinations.length === 0) {
        busInfoContainer.innerHTML = '<div class="loading">バス情報がありません</div>';
        return;
    }
    
    // Save data for reference
    busData = data.destinations;
    
    // Create and append bus cards
    busData.forEach(bus => {
        const busCard = createBusCard(bus);
        busInfoContainer.appendChild(busCard);
    });
    
    // Start countdown timers
    startCountdowns();
}

function createBusCard(bus) {
    // Clone template
    const card = document.importNode(busCardTemplate.content, true).querySelector('.bus-card');
    
    // Set bus information
    card.querySelector('.destination').textContent = bus.destination;
    card.querySelector('.bus-number').textContent = bus.bus_number;
    card.querySelector('.countdown').textContent = formatMinutes(bus.estimated_departure_minutes);
    card.querySelector('.scheduled-departure').textContent = bus.scheduled_departure_time || '--:--';
    card.querySelector('.scheduled-arrival').textContent = bus.scheduled_arrival_time || '--:--';
    card.querySelector('.stop-number').textContent = bus.stop_number || '-';
    
    // Set status
    const statusElement = card.querySelector('.bus-status');
    statusElement.dataset.status = bus.delay_status || 'unknown';
    
    const statusText = getStatusText(bus.delay_status);
    card.querySelector('.status-text').textContent = statusText;
    
    // Add data attributes for countdown
    card.dataset.minutes = bus.estimated_departure_minutes;
    card.dataset.destination = bus.destination;
    
    return card;
}

function startCountdowns() {
    // Get all bus cards
    const busCards = document.querySelectorAll('.bus-card');
    
    // Start a countdown for each card
    busCards.forEach(card => {
        const countdownElement = card.querySelector('.countdown');
        let minutes = parseInt(card.dataset.minutes, 10);
        
        if (isNaN(minutes)) return;
        
        const interval = setInterval(() => {
            // Decrement minutes (every 60 seconds)
            if (minutes > 0) {
                minutes--;
                countdownElement.textContent = formatMinutes(minutes);
                
                // Update card data attribute
                card.dataset.minutes = minutes;
                
                // Change color when time is running out
                if (minutes <= 5) {
                    countdownElement.style.color = 'red';
                }
            } else {
                // When countdown reaches zero, clear the interval and mark as "発車済み"
                clearInterval(interval);
                countdownElement.textContent = '発車済み';
                countdownElement.style.color = '#999';
            }
        }, 60000); // Update every minute
        
        countdownIntervals.push(interval);
    });
}

function clearCountdownIntervals() {
    countdownIntervals.forEach(interval => clearInterval(interval));
    countdownIntervals = [];
}

function updateSystemStatus(status) {
    if (!status) return;
    
    let statusText = '正常';
    let statusColor = 'green';
    
    if (status.health === 'DEGRADED') {
        statusText = '低下';
        statusColor = 'orange';
    } else if (status.health === 'ERROR') {
        statusText = '障害';
        statusColor = 'red';
    }
    
    systemStatusElement.textContent = statusText;
    systemStatusElement.style.color = statusColor;
}

// Helper Functions
function formatTime(timeString) {
    if (!timeString) return '--:--';
    
    try {
        const date = new Date(timeString);
        return date.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' });
    } catch (e) {
        return timeString; // Return as-is if parsing fails
    }
}

function formatMinutes(minutes) {
    if (!minutes && minutes !== 0) return '--分';
    return `${minutes}分`;
}

function getStatusText(status) {
    switch (status) {
        case 'ON_TIME':
            return '定刻通り';
        case 'DELAYED':
            return '遅延';
        case 'EARLY':
            return '早発';
        default:
            return '不明';
    }
}