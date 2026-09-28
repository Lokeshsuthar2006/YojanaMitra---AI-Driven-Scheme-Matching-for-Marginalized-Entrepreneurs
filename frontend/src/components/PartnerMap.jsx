import { MapContainer, Marker, Polyline, Popup, TileLayer, useMap } from 'react-leaflet';
import L from 'leaflet';
import { useEffect, useMemo } from 'react';

const userIcon = new L.DivIcon({className:'map-dot user-dot', html:'<span></span>', iconSize:[20,20], iconAnchor:[10,10]});
const partnerIcon = new L.DivIcon({className:'map-dot', html:'<span></span>', iconSize:[20,20], iconAnchor:[10,10]});
const selectedPartnerIcon = new L.DivIcon({className:'map-dot selected-partner-dot', html:'<span></span>', iconSize:[24,24], iconAnchor:[12,12]});
const hasLocation = partner => partner.latitude !== null && partner.latitude !== undefined && partner.longitude !== null && partner.longitude !== undefined && Number.isFinite(Number(partner.latitude)) && Number.isFinite(Number(partner.longitude));

function MapViewport({userLocation, selectedPartner}) {
  const map = useMap();
  useEffect(() => {
    if (userLocation && selectedPartner && hasLocation(selectedPartner)) {
      map.fitBounds([userLocation, [selectedPartner.latitude, selectedPartner.longitude]], {padding: [36, 36], maxZoom: 14});
    } else if (selectedPartner && hasLocation(selectedPartner)) {
      map.setView([selectedPartner.latitude, selectedPartner.longitude], 13);
    } else if (userLocation) {
      map.setView(userLocation, 11);
    }
  }, [map, userLocation, selectedPartner]);
  return null;
}

export default function PartnerMap({profile, partners, selectedPartner, userLocation, route, onSelectPartner}) {
  const center = useMemo(() =>
    userLocation || (selectedPartner && hasLocation(selectedPartner) ? [selectedPartner.latitude, selectedPartner.longitude] : [20.5937, 78.9629]),
    [userLocation, selectedPartner],
  );
  const routeLine = useMemo(() => route?.coordinates || [], [route]);

  return <MapContainer center={center} zoom={userLocation ? 8 : 5} className="map">
    <TileLayer attribution='&copy; OpenStreetMap contributors' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
    <MapViewport userLocation={userLocation} selectedPartner={selectedPartner}/>
    {userLocation && <Marker position={userLocation} icon={userIcon}><Popup>Your location</Popup></Marker>}
    {partners.filter(hasLocation).map(partner => {
      const position = [partner.latitude, partner.longitude];
      const selected = partner.partner_id === selectedPartner?.partner_id;
      return <Marker key={partner.partner_id} position={position} icon={selected ? selectedPartnerIcon : partnerIcon} eventHandlers={{click: () => onSelectPartner(partner)}}>
        <Popup><strong>{partner.name}</strong><br/>{partner.type} | Demonstration data</Popup>
      </Marker>;
    })}
    {routeLine.length > 0 && <Polyline positions={routeLine} pathOptions={{color:'#007d87', weight:5, opacity:0.85}}/>}
  </MapContainer>;
}