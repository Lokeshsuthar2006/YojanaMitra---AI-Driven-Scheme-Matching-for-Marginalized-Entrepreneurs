import { useEffect, useState } from 'react';
import { Bot, LocateFixed, Route as RouteIcon } from 'lucide-react';
import { AnimatePresence } from 'framer-motion';
import PartnerMap from './PartnerMap';
import ExplanationPanel from './ExplanationPanel';
import './PartnerRouting.css';

const hasCoordinates = (latitude, longitude) => latitude !== null && latitude !== undefined && latitude !== '' && longitude !== null && longitude !== undefined && longitude !== '' && Number.isFinite(Number(latitude)) && Number.isFinite(Number(longitude));

function straightLineKm(start, end) {
  const radians = value => value * Math.PI / 180;
  const latitudeDelta = radians(end[0] - start[0]);
  const longitudeDelta = radians(end[1] - start[1]);
  const value = Math.sin(latitudeDelta / 2) ** 2 + Math.cos(radians(start[0])) * Math.cos(radians(end[0])) * Math.sin(longitudeDelta / 2) ** 2;
  return 6371 * 2 * Math.atan2(Math.sqrt(value), Math.sqrt(1 - value));
}

function formatDistance(meters) {
  const km = meters / 1000;
  return `${km < 10 ? km.toFixed(1) : Math.round(km)} km`;
}

function formatDuration(seconds) {
  const minutes = Math.max(1, Math.round(seconds / 60));
  return minutes < 60 ? `${minutes} min` : `${Math.floor(minutes / 60)} hr ${minutes % 60} min`;
}

export default function PartnerRouting({profile, partners, schemeName, schemeResult}) {
  const [selectedPartner, setSelectedPartner] = useState(null);
  const [showExplanation, setShowExplanation] = useState(false);
  const [userLocation, setUserLocation] = useState(() => hasCoordinates(profile.latitude, profile.longitude) ? [Number(profile.latitude), Number(profile.longitude)] : null);
  const [locationMessage, setLocationMessage] = useState('');
  const [route, setRoute] = useState(null);

  useEffect(() => {
    if (hasCoordinates(profile.latitude, profile.longitude)) {
      setUserLocation([Number(profile.latitude), Number(profile.longitude)]);
      return;
    }
    if (!navigator.geolocation) {
      setLocationMessage('Location is unavailable in this browser. Allow location access or enter it in the matching flow.');
      return;
    }
    navigator.geolocation.getCurrentPosition(
      position => {
        setUserLocation([position.coords.latitude, position.coords.longitude]);
        setLocationMessage('');
      },
      () => setLocationMessage('Location access was not provided. No route or ETA can be calculated without it.'),
      {enableHighAccuracy: false, timeout: 8000, maximumAge: 300000},
    );
  }, [profile.latitude, profile.longitude]);

  useEffect(() => {
    if (!selectedPartner) {
      setRoute(null);
      return;
    }
    if (!userLocation) {
      setRoute({status: 'location-needed'});
      return;
    }
    const partnerLocation = [Number(selectedPartner.latitude), Number(selectedPartner.longitude)];
    if (!partnerLocation.every(Number.isFinite)) {
      setRoute({status: 'partner-location-unavailable'});
      return;
    }

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 9000);
    let active = true;
    setRoute({status: 'loading'});
    const [userLatitude, userLongitude] = userLocation;
    const [partnerLatitude, partnerLongitude] = partnerLocation;
    fetch(`https://router.project-osrm.org/route/v1/driving/${userLongitude},${userLatitude};${partnerLongitude},${partnerLatitude}?overview=full&geometries=geojson`, {signal: controller.signal})
      .then(response => {
        if (!response.ok) throw new Error('Routing service unavailable');
        return response.json();
      })
      .then(data => {
        const result = data.code === 'Ok' && data.routes?.[0];
        if (!result || !Array.isArray(result.geometry?.coordinates) || !Number.isFinite(result.distance) || !Number.isFinite(result.duration)) {
          throw new Error('Invalid route response');
        }
        if (active) setRoute({status: 'road', distance: result.distance, duration: result.duration, coordinates: result.geometry.coordinates.map(([longitude, latitude]) => [latitude, longitude])});
      })
      .catch(() => {
        if (active) setRoute({status: 'straight-line', distance: straightLineKm(userLocation, partnerLocation) * 1000});
      });
    return () => {
      active = false;
      clearTimeout(timeout);
      controller.abort();
    };
  }, [selectedPartner, userLocation]);

  const selectPartner = partner => setSelectedPartner(partner);
  return <div className="partner-layout">
    <section className="surface partner-list">
      <h2>{schemeName} compatible partners</h2>
      <p>Demonstration partner records, filtered for this scheme. Route distance and ETA are requested when you select a partner.</p>
      <div className="partner-options">{partners.slice(0, 6).map(partner => {
        const selected = partner.partner_id === selectedPartner?.partner_id;
        return <article className={selected ? 'partner-option selected' : 'partner-option'} key={partner.partner_id}>
          <button type="button" className="partner-select" onClick={() => selectPartner(partner)} aria-pressed={selected}>
            <span className="partner-option-copy"><b>{partner.name}</b><span>{partner.type} · {partner.district}, {partner.state}</span><small>{partner.demo_status || 'DEMO DATA'} · Compatible with this scheme</small></span>
            <span className="partner-option-metrics">{selected && route?.status === 'road' ? formatDistance(route.distance) : partner.distance_km != null ? `~${Number(partner.distance_km).toFixed(1)} km` : 'Select for route'}<small>{selected && route?.status === 'road' ? formatDuration(route.duration) : partner.distance_km != null ? 'straight-line' : 'distance and ETA'}</small></span>
          </button>
          <button className="partner-route-button" type="button" onClick={() => selectPartner(partner)}><RouteIcon size={15}/> View Route</button>
        </article>;
      })}</div>
    </section>
    <section className="partner-map-panel">
      <PartnerMap profile={profile} partners={partners} selectedPartner={selectedPartner} userLocation={userLocation} route={route} onSelectPartner={selectPartner}/>
      <div className="route-information" aria-live="polite">
        {selectedPartner ? <>
          <div className="route-information-heading"><div><span className="eyebrow">Selected partner</span><h3>{selectedPartner.name}</h3></div><LocateFixed size={19}/></div>
          {route?.status === 'loading' && <p>Finding the road route…</p>}
          {route?.status === 'road' && <div className="route-metrics"><span><b>{formatDistance(route.distance)}</b><small>Road distance</small></span><span><b>{formatDuration(route.duration)}</b><small>Estimated travel time</small></span></div>}
          {route?.status === 'straight-line' && <p className="route-fallback">Road routing is unavailable. Straight-line distance: <b>{formatDistance(route.distance)}</b>. ETA unavailable.</p>}
          {route?.status === 'location-needed' && <p className="route-fallback">{locationMessage || 'Waiting for your location. Allow location access to calculate the route and ETA.'}</p>}
          {route?.status === 'partner-location-unavailable' && <p className="route-fallback">This demonstration record has no usable coordinates, so a route cannot be shown.</p>}
          {route?.status === 'road' && <p className="route-disclaimer">Estimated from OpenStreetMap routing; no live traffic or availability data.</p>}
          {schemeResult && <button className="route-explain-button" type="button" onClick={() => setShowExplanation(true)}><Bot size={16}/> Explain this recommendation</button>}
        </> : <p className="route-empty">Select a partner to see its location, road route, distance and estimated travel time.</p>}
      </div>
      <AnimatePresence>{showExplanation && schemeResult && <ExplanationPanel result={schemeResult} onClose={() => setShowExplanation(false)}/>}</AnimatePresence>
    </section>
  </div>;
}