import React, { useState, useEffect } from 'react';
import './App.css';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { Icon } from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Slider } from '@mui/material';
import Papa from 'papaparse';

// Default marker icon
const defaultIcon = new Icon({
  iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png'
});

// Add this function to convert slider value to date
function valueToDate(value) {
  const startDate = new Date('2023-09-20');
  const date = new Date(startDate);
  date.setDate(startDate.getDate() + value);
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

// Component to show location details when a marker is clicked
function LocationDetails({ location }) {
  if (!location) return null;
  
  return (
    <div style={{ marginTop: '1em', padding: '1em', backgroundColor: '#f0f0f0', borderRadius: '8px' }}>
      <h3>Location Details</h3>
      <p><strong>Name:</strong> {location.name}</p>
      <p><strong>Coordinates:</strong> {location.position[0]}, {location.position[1]}</p>
    </div>
  );
}

// Main map component
function StormMap() {
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [dateValue, setDateValue] = useState(0);
  const [events, setEvents] = useState([]);

  // Load CSV data on component mount
  useEffect(() => {
    const loadCSV = async () => {
      try {
        const response = await fetch('/events.csv'); // Make sure your CSV is in the public folder
        const reader = response.body.getReader();
        const result = await reader.read();
        const decoder = new TextDecoder('utf-8');
        const csvData = decoder.decode(result.value);
        
        Papa.parse(csvData, {
          header: true,
          complete: (results) => {
            // Assuming your CSV has columns: id, name, latitude, longitude, date
            const formattedEvents = results.data.map(event => ({
              id: event.id,
              name: event.name,
              position: [parseFloat(event.latitude), parseFloat(event.longitude)],
              date: new Date(event.date)
            })).filter(event => event.position[0] && event.position[1]); // Filter out any invalid coordinates
            
            setEvents(formattedEvents);
          }
        });
      } catch (error) {
        console.error('Error loading CSV:', error);
      }
    };

    loadCSV();
  }, []);

  // Filter events based on selected date
  const filteredEvents = events.filter(event => {
    const eventDate = event.date;
    const selectedDate = new Date('2023-09-20');
    selectedDate.setDate(selectedDate.getDate() + dateValue);
    
    // Show all events up to and including the selected date
    return eventDate <= selectedDate;
  });

  return (
    <div>
      <div style={{ width: '80%', margin: '20px auto' }}>
        <Slider
          value={dateValue}
          min={0}
          max={32} // 32 days between Sept 20 and Oct 22
          onChange={(_, newValue) => setDateValue(newValue)}
          valueLabelDisplay="auto"
          valueLabelFormat={(value) => valueToDate(value)}
          marks={[
            { value: 0, label: 'Sept 20' },
            { value: 32, label: 'Oct 22' }
          ]}
        />
      </div>
      <div style={{ height: '400px', width: '100%', maxWidth: '800px', position: 'relative' }}>
        <MapContainer 
          center={[28.5384, -81.3789]}
          zoom={13} 
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          />
          
          {filteredEvents.map(event => (
            <Marker 
              key={event.id}
              position={event.position} 
              icon={defaultIcon}
              eventHandlers={{
                click: () => setSelectedLocation(event),
              }}
            >
              <Popup>{event.name}</Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>
      <LocationDetails location={selectedLocation} />
    </div>
  );
}

// Main app component
function App() {
  return (
    <div className="App" style={{ textAlign: 'center', height: '100vh', padding: '20px', backgroundColor: '#eaeaea' }}>
      <header style={{ paddingBottom: '1em' }}>
        <h1>Hurricane Helene News Tracker</h1>
      </header>
      <StormMap />
    </div>
  );
}

export default App;

