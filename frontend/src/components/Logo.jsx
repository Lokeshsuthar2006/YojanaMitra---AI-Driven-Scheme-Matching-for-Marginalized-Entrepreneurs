export default function Logo({ compact = false }) {
  return (
    <div className="logo" aria-label="Yojana Mitra home">
      <svg viewBox="0 0 64 64" role="img" aria-hidden="true">
        <defs>
          <linearGradient id="ymGrad1" x1="8" y1="8" x2="56" y2="56" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#00b4a6" />
            <stop offset="100%" stopColor="#006975" />
          </linearGradient>
          <linearGradient id="ymGrad2" x1="16" y1="14" x2="48" y2="46" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#22d3ee" />
            <stop offset="100%" stopColor="#00a7a0" />
          </linearGradient>
        </defs>
        {/* Protective circular boundary */}
        <circle cx="32" cy="32" r="28" stroke="url(#ymGrad1)" strokeWidth="3" strokeDasharray="145 25" strokeLinecap="round" fill="none" />
        
        {/* Mitra supportive foundation / helping embrace */}
        <path d="M16 38 C16 46, 26 50, 32 50 C38 50, 48 46, 48 38 C48 33, 42 31, 37 33 C33 34.5, 31 34.5, 27 33 C22 31, 16 33, 16 38 Z" fill="url(#ymGrad1)" fillOpacity="0.22" stroke="url(#ymGrad1)" strokeWidth="2.2" strokeLinejoin="round" />
        
        {/* Handshake / Partnership bridge arch */}
        <path d="M19 36 C22 28, 28 24, 32 24 C36 24, 42 28, 45 36" stroke="url(#ymGrad2)" strokeWidth="3.2" strokeLinecap="round" fill="none" />
        
        {/* Guiding scheme star of opportunity */}
        <path d="M32 11 L34.5 19.5 L42.5 21.5 L34.5 23.5 L32 31 L29.5 23.5 L21.5 21.5 L29.5 19.5 Z" fill="url(#ymGrad2)" />
        
        {/* Mitra partner nodes */}
        <circle cx="21" cy="27" r="2.2" fill="#00b4a6" />
        <circle cx="43" cy="27" r="2.2" fill="#00b4a6" />
      </svg>
      {!compact && <span>YOJANA <span>MITRA</span></span>}
    </div>
  );
}
