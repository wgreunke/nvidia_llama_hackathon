import React, { useState, useEffect } from 'react';
import './App.css';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { Slider } from '@mui/material';
import Papa from 'papaparse';
import { Icon } from 'leaflet';
import L from 'leaflet';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

// Fix for default icons
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
});

// Custom hurricane icon
const hurricaneIcon = new Icon({
  iconUrl: 'data:image/svg+xml;charset=UTF-8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><path fill="%23000" d="M288 32c0 17.7 14.3 32 32 32h32c17.7 0 32 14.3 32 32s-14.3 32-32 32H32c-17.7 0-32 14.3-32 32s14.3 32 32 32H352c53 0 96-43 96-96s-43-96-96-96H320c-17.7 0-32 14.3-32 32zm64 352c0 17.7 14.3 32 32 32h32c53 0 96-43 96-96s-43-96-96-96H32c-17.7 0-32 14.3-32 32s14.3 32 32 32H416c17.7 0 32 14.3 32 32s-14.3 32-32 32H384c-17.7 0-32 14.3-32 32zM128 512h32c53 0 96-43 96-96s-43-96-96-96H32c-17.7 0-32 14.3-32 32s14.3 32 32 32H160c17.7 0 32 14.3 32 32s-14.3 32-32 32H128c-17.7 0-32 14.3-32 32s14.3 32 32 32z"/></svg>',
  iconSize: [25, 25],
  iconAnchor: [12, 12],
  popupAnchor: [0, -12]
});

// Add this function to convert slider value to date
function valueToDate(value) {
  const baseDate = new Date('2024-09-22');
  const date = new Date(baseDate);
  date.setDate(baseDate.getDate() + value);
  return date.toLocaleDateString();
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
  const [events, setEvents] = useState([]);
  const [dateValue, setDateValue] = useState(0);
  const [selectedEvent, setSelectedEvent] = useState(null);

  // Load and parse CSV
  useEffect(() => {
    const loadCSV = async () => {
      try {
        const response = await fetch('/events.csv');
        const text = await response.text();
        
        Papa.parse(text, {
          header: true,
          complete: (results) => {
            console.log('CSV columns:', Object.keys(results.data[0]));
            console.log('First row data:', results.data[0]);
            
            const formattedEvents = results.data
              .filter(event => event.lat && event.lon)
              .map(event => ({
                id: Math.random().toString(),
                city: event.city,
                state: event.state,
                event: event.event,
                summary: event.summary,
                position: [
                  parseFloat(event.lat),
                  parseFloat(event.lon)
                ],
                date: new Date(event['date-of-event']),
                'event-picture-caption': event['event-picture-caption'],
                'event-picture-link': event['event-picture-link'],
                lat: event.lat,
                lon: event.lon,
                source: event.source,  
                article_url: event.articel_url
              }));
            
            setEvents(formattedEvents);
          }
        });
      } catch (error) {
        console.error('Error loading CSV:', error);
      }
    };

    loadCSV();
  }, []);

  // Filter events based on slider date
  const filteredEvents = events.filter(event => {
    const selectedDate = new Date('2024-09-23');
    selectedDate.setDate(selectedDate.getDate() + dateValue);
    return event.date <= selectedDate;
  });

  return (
    <div>
      <div style={{ width: '100%', maxWidth: '800px', margin: '20px auto' }}>
        <Slider
          value={dateValue}
          min={0}
          max={32}
          onChange={(_, newValue) => setDateValue(newValue)}
          valueLabelDisplay="auto"
          valueLabelFormat={valueToDate}
          marks={[
            { value: 0, label: 'Sept 22' },
            { value: 32, label: 'Oct 22' }
          ]}
        />
      </div>
      
      <div style={{ height: '400px', width: '100%', maxWidth: '800px', margin: '0 auto' }}>
        <MapContainer 
          center={[30.4513, -84.2727]}
          zoom={6} 
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
              icon={hurricaneIcon}
            >
              <Popup>
                <div>
                  <h3>{event.city}, {event.state}</h3>
                  <p><strong>{event.event}</strong></p>
                  <button 
                    onClick={() => setSelectedEvent(event)}
                    style={{
                      background: '#007bff',
                      color: 'white',
                      border: 'none',
                      padding: '5px 10px',
                      borderRadius: '4px',
                      cursor: 'pointer'
                    }}
                  >
                    Details
                  </button>
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>

      {/* Event Details Panel - Now shown below the map */}
      {selectedEvent && (
        <div style={{
          backgroundColor: 'white',
          padding: '20px',
          borderRadius: '8px',
          boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
          maxWidth: '800px',
          width: '90%',
          margin: '20px auto'
        }}>
          <h2>{selectedEvent.city}, {selectedEvent.state}</h2>
          <div style={{ marginBottom: '20px' }}>
            <p><strong>Event Type:</strong> {selectedEvent.event}</p>
            <p><strong>Date:</strong> {selectedEvent.date.toLocaleDateString()}</p>
            <p><strong>Summary:</strong> {selectedEvent.summary}</p>
            <p><strong>Location:</strong> {selectedEvent.lat}, {selectedEvent.lon}</p>
            <p><strong>Source:</strong> {selectedEvent.source}</p>
            <p><strong>Article:</strong> <a href={selectedEvent.article_url} target="_blank" rel="noopener noreferrer">{selectedEvent.article_url}</a></p>
          </div>
          
          {selectedEvent['event-picture-link'] && (
            <div style={{ marginBottom: '15px' }}>
              <img 
                src={selectedEvent['event-picture-link']} 
                alt={selectedEvent['event-picture-caption'] || 'Event image'}
                style={{
                  maxWidth: '100%',
                  height: 'auto',
                  borderRadius: '4px'
                }}
              />
              {selectedEvent['event-picture-caption'] && (
                <p style={{ 
                  fontSize: '0.9em', 
                  fontStyle: 'italic',
                  color: '#666',
                  marginTop: '8px'
                }}>
                  {selectedEvent['event-picture-caption']}
                </p>
              )}
            </div>
          )}
        </div>
      )}

      {/* Debug list of filtered events */}
      
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
