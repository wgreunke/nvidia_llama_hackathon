import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import Papa from 'papaparse';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Custom marker icon
const icon = new L.Icon({
  iconUrl: 'https://leafletjs.com/examples/custom-icons/leaf-red.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

function App() {
  const [events, setEvents] = useState([]);
  const [selectedEvent, setSelectedEvent] = useState(null);

  // Load CSV data
  useEffect(() => {
    fetch("/events.csv")
      .then(response => response.text())
      .then(csvData => {
        Papa.parse(csvData, {
          header: true,
          complete: (result) => {
            setEvents(result.data);
          }
        });
      });
  }, []);

  return (
    <div style={styles.container}>
      <MapContainer 
        center={[40.7128, -74.006]} 
        zoom={12} 
        style={styles.mapContainer}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution="&copy; OpenStreetMap contributors"
        />
        {events.map((event, idx) => (
          <Marker
            key={idx}
            position={[event.lat, event.lon]}
            icon={icon}
            eventHandlers={{
              click: () => setSelectedEvent(event),
            }}
          >
            <Popup>{event.event}</Popup>
          </Marker>
        ))}
      </MapContainer>
      {selectedEvent && (
        <div style={styles.detailsContainer}>
          <h2>{selectedEvent.event}</h2>
          <p><strong>Location:</strong> {selectedEvent.location}</p>
          <p><strong>Date:</strong> {selectedEvent['date-of-event']}</p>
          <p><strong>Description:</strong> {selectedEvent['event-picture-caption']}</p>
          {selectedEvent['event-picture-link'] && (
            <img
              src={selectedEvent['event-picture-link']}
              alt={selectedEvent['event-picture-caption']}
              style={styles.image}
            />
          )}
        </div>
      )}
    </div>
  );
}

// Inline styling for components
const styles = {
  container: {
    fontFamily: 'Arial, sans-serif',
    padding: '2em'
  },
  mapContainer: {
    height: '500px',
    width: '100%',
    marginBottom: '1em'
  },
  detailsContainer: {
    padding: '1em',
    borderTop: '1px solid #ccc',
    backgroundColor: '#f9f9f9'
  },
  image: {
    width: '100%',
    maxHeight: '300px',
    objectFit: 'cover',
    marginTop: '0.5em'
  }
};

export default App;
